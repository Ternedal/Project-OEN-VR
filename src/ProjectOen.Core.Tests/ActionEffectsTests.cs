using System;
using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;

namespace ProjectOen.Core.Tests
{
    public class ActionEffectsTests
    {
        static ActionEffect Effect(int wood = 0, int shelter = 0, string? addTag = null, int fatigue = 0) =>
            new ActionEffect(
                resourceDeltas: wood != 0 ? new Dictionary<string, int> { ["wood"] = wood } : null,
                campDeltas: shelter != 0 ? new Dictionary<string, int> { ["shelterIntegrity"] = shelter } : null,
                addTags: addTag != null ? new[] { addTag } : null,
                fatigueCost: fatigue);

        static EffectTable FullTableFor(string actionId)
        {
            var table = new EffectTable();
            table.Set(actionId, OutcomeTier.CriticalSuccess, Effect(wood: 5, shelter: 15, fatigue: 5));
            table.Set(actionId, OutcomeTier.Success, Effect(wood: 3, shelter: 10, fatigue: 8));
            table.Set(actionId, OutcomeTier.PartialWithCost, Effect(wood: 1, shelter: 3, fatigue: 15));
            // Selv et mislykket forsøg flytter noget. Aldrig "ingen effekt".
            table.Set(actionId, OutcomeTier.FailForward, Effect(wood: 1, addTag: "TOOL_DAMAGED", fatigue: 20));
            return table;
        }

        static ScenarioDirector AtActionSequence(EffectTable table)
        {
            var d = new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 9), null, table);
            d.Submit(new AdvancePhaseCommand("p0", 0));
            d.Submit(new AdvancePhaseCommand("p1", 0));
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_GATHER_WOOD_001", 2));
            d.Submit(new ConfirmPlanCommand("c1", 0));
            d.Submit(new AdvancePhaseCommand("p2", 0));
            d.Submit(new AdvancePhaseCommand("p3", 0));
            Assert.Equal(ScenarioPhase.ActionSequence, d.State.Phase);
            return d;
        }

        [Fact]
        public void A_strong_outcome_moves_resources_and_camp_state()
        {
            var d = AtActionSequence(FullTableFor("INT_GATHER_WOOD_001"));
            var produced = d.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_GATHER_WOOD_001",
                new ExecutionSample(1, 1)));

            Assert.Equal(OutcomeTier.CriticalSuccess, produced.OfType<ActionResolved>().Single().Tier);
            Assert.Equal(5, d.State.Resources["wood"]);
            Assert.Equal(15, d.State.Camp.ShelterIntegrity);
            Assert.Contains(produced.OfType<ResourceChanged>(), e => e.Key == "wood" && e.Delta == 5);
        }

        /// <summary>docs/04 §9: fejl med fremdrift. Et mislykket forsøg efterlader stadig spor.</summary>
        [Fact]
        public void A_failed_attempt_still_changes_the_world()
        {
            var d = AtActionSequence(FullTableFor("INT_GATHER_WOOD_001"));
            var produced = d.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_GATHER_WOOD_001",
                new ExecutionSample(0.05, 0.05)));

            Assert.Equal(OutcomeTier.FailForward, produced.OfType<ActionResolved>().Single().Tier);
            Assert.Equal(1, d.State.Resources["wood"]);
            Assert.Contains("TOOL_DAMAGED", d.State.Tags);
        }

        /// <summary>
        /// Tagget fra et mislykket forsøg skal kunne forklares bagefter. Uden proveniens
        /// bliver efterspilsrapporten til en liste over ting, der bare skete.
        /// </summary>
        [Fact]
        public void A_tag_added_by_an_effect_records_which_action_caused_it()
        {
            var d = AtActionSequence(FullTableFor("INT_GATHER_WOOD_001"));
            d.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_GATHER_WOOD_001",
                new ExecutionSample(0.05, 0.05)));

            var tagged = d.Journal.OfType<CampTagAdded>().Single(t => t.Tag == "TOOL_DAMAGED");
            Assert.Equal("INT_GATHER_WOOD_001", tagged.SourceActionId);
        }

        [Fact]
        public void Camp_values_are_clamped_between_zero_and_one_hundred()
        {
            var state = new ScenarioState("SCN_STORMNATTEN_001", 1);
            state.Camp.ShelterIntegrity = 95;

            EffectApplier.Apply(state, Effect(shelter: 40), new[] { 0, 1 });
            Assert.Equal(100, state.Camp.ShelterIntegrity);

            EffectApplier.Apply(state, Effect(shelter: -400), new[] { 0, 1 });
            Assert.Equal(0, state.Camp.ShelterIntegrity);
        }

        /// <summary>En handling der koster mere end der findes, bruger hvad der er - den skaber ikke gæld.</summary>
        [Fact]
        public void Resources_never_go_negative()
        {
            var state = new ScenarioState("SCN_STORMNATTEN_001", 1);
            state.Resources["wood"] = 2;

            var events = EffectApplier.Apply(state, Effect(wood: -10), new[] { 0, 1 });

            Assert.Equal(0, state.Resources["wood"]);
            Assert.Equal(-2, events.OfType<ResourceChanged>().Single().Delta);
        }

        [Fact]
        public void Fatigue_is_applied_to_the_participants_only()
        {
            var state = new ScenarioState("SCN_STORMNATTEN_001", 1);
            EffectApplier.Apply(state, Effect(fatigue: 12), new[] { 1 });

            Assert.Equal(0, state.Players[0].Fatigue);
            Assert.Equal(12, state.Players[1].Fatigue);
        }

        /// <summary>
        /// En manglende FailForward-effekt opdages ellers først, når to spillere står
        /// og undrer sig over, at intet skete.
        /// </summary>
        [Fact]
        public void Validation_catches_a_missing_tier()
        {
            var table = new EffectTable();
            table.Set("INT_BUILD_SHELTER_003", OutcomeTier.Success, Effect(shelter: 10));

            var problems = table.Validate();
            Assert.Contains(problems, p => p.Contains("FailForward") && p.Contains("mangler"));
            Assert.Equal(3, problems.Count);
        }

        [Fact]
        public void Validation_catches_an_empty_effect()
        {
            var table = FullTableFor("INT_FIND_FOOD_002");
            table.Set("INT_FIND_FOOD_002", OutcomeTier.PartialWithCost, new ActionEffect());

            Assert.Contains(table.Validate(), p => p.Contains("tom effekt"));
        }

        [Fact]
        public void A_complete_table_validates_clean()
        {
            Assert.Empty(FullTableFor("INT_GATHER_WOOD_001").Validate());
        }

        [Fact]
        public void An_unknown_camp_field_throws_rather_than_being_ignored()
        {
            var state = new ScenarioState("SCN_STORMNATTEN_001", 1);
            var bogus = new ActionEffect(campDeltas: new Dictionary<string, int> { ["moraleVibes"] = 5 });

            Assert.Throws<InvalidOperationException>(() => EffectApplier.Apply(state, bogus, new[] { 0, 1 }));
        }

        /// <summary>Uden en effekttabel kører direktoren stadig - effekter er valgfri, ikke påkrævede.</summary>
        [Fact]
        public void A_director_without_an_effect_table_still_resolves_actions()
        {
            var d = new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 2));
            d.Submit(new AdvancePhaseCommand("p0", 0));
            d.Submit(new AdvancePhaseCommand("p1", 0));
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 2));
            d.Submit(new ConfirmPlanCommand("c1", 0));
            d.Submit(new AdvancePhaseCommand("p2", 0));
            d.Submit(new AdvancePhaseCommand("p3", 0));

            var produced = d.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_A_001",
                new ExecutionSample(0.9, 0.9)));

            Assert.Single(produced.OfType<ActionResolved>());
            Assert.Empty(produced.OfType<ResourceChanged>());
        }
    }
}
