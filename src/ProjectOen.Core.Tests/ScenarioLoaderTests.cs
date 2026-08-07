using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// Loaderen er bindeleddet: fem data-drevne systemer var bygget, men der fandtes
    /// ingen vej fra JSON til et kørende scenario. Uden den er "data-drevet" en påstand.
    /// </summary>
    public class ScenarioLoaderTests
    {
        readonly ITestOutputHelper _out;
        public ScenarioLoaderTests(ITestOutputHelper output) => _out = output;

        const int Protocol = 1;

        [Fact]
        public void The_repository_scenario_loads_and_is_internally_complete()
        {
            var def = ScenarioLoader.Load(TestVector.LoadScenarioExample(), Protocol);

            _out.WriteLine($"{def.Id} | protokol {def.SupportedBuildProtocol} | " +
                           $"{def.Actions.Count} handlinger | {def.WinRules.Count} win / {def.LoseRules.Count} lose");

            Assert.Equal("SCN_STORMNATTEN_001", def.Id);
            Assert.NotEmpty(def.Actions);
            Assert.Empty(def.Effects.Validate());
            Assert.NotEmpty(def.WinRules);
            Assert.NotEmpty(def.LoseRules);
        }

        /// <summary>
        /// Et scenario der starter halvt indlæst, fejler først midt i en session.
        /// Derfor samles alle problemer, og hele indlæsningen afvises.
        /// </summary>
        [Fact]
        public void A_missing_fail_forward_effect_stops_the_whole_load()
        {
            var json = TestVector.LoadScenarioExample();
            var effects = (IDictionary<string, object?>)json["effects"]!;
            var first = (IDictionary<string, object?>)effects.Values.First()!;
            first.Remove("failForward");

            var ex = Assert.Throws<ScenarioLoadException>(() => ScenarioLoader.Load(json, Protocol));
            Assert.Contains(ex.Problems, p => p.Contains("FailForward"));
        }

        [Fact]
        public void An_empty_effect_is_rejected_at_load_time()
        {
            var json = TestVector.LoadScenarioExample();
            var effects = (IDictionary<string, object?>)json["effects"]!;
            var first = (IDictionary<string, object?>)effects.Values.First()!;
            first["failForward"] = new Dictionary<string, object?>();

            var ex = Assert.Throws<ScenarioLoadException>(() => ScenarioLoader.Load(json, Protocol));
            Assert.Contains(ex.Problems, p => p.Contains("tom effekt"));
        }

        [Fact]
        public void Effects_for_an_action_that_does_not_exist_are_caught()
        {
            var json = TestVector.LoadScenarioExample();
            var effects = (IDictionary<string, object?>)json["effects"]!;
            var template = effects.Values.First();
            effects["INT_GHOST_ACTION_999"] = template;

            var ex = Assert.Throws<ScenarioLoadException>(() => ScenarioLoader.Load(json, Protocol));
            Assert.Contains(ex.Problems, p => p.Contains("findes ikke i actionCatalog"));
        }

        [Fact]
        public void An_action_without_any_effects_is_caught()
        {
            var json = TestVector.LoadScenarioExample();
            var effects = (IDictionary<string, object?>)json["effects"]!;
            effects.Remove(effects.Keys.First());

            var ex = Assert.Throws<ScenarioLoadException>(() => ScenarioLoader.Load(json, Protocol));
            Assert.Contains(ex.Problems, p => p.Contains("mangler helt"));
        }

        [Fact]
        public void Thresholds_must_be_increasing()
        {
            var json = TestVector.LoadScenarioExample();
            json["outcomeThresholds"] = new Dictionary<string, object?>
            {
                ["partial"] = 0.8, ["success"] = 0.5, ["critical"] = 0.6
            };

            var ex = Assert.Throws<ScenarioLoadException>(() => ScenarioLoader.Load(json, Protocol));
            Assert.Contains(ex.Problems, p => p.Contains("stigende"));
        }

        [Fact]
        public void A_protocol_mismatch_stops_the_load()
        {
            var ex = Assert.Throws<ScenarioLoadException>(
                () => ScenarioLoader.Load(TestVector.LoadScenarioExample(), Protocol + 5));
            Assert.Contains(ex.Problems, p => p.Contains("PROTOCOL_MISMATCH"));
        }

        [Fact]
        public void All_problems_are_reported_at_once_rather_than_one_per_run()
        {
            var json = TestVector.LoadScenarioExample();
            var effects = (IDictionary<string, object?>)json["effects"]!;
            ((IDictionary<string, object?>)effects.Values.First()!).Remove("failForward");
            ((List<object?>)json["loseRules"]!).Add(new Dictionary<string, object?> { ["type"] = "everyoneGetsIceCream" });

            var ex = Assert.Throws<ScenarioLoadException>(() => ScenarioLoader.Load(json, Protocol + 5));
            _out.WriteLine(string.Join("\n", ex.Problems));
            Assert.True(ex.Problems.Count >= 3, "Loaderen skal samle alle problemer, ikke stoppe ved det første.");
        }

        /// <summary>Dag 2's overbelastning: to handlinger låses op af en hændelse frem for at ligge klar fra morgenstunden.</summary>
        [Fact]
        public void An_action_gated_behind_an_event_is_unavailable_until_it_fires()
        {
            var def = ScenarioLoader.Load(TestVector.LoadScenarioExample(), Protocol);
            var gated = def.Actions.Values.Where(a => a.UnlockedBy.Count > 0).ToList();

            Assert.NotEmpty(gated);
            foreach (var action in gated)
            {
                Assert.False(action.IsAvailable(new string[0]));
                Assert.True(action.IsAvailable(action.UnlockedBy.ToArray()));
            }
        }

        /// <summary>Loaderen skal producere noget, direktoren faktisk kan køre på.</summary>
        [Fact]
        public void The_loaded_definition_drives_a_director_end_to_end()
        {
            var def = ScenarioLoader.Load(TestVector.LoadScenarioExample(), Protocol);
            var state = new ScenarioState(def.Id, 99);
            var d = new ScenarioDirector(state, def.CreateResolver(), def.Effects);

            var action = def.Actions.Values.First(a => a.UnlockedBy.Count == 0).Id;

            d.Submit(new AdvancePhaseCommand("p0", 0));
            d.Submit(new AdvancePhaseCommand("p1", 0));
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, action, 2));
            d.Submit(new ConfirmPlanCommand("c1", 0));
            d.Submit(new AdvancePhaseCommand("p2", 0));
            d.Submit(new AdvancePhaseCommand("p3", 0));

            var produced = d.Submit(new CompleteInteractionStepCommand("s1", 0, action,
                new ExecutionSample(0.9, 0.9)));

            Assert.Single(produced.OfType<ActionResolved>());
            Assert.NotEmpty(produced.OfType<ResourceChanged>());
        }
    }
}
