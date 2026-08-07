using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using ProjectOen.Core.Persistence;
using ProjectOen.Core.Scenario;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// PR 5 i docs/20: "Save/state skeleton - ScenarioDirector, snapshot/checksum,
    /// disconnect pause." Det er her reconnect og retry står og falder.
    /// </summary>
    public class ScenarioSnapshotTests
    {
        readonly ITestOutputHelper _out;
        public ScenarioSnapshotTests(ITestOutputHelper output) => _out = output;

        static ScenarioDirector PlayToNightOne()
        {
            var d = new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 4242));
            d.Submit(new AdvancePhaseCommand("p0", 0));   // Intro -> Dawn
            d.Submit(new AdvancePhaseCommand("p1", 0));   // Dawn  -> Planning
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_GATHER_WOOD_001", 2));
            d.Submit(new PlaceEffortMarkerCommand("m2", 1, "INT_BUILD_SHELTER_003", 2));
            d.Submit(new ConfirmPlanCommand("c1", 0));
            d.AddTag("SCENT_HIGH", "lod maden stå åben");
            d.Submit(new ScheduleDelayedEventCommand("s1", 0, "EVT_ANIMAL_AT_CAMP_002",
                2, ScenarioPhase.Night, "SCENT_HIGH"));
            d.State.Camp.ShelterIntegrity = 41;
            d.State.Camp.FireStrength = 63;
            d.State.Resources["wood"] = 3;
            d.State.Players[1].AddInjury("HAND_CUT");
            d.State.Players[1].Health = 78;
            return d;
        }

        static IDictionary<string, object?> RoundTripThroughDisk(IDictionary<string, object?> save, out bool fromBackup)
        {
            var dir = Path.Combine(Path.GetTempPath(), "oen-" + Path.GetRandomFileName());
            Directory.CreateDirectory(dir);
            try
            {
                var path = Path.Combine(dir, "checkpoint.json");
                new AtomicSaveWriter().Write(path, save);
                var result = new AtomicSaveWriter().Load(path, Parse);
                fromBackup = result.FromBackup;
                Assert.True(result.Ok);
                return result.Save!;
            }
            finally { Directory.Delete(dir, true); }
        }

        static IDictionary<string, object?> Parse(string json)
        {
            using var doc = JsonDocument.Parse(json);
            return (IDictionary<string, object?>)Convert(doc.RootElement)!;
        }

        static object? Convert(JsonElement e)
        {
            switch (e.ValueKind)
            {
                case JsonValueKind.Object:
                    var m = new Dictionary<string, object?>();
                    foreach (var p in e.EnumerateObject()) m[p.Name] = Convert(p.Value);
                    return m;
                case JsonValueKind.Array: return e.EnumerateArray().Select(Convert).ToList();
                case JsonValueKind.String: return e.GetString();
                case JsonValueKind.True: return true;
                case JsonValueKind.False: return false;
                case JsonValueKind.Null: return null;
                default: return e.TryGetInt64(out var l) ? l : (object)e.GetDouble();
            }
        }

        [Fact]
        public void Full_state_survives_a_round_trip_through_disk()
        {
            var d = PlayToNightOne();
            var save = ScenarioSnapshot.Capture(d.State, 1, "stormnatten-1.0", 1, "DAY1_NIGHT");

            var reloaded = RoundTripThroughDisk(save, out _);
            var restored = ScenarioSnapshot.Restore(reloaded);

            Assert.Equal(d.State.ScenarioId, restored.ScenarioId);
            Assert.Equal(d.State.Seed, restored.Seed);
            Assert.Equal(d.State.Phase, restored.Phase);
            Assert.Equal(d.State.Day, restored.Day);
            Assert.Equal(d.State.Revision, restored.Revision);
            Assert.Equal(d.State.PlanLocked, restored.PlanLocked);
            Assert.Equal(41, restored.Camp.ShelterIntegrity);
            Assert.Equal(63, restored.Camp.FireStrength);
            Assert.Equal(3, restored.Resources["wood"]);
            Assert.Equal(78, restored.Players[1].Health);
            Assert.Contains("HAND_CUT", restored.Players[1].Injuries);
            Assert.Contains("SCENT_HIGH", restored.Tags);
            Assert.Equal(d.State.Plan.Count, restored.Plan.Count);
            Assert.Single(restored.EventQueue);
        }

        /// <summary>
        /// SAVE-001, hele vejen igennem: planlæg → checkpoint → skriv → indlæs →
        /// genoptag. Eventet skal udløses præcis én gang.
        /// </summary>
        [Fact]
        public void Resume_from_a_written_checkpoint_fires_the_delayed_event_exactly_once()
        {
            var original = PlayToNightOne();
            var save = ScenarioSnapshot.Capture(original.State, 1, "stormnatten-1.0", 1, "DAY1_NIGHT");
            var restored = ScenarioSnapshot.Restore(RoundTripThroughDisk(save, out _));

            var resumed = new ScenarioDirector(restored);
            var guard = 0;
            while (!(resumed.State.Phase == ScenarioPhase.Night && resumed.State.Day == 2) && guard++ < 40)
                resumed.Submit(new AdvancePhaseCommand($"r{guard}", 0));

            Assert.Single(resumed.Journal.OfType<DelayedEventTriggered>());

            // Endnu et resume fra SAMME checkpoint må heller ikke fyre to gange i alt.
            var secondResume = new ScenarioDirector(ScenarioSnapshot.Restore(save));
            guard = 0;
            while (!(secondResume.State.Phase == ScenarioPhase.Night && secondResume.State.Day == 2) && guard++ < 40)
                secondResume.Submit(new AdvancePhaseCommand($"q{guard}", 0));
            Assert.Single(secondResume.Journal.OfType<DelayedEventTriggered>());
        }

        /// <summary>Efter resume må en gentaget command fra før checkpointet ikke tælle igen.</summary>
        [Fact]
        public void Commands_handled_before_the_checkpoint_stay_handled_after_resume()
        {
            var original = PlayToNightOne();
            var save = ScenarioSnapshot.Capture(original.State, 1, "stormnatten-1.0", 1, "DAY1_NIGHT");
            var resumed = new ScenarioDirector(ScenarioSnapshot.Restore(save));

            var replay = resumed.Submit(new ScheduleDelayedEventCommand("s1", 0, "EVT_ANIMAL_AT_CAMP_002",
                2, ScenarioPhase.Night, "SCENT_HIGH"));

            Assert.Empty(replay);
            Assert.Single(resumed.State.EventQueue);
        }

        /// <summary>
        /// Snapshottet skrives af spillet og valideres af tooling. Afviger feltsættet fra
        /// skemaet, ville CI og runtime være uenige om, hvad en gyldig save er.
        /// Testen læser det faktiske skema frem for en kopi af det.
        /// </summary>
        [Fact]
        public void The_snapshot_stays_within_the_fields_the_schema_allows()
        {
            var schemaPath = Path.Combine(TestVector.RepoRoot, "schemas", "savegame.schema.json");
            using var schema = JsonDocument.Parse(File.ReadAllText(schemaPath));
            var allowed = schema.RootElement.GetProperty("properties").EnumerateObject().Select(p => p.Name).ToHashSet();
            var required = schema.RootElement.GetProperty("required").EnumerateArray().Select(e => e.GetString()!).ToList();

            var save = ScenarioSnapshot.Capture(PlayToNightOne().State, 1, "stormnatten-1.0", 1, "DAY1_NIGHT");

            var extras = save.Keys.Where(k => !allowed.Contains(k)).ToList();
            _out.WriteLine($"felter i snapshot: {save.Count} | tilladt af skema: {allowed.Count}");
            Assert.True(extras.Count == 0, "Felter uden for skemaet (additionalProperties er false): " + string.Join(", ", extras));

            var missing = required.Where(r => !save.ContainsKey(r)).ToList();
            Assert.True(missing.Count == 0, "Manglende påkrævede felter: " + string.Join(", ", missing));
        }

        [Fact]
        public void A_tampered_snapshot_is_rejected_instead_of_loaded()
        {
            var save = ScenarioSnapshot.Capture(PlayToNightOne().State, 1, "stormnatten-1.0", 1, "DAY1_NIGHT");
            save["revision"] = 9999L;
            Assert.Throws<System.InvalidOperationException>(() => ScenarioSnapshot.Restore(save));
        }

        [Fact]
        public void A_future_schema_version_is_refused_with_a_clear_message()
        {
            var save = ScenarioSnapshot.Capture(PlayToNightOne().State, 1, "stormnatten-1.0", 1, "DAY1_NIGHT");
            save["schemaVersion"] = 99L;
            SaveChecksum.Stamp(save);

            var ex = Assert.Throws<System.InvalidOperationException>(() => ScenarioSnapshot.Restore(save));
            Assert.Contains("Migrator", ex.Message);
        }
    }
}
