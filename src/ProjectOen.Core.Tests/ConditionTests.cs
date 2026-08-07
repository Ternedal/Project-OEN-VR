using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// docs/07 §7: "Klienten sender intents, ikke færdige resultater."
    ///
    /// Modstanden i udfaldsformlen udledes derfor af autoritativ state. Kom den fra
    /// klienten, ville en klient kunne fortælle serveren, hvor hårdt den skulle straffes
    /// — og en fejl i én klients måling ville forplante sig til det delte resultat.
    /// </summary>
    public class ConditionTests
    {
        readonly ITestOutputHelper _out;
        public ConditionTests(ITestOutputHelper output) => _out = output;

        static ConditionTable Table() 
        {
            var t = new ConditionTable { MaxFatiguePenalty = 0.20 };
            t.Add(new InjuryDefinition("HAND_CUT", 0.12, healedBy: new[] { "INT_TREAT_INJURY_011" }));
            t.Add(new InjuryDefinition("SPRAINED_ANKLE", 0.18,
                blocksActions: new[] { "INT_EXPLORE_CLIFF_004" },
                healedBy: new[] { "INT_TREAT_INJURY_011" }));
            return t;
        }

        static ScenarioDirector AtActionSequence(ConditionTable conditions, out ScenarioState state, string action = "INT_GATHER_WOOD_001")
        {
            state = new ScenarioState("SCN_STORMNATTEN_001", 3);
            var d = new ScenarioDirector(state, null, null, conditions);
            d.Submit(new AdvancePhaseCommand("p0", 0));
            d.Submit(new AdvancePhaseCommand("p1", 0));
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, action, 2));
            d.Submit(new ConfirmPlanCommand("c1", 0));
            d.Submit(new AdvancePhaseCommand("p2", 0));
            d.Submit(new AdvancePhaseCommand("p3", 0));
            return d;
        }

        [Fact]
        public void Injuries_and_fatigue_add_to_the_penalty()
        {
            var conditions = Table();
            var state = new ScenarioState("SCN_STORMNATTEN_001", 1);
            Assert.Equal(0, ConditionModel.PenaltyFor(state, conditions), 3);

            state.Players[0].AddInjury("HAND_CUT");
            Assert.Equal(0.12, ConditionModel.PenaltyFor(state, conditions), 3);

            state.Players[1].Fatigue = 50;   // gennemsnit 25 -> 0,25 * 0,20 = 0,05
            Assert.Equal(0.17, ConditionModel.PenaltyFor(state, conditions), 3);
        }

        /// <summary>Træthed blev talt op af effekterne, men læst af ingenting. Nu tæller den.</summary>
        [Fact]
        public void Fatigue_alone_measurably_worsens_the_outcome()
        {
            var conditions = Table();
            var rested = AtActionSequence(conditions, out var restedState);
            var tired = AtActionSequence(conditions, out var tiredState);
            tiredState.Players[0].Fatigue = 100;
            tiredState.Players[1].Fatigue = 100;

            var sample = new ExecutionSample(0.75, 0.75);
            var a = rested.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_GATHER_WOOD_001", sample))
                          .OfType<ActionResolved>().Single();
            var b = tired.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_GATHER_WOOD_001", sample))
                         .OfType<ActionResolved>().Single();

            _out.WriteLine($"udhvilet {a.Score:0.000} ({a.Tier}) | udmattet {b.Score:0.000} ({b.Tier})");
            Assert.True(b.Score < a.Score);
        }

        [Fact]
        public void An_injury_can_block_an_action_entirely()
        {
            var conditions = Table();
            var d = AtActionSequence(conditions, out var state, "INT_EXPLORE_CLIFF_004");
            state.Players[1].AddInjury("SPRAINED_ANKLE");

            var produced = d.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_EXPLORE_CLIFF_004",
                new ExecutionSample(1, 1)));

            Assert.Contains(produced.OfType<CommandRejected>(), r => r.Code == "BLOCKED_BY_INJURY");
            Assert.Empty(produced.OfType<ActionResolved>());
        }

        [Fact]
        public void Treating_an_injury_removes_it()
        {
            var conditions = Table();
            var d = AtActionSequence(conditions, out var state, "INT_TREAT_INJURY_011");
            state.Players[1].AddInjury("HAND_CUT");

            var produced = d.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_TREAT_INJURY_011",
                new ExecutionSample(0.9, 0.9)));

            Assert.Contains(produced.OfType<InjuryHealed>(), h => h.InjuryId == "HAND_CUT");
            Assert.Empty(state.Players[1].Injuries);
        }

        /// <summary>Preparation kommer fra planen. Klienten kan ikke opfinde den.</summary>
        [Fact]
        public void Preparation_is_derived_from_the_markers_actually_placed()
        {
            var state = new ScenarioState("SCN_STORMNATTEN_001", 1);
            Assert.Equal(0, ConditionModel.PreparationFor(state, "INT_A_001", 1), 3);

            state.Plan["INT_A_001"] = 1;
            Assert.Equal(1.0, ConditionModel.PreparationFor(state, "INT_A_001", 1), 3);
            Assert.Equal(0.5, ConditionModel.PreparationFor(state, "INT_A_001", 2), 3);

            state.Plan["INT_A_001"] = 2;
            Assert.Equal(1.0, ConditionModel.PreparationFor(state, "INT_A_001", 2), 3);
        }

        /// <summary>En skade uden vej ud er permanent — det er en content-fejl, ikke svær balancering.</summary>
        [Fact]
        public void An_injury_without_a_cure_is_a_content_error()
        {
            var t = new ConditionTable();
            t.Add(new InjuryDefinition("CURSED_KNEE", 0.2));
            Assert.Contains(t.Validate(), p => p.Contains("healedBy"));
        }

        [Fact]
        public void A_penalty_contribution_outside_zero_to_one_is_caught()
        {
            var t = new ConditionTable();
            t.Add(new InjuryDefinition("DOOM", 4.0, healedBy: new[] { "INT_TREAT_INJURY_011" }));
            Assert.Contains(t.Validate(), p => p.Contains("mellem 0 og 1"));
        }

        [Fact]
        public void The_repository_scenario_loads_its_conditions()
        {
            var def = ScenarioLoader.Load(TestVector.LoadScenarioExample(), 1);
            Assert.NotEmpty(def.Conditions.All);
            Assert.Empty(def.Conditions.Validate());
        }

        [Fact]
        public void An_injury_referring_to_an_unknown_action_stops_the_load()
        {
            var json = TestVector.LoadScenarioExample();
            var conditions = (IDictionary<string, object?>)json["conditions"]!;
            var injuries = (List<object?>)conditions["injuries"]!;
            ((IDictionary<string, object?>)injuries[0]!)["healedBy"] = new List<object?> { "INT_NOT_A_THING_999" };

            var ex = Assert.Throws<ScenarioLoadException>(() => ScenarioLoader.Load(json, 1));
            Assert.Contains(ex.Problems, p => p.Contains("healedBy peger paa ukendt handling"));
        }
    }
}
