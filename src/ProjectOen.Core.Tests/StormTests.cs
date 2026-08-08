using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// docs/05: "Stormen læser lejrens tilstand." Udvælgelsen er deterministisk med
    /// vilje — stormen er udbetalingen på tre dages beslutninger, ikke et terningkast.
    /// </summary>
    public class StormTests
    {
        readonly ITestOutputHelper _out;
        public StormTests(ITestOutputHelper output) => _out = output;

        static ScenarioState Camp(int shelter, int fire, int signal, params string[] tags)
        {
            var s = new ScenarioState("SCN_STORMNATTEN_001", 1);
            s.Camp.ShelterIntegrity = shelter;
            s.Camp.FireStrength = fire;
            s.Camp.SignalProgress = signal;
            foreach (var t in tags) s.Tags.Add(t);
            return s;
        }

        static StormCatalog Catalog() => ScenarioLoader.Load(TestVector.LoadScenarioExample(), 1).Storm;

        /// <summary>En velspillet gennemgang skal stadig have en storm. Klimaks er ikke belønning for at fejle.</summary>
        [Fact]
        public void A_well_kept_camp_still_gets_a_storm()
        {
            var selected = StormResolver.Select(Camp(shelter: 90, fire: 80, signal: 40), Catalog());

            _out.WriteLine("velholdt lejr: " + string.Join(", ", selected.Select(s => s.Complication.Id)));
            Assert.NotEmpty(selected);
            Assert.All(selected, s => Assert.True(s.Complication.IsBaseline));
        }

        [Fact]
        public void A_weak_shelter_tears_the_roof()
        {
            var selected = StormResolver.Select(Camp(shelter: 20, fire: 80, signal: 10), Catalog());
            Assert.Contains(selected, s => s.Complication.Id == "STM_ROOF_TEAR_002");
        }

        /// <summary>Konsekvenskæden fra dag 1 skal nå helt frem til finalen.</summary>
        [Fact]
        public void Open_food_from_day_one_brings_the_animal_back_in_the_storm()
        {
            var withScent = StormResolver.Select(Camp(90, 80, 10, "SCENT_HIGH"), Catalog());
            var without = StormResolver.Select(Camp(90, 80, 10), Catalog());

            Assert.Contains(withScent, s => s.Complication.Id == "STM_ANIMAL_RETURN_004");
            Assert.DoesNotContain(without, s => s.Complication.Id == "STM_ANIMAL_RETURN_004");
        }

        /// <summary>At have gjort noget rigtigt skal kunne afværge en komplikation.</summary>
        [Fact]
        public void Securing_the_mast_prevents_the_mast_complication()
        {
            var exposed = StormResolver.Select(Camp(90, 80, signal: 80), Catalog());
            var secured = StormResolver.Select(Camp(90, 80, signal: 80, tags: "MAST_SECURED"), Catalog());

            Assert.Contains(exposed, s => s.Complication.Id == "STM_SIGNAL_MAST_005");
            Assert.DoesNotContain(secured, s => s.Complication.Id == "STM_SIGNAL_MAST_005");
        }

        /// <summary>Uden loft giver en dårlig gennemgang en uspillelig ophobning i et 12-16 min vindue.</summary>
        [Fact]
        public void The_worst_case_is_capped_and_keeps_the_most_severe()
        {
            var catalog = Catalog();
            var disaster = Camp(shelter: 5, fire: 5, signal: 90, tags: "SCENT_HIGH");

            var selected = StormResolver.Select(disaster, catalog);
            _out.WriteLine("katastrofe: " + string.Join(", ",
                selected.Select(s => $"{s.Complication.Id}(sev {s.Complication.Severity})")));

            Assert.Equal(catalog.MaxSimultaneous, selected.Count);
            Assert.Equal(5, selected[0].Complication.Severity);
            Assert.True(selected.Zip(selected.Skip(1), (a, b) => a.Complication.Severity >= b.Complication.Severity).All(x => x));

            // Den optjente konsekvens må ikke være skåret væk til fordel for generiske katastrofer.
            Assert.Contains(selected, s => s.Complication.RequiredTags.Contains("SCENT_HIGH"));
        }

        /// <summary>En komplikation uden forklaring er ren straf.</summary>
        [Fact]
        public void Every_complication_carries_the_reason_it_fired()
        {
            var selected = StormResolver.Select(Camp(20, 10, 80, "SCENT_HIGH"), Catalog());
            foreach (var s in selected)
                _out.WriteLine($"{s.Complication.Id} <- {s.Reason}");

            Assert.All(selected, s => Assert.False(string.IsNullOrWhiteSpace(s.Reason)));
            Assert.Contains(selected, s => s.Reason.Contains("shelterIntegrity"));
            Assert.Contains(selected, s => s.Reason.Contains("SCENT_HIGH"));
        }

        /// <summary>Samme lejr skal give samme storm. Ellers er tre dages beslutninger ligegyldige.</summary>
        [Fact]
        public void The_same_camp_always_produces_the_same_storm()
        {
            var catalog = Catalog();
            var first = StormResolver.Select(Camp(30, 20, 70, "SCENT_HIGH"), catalog).Select(s => s.Complication.Id);
            for (var i = 0; i < 5; i++)
                Assert.Equal(first, StormResolver.Select(Camp(30, 20, 70, "SCENT_HIGH"), catalog).Select(s => s.Complication.Id));
        }

        [Fact]
        public void A_catalog_without_a_baseline_fails_validation()
        {
            var catalog = new StormCatalog();
            catalog.Add(new StormComplication("STM_ONLY_ON_FAILURE_001", 3,
                new ActionEffect(campDeltas: new System.Collections.Generic.Dictionary<string, int> { ["fireStrength"] = -10 }),
                campConditions: new[] { new CampCondition("fireStrength", CampComparison.AtMost, 20) }));

            Assert.Contains(catalog.Validate(), p => p.Contains("baseline"));
        }

        [Fact]
        public void An_unexplainable_complication_fails_validation()
        {
            var catalog = new StormCatalog();
            catalog.Add(new StormComplication("STM_BASE_001", 1,
                new ActionEffect(fatigueCost: 5), isBaseline: true));
            catalog.Add(new StormComplication("STM_MYSTERY_002", 3, new ActionEffect(fatigueCost: 5)));

            Assert.Contains(catalog.Validate(), p => p.Contains("kan ikke forklares"));
        }

        [Fact]
        public void The_repository_storm_catalog_validates_clean()
        {
            Assert.Empty(Catalog().Validate());
        }

        /// <summary>Komplikationerne skal kunne anvendes på lejren gennem det eksisterende effektsystem.</summary>
        [Fact]
        public void Complications_apply_through_the_normal_effect_pipeline()
        {
            var state = Camp(shelter: 20, fire: 80, signal: 10);
            var before = state.Camp.ShelterIntegrity;

            foreach (var s in StormResolver.Select(state, Catalog()))
                EffectApplier.Apply(state, s.Complication.Effect, new[] { 0, 1 });

            Assert.True(state.Camp.ShelterIntegrity < before);
            Assert.Contains("ROOF_OPEN", state.Tags);
        }
    }
}
