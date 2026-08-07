using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// docs/04 afsnit 10: aaben mad -> SCENT_HIGH -> mulig dyretrussel nat 2.
    /// SAVE-001 i docs/13: checkpoint gemmes efter event scheduling, foer trigger.
    /// Resume skal udloese eventet praecis \u00e9n gang.
    /// </summary>
    public class DelayedEventTests
    {
        static ScenarioDirector Fresh() => new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 7));

        static void AdvanceTo(ScenarioDirector d, ScenarioPhase phase, int day, string prefix)
        {
            var guard = 0;
            while (!(d.State.Phase == phase && d.State.Day == day) && guard++ < 40)
                d.Submit(new AdvancePhaseCommand($"{prefix}{guard}", 0));
        }

        [Fact]
        public void Open_food_on_day_one_becomes_an_animal_threat_on_night_two()
        {
            var d = Fresh();
            d.AddTag("SCENT_HIGH");
            d.Submit(new ScheduleDelayedEventCommand("sched-1", 0, "EVT_ANIMAL_AT_CAMP_002",
                triggerOnDay: 2, triggerPhase: ScenarioPhase.Night, requiredTag: "SCENT_HIGH"));

            AdvanceTo(d, ScenarioPhase.Night, 1, "n1-");
            Assert.Empty(d.Journal.OfType<DelayedEventTriggered>());   // ikke nat 1

            AdvanceTo(d, ScenarioPhase.Night, 2, "n2-");
            Assert.Single(d.Journal.OfType<DelayedEventTriggered>());
        }

        [Fact]
        public void The_event_does_not_fire_when_the_tag_was_never_set()
        {
            var d = Fresh();
            d.Submit(new ScheduleDelayedEventCommand("sched-1", 0, "EVT_ANIMAL_AT_CAMP_002",
                2, ScenarioPhase.Night, "SCENT_HIGH"));

            AdvanceTo(d, ScenarioPhase.Night, 2, "n-");
            Assert.Empty(d.Journal.OfType<DelayedEventTriggered>());
        }

        /// <summary>SAVE-001. Den fejl, der ellers foerst dukker op hos en spiller efter et reconnect.</summary>
        [Fact]
        public void Resume_after_checkpoint_triggers_the_event_exactly_once()
        {
            var d = Fresh();
            d.AddTag("SCENT_HIGH");

            // Klienten sender planlaegningen, mister forbindelsen, og sender den igen.
            d.Submit(new ScheduleDelayedEventCommand("sched-1", 0, "EVT_ANIMAL_AT_CAMP_002",
                2, ScenarioPhase.Night, "SCENT_HIGH"));
            d.Submit(new ScheduleDelayedEventCommand("sched-1", 0, "EVT_ANIMAL_AT_CAMP_002",
                2, ScenarioPhase.Night, "SCENT_HIGH"));

            Assert.Single(d.State.EventQueue);

            AdvanceTo(d, ScenarioPhase.Night, 2, "n-");
            Assert.Single(d.Journal.OfType<DelayedEventTriggered>());

            // Endnu et forsoeg paa at naa samme fase maa ikke genudloese den.
            d.Submit(new AdvancePhaseCommand("extra", 0));
            Assert.Single(d.Journal.OfType<DelayedEventTriggered>());
        }

        [Fact]
        public void Tags_are_idempotent()
        {
            var d = Fresh();
            d.AddTag("SHELTER_WEAK");
            d.AddTag("SHELTER_WEAK");
            Assert.Single(d.Journal.OfType<CampTagAdded>());
        }
    }
}
