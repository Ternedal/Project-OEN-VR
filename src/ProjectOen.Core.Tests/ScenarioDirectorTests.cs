using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;

namespace ProjectOen.Core.Tests
{
    public class ScenarioDirectorTests
    {
        static ScenarioDirector AtPlanning()
        {
            var d = new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 42));
            d.Submit(new AdvancePhaseCommand("c-intro", 0));  // Intro -> Dawn
            d.Submit(new AdvancePhaseCommand("c-dawn", 0));   // Dawn  -> Planning
            Assert.Equal(ScenarioPhase.Planning, d.State.Phase);
            return d;
        }

        [Fact]
        public void Four_markers_is_the_hard_ceiling()
        {
            var d = AtPlanning();
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 2));
            d.Submit(new PlaceEffortMarkerCommand("m2", 1, "INT_B_002", 2));
            Assert.Equal(0, d.State.MarkersRemaining);

            var rejected = d.Submit(new PlaceEffortMarkerCommand("m3", 0, "INT_C_003", 1));
            Assert.Contains(rejected.OfType<CommandRejected>(), r => r.Code == "NO_MARKERS_LEFT");
        }

        [Fact]
        public void Three_or_more_markers_on_one_action_is_rejected()
        {
            var d = AtPlanning();
            var rejected = d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 3));
            Assert.Contains(rejected.OfType<CommandRejected>(), r => r.Code == "MARKER_COUNT");
        }

        /// <summary>FLOW-001 i docs/13: kun én planversion må låses.</summary>
        [Fact]
        public void Plan_lock_race_produces_exactly_one_lock()
        {
            var d = AtPlanning();
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 2));

            var first = d.Submit(new ConfirmPlanCommand("confirm-a", 0));
            var second = d.Submit(new ConfirmPlanCommand("confirm-b", 1));

            Assert.Single(first.OfType<PlanLocked>());
            Assert.Empty(second.OfType<PlanLocked>());
            Assert.Contains(second.OfType<CommandRejected>(), r => r.Code == "ALREADY_LOCKED");
            Assert.Single(d.Journal.OfType<PlanLocked>());
        }

        [Fact]
        public void Marker_after_lock_is_rejected()
        {
            var d = AtPlanning();
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 1));
            d.Submit(new ConfirmPlanCommand("confirm", 0));

            var rejected = d.Submit(new PlaceEffortMarkerCommand("m2", 1, "INT_B_002", 1));
            Assert.Contains(rejected.OfType<CommandRejected>(), r => r.Code == "PLAN_LOCKED");
        }

        /// <summary>
        /// docs/07 afsnit 11: commands er idempotente via command-ID. Efter reconnect
        /// gentager klienten - det skal koste ingenting.
        /// </summary>
        [Fact]
        public void Replaying_the_same_command_id_changes_nothing()
        {
            var d = AtPlanning();
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 2));
            var revisionAfterFirst = d.State.Revision;

            var replay = d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 2));

            Assert.Empty(replay);
            Assert.Equal(revisionAfterFirst, d.State.Revision);
            Assert.Equal(2, d.State.MarkersRemaining);
        }

        [Fact]
        public void An_interaction_step_cannot_be_counted_twice()
        {
            var d = AtPlanning();
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 2));
            d.Submit(new ConfirmPlanCommand("confirm", 0));
            d.Submit(new AdvancePhaseCommand("a1", 0));   // Planning -> ResolvePlan
            d.Submit(new AdvancePhaseCommand("a2", 0));   // ResolvePlan -> ActionSequence

            var input = new OutcomeInput(0.8, 0.8, 0.8, 0.0);
            var first = d.Submit(new CompleteInteractionStepCommand("s1", 0, "INT_A_001", input));
            var again = d.Submit(new CompleteInteractionStepCommand("s2", 1, "INT_A_001", input));

            Assert.Single(first.OfType<ActionResolved>());
            Assert.Contains(again.OfType<CommandRejected>(), r => r.Code == "ALREADY_COMPLETED");
        }

        [Fact]
        public void Revision_is_monotonic()
        {
            var d = AtPlanning();
            var seen = 0;
            foreach (var e in d.Journal)
            {
                Assert.True(e.Revision >= seen);
                seen = e.Revision;
            }
            Assert.True(d.State.Revision > 0);
        }

        [Fact]
        public void Day_three_night_leads_into_the_storm()
        {
            var d = new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 1));
            var guard = 0;
            while (d.State.Phase != ScenarioPhase.Storm && guard++ < 40)
                d.Submit(new AdvancePhaseCommand($"a{guard}", 0));

            Assert.Equal(ScenarioPhase.Storm, d.State.Phase);
            Assert.Equal(3, d.State.Day);
            Assert.Contains(d.Journal.OfType<CheckpointCreated>(), c => c.CheckpointId.StartsWith("Storm"));
        }

        [Fact]
        public void A_new_day_clears_the_plan()
        {
            var d = AtPlanning();
            d.Submit(new PlaceEffortMarkerCommand("m1", 0, "INT_A_001", 2));
            d.Submit(new ConfirmPlanCommand("confirm", 0));

            var guard = 0;
            while (!(d.State.Phase == ScenarioPhase.Planning && d.State.Day == 2) && guard++ < 20)
                d.Submit(new AdvancePhaseCommand($"n{guard}", 0));

            Assert.Equal(2, d.State.Day);
            Assert.False(d.State.PlanLocked);
            Assert.Equal(ScenarioState.TotalMarkers, d.State.MarkersRemaining);
        }
    }
}
