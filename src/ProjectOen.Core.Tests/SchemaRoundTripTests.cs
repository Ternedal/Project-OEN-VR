using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ProjectOen.Core.Persistence;
using ProjectOen.Core.Scenario;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// Eksempelfilerne i <c>examples/</c> er kontrakten mellem skemaerne, Core og alt
    /// data, der senere skrives i hånden. Python-valideringen tjekker dem mod JSON-skemaerne;
    /// disse tests tjekker den anden halvdel: at Core kan læse dem, skrive dem tilbage, og
    /// at intet forsvinder undervejs.
    ///
    /// Hvorfor det er værd at teste: den kanoniske serialisering er grundlaget for
    /// save-checksummen. Taber den en nøgle, ændrer den talformat eller sorterer den
    /// ustabilt, så ændrer checksummen sig uden at data gør — og en gyldig save afvises
    /// som korrupt. Det ville vise sig som en tilfældig fejl hos spilleren, ikke som en
    /// compilefejl.
    /// </summary>
    public class SchemaRoundTripTests
    {
        readonly ITestOutputHelper _out;
        public SchemaRoundTripTests(ITestOutputHelper output) => _out = output;

        public static IEnumerable<object[]> ExampleFiles()
        {
            var dir = Path.Combine(TestVector.RepoRoot, "examples");
            foreach (var path in Directory.GetFiles(dir, "*.json").OrderBy(p => p))
                yield return new object[] { Path.GetFileName(path) };
        }

        /// <summary>
        /// Kanonisk serialisering skal være et fikspunkt: at serialisere en allerede
        /// serialiseret struktur må give præcis samme streng. Er den ikke idempotent,
        /// er den ubrugelig som checksum-grundlag.
        /// </summary>
        [Theory]
        [MemberData(nameof(ExampleFiles))]
        public void Canonical_serialisation_is_stable_for(string fileName)
        {
            var original = TestVector.LoadExample(fileName);

            var first = CanonicalJson.Serialize(original);
            var reparsed = TestVector.ParseJsonObject(first);
            var second = CanonicalJson.Serialize(reparsed);

            _out.WriteLine($"{fileName}: {first.Length} tegn kanonisk");
            Assert.Equal(first, second);
        }

        /// <summary>
        /// En roundtrip må ikke tabe felter. Sammenligningen er på nøglestier, ikke på
        /// tekst, så en ren formateringsforskel ikke kan skjule et manglende felt.
        /// </summary>
        [Theory]
        [MemberData(nameof(ExampleFiles))]
        public void Round_trip_preserves_every_key_in(string fileName)
        {
            var original = TestVector.LoadExample(fileName);
            var roundTripped = TestVector.ParseJsonObject(CanonicalJson.Serialize(original));

            var before = new SortedSet<string>();
            var after = new SortedSet<string>();
            CollectPaths(original, "", before);
            CollectPaths(roundTripped, "", after);

            var lost = before.Except(after).ToList();
            var gained = after.Except(before).ToList();

            _out.WriteLine($"{fileName}: {before.Count} nøglestier");
            Assert.True(lost.Count == 0, $"{fileName} tabte felter: {string.Join(", ", lost.Take(10))}");
            Assert.True(gained.Count == 0, $"{fileName} fik felter: {string.Join(", ", gained.Take(10))}");
        }

        /// <summary>
        /// Den konkrete konsekvens, kæden findes for: checksummen skal overleve en
        /// roundtrip. Gør den ikke det, kan en gyldig save ikke indlæses igen.
        /// </summary>
        [Fact]
        public void Savegame_checksum_survives_a_round_trip()
        {
            var save = TestVector.LoadSavegameExample();
            Assert.True(SaveChecksum.Verify(save), "eksempel-saven verificerer ikke som den ligger");

            var expected = SaveChecksum.Compute(save);
            var roundTripped = TestVector.ParseJsonObject(CanonicalJson.Serialize(save));

            _out.WriteLine($"checksum: {expected}");
            Assert.Equal(expected, SaveChecksum.Compute(roundTripped));
            Assert.True(SaveChecksum.Verify(roundTripped), "saven verificerer ikke efter roundtrip");
        }

        /// <summary>
        /// Scenariet skal kunne indlæses fra sin egen roundtrip. Det binder loaderen til
        /// serialiseringen: en ændring i den ene, der brækker den anden, fanges her.
        /// </summary>
        [Fact]
        public void Scenario_still_loads_after_a_round_trip()
        {
            var raw = TestVector.LoadScenarioExample();
            var direct = ScenarioLoader.Load(raw, 1);

            var roundTripped = TestVector.ParseJsonObject(CanonicalJson.Serialize(raw));
            var reloaded = ScenarioLoader.Load(roundTripped, 1);

            _out.WriteLine($"{reloaded.Id}: {reloaded.Actions.Count} handlinger");
            Assert.Equal(direct.Id, reloaded.Id);
            Assert.Equal(direct.Actions.Count, reloaded.Actions.Count);
            Assert.Equal(direct.WinRules.Count, reloaded.WinRules.Count);
            Assert.Equal(direct.LoseRules.Count, reloaded.LoseRules.Count);
            Assert.Empty(reloaded.Effects.Validate());
        }

        static void CollectPaths(object? node, string path, ISet<string> into)
        {
            switch (node)
            {
                case IDictionary<string, object?> map:
                    foreach (var pair in map)
                    {
                        var child = path + "/" + pair.Key;
                        into.Add(child);
                        CollectPaths(pair.Value, child, into);
                    }
                    break;
                case string:
                    break;
                case IEnumerable list:
                    var index = 0;
                    foreach (var item in list)
                    {
                        CollectPaths(item, path + "[" + index + "]", into);
                        index++;
                    }
                    break;
            }
        }
    }
}
