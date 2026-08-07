using System.Linq;
using ProjectOen.Core.Scenario;
using ProjectOen.Core.Telemetry;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// M4's gate i docs/12: "tester kan forklare mindst én forsinket konsekvens."
    /// Rapporten bygges kun af event-journalen, så den ikke kan komme ud af trit
    /// med det, der faktisk skete.
    /// </summary>
    public class AfterActionReportTests
    {
        readonly ITestOutputHelper _out;
        public AfterActionReportTests(ITestOutputHelper output) => _out = output;

        static ScenarioDirector PlayThroughOpenFoodChain()
        {
            var d = new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 11));

            // Dag 1: maden bliver ikke sikret ordentligt.
            d.Submit(new AdvancePhaseCommand("a0", 0));   // Intro -> Dawn
            d.AddTag("SCENT_HIGH", "lod maden stå åben");
            d.Submit(new ScheduleDelayedEventCommand("s1", 0, "EVT_ANIMAL_AT_CAMP_002",
                2, ScenarioPhase.Night, "SCENT_HIGH"));

            var guard = 0;
            while (!(d.State.Phase == ScenarioPhase.Night && d.State.Day == 2) && guard++ < 40)
                d.Submit(new AdvancePhaseCommand($"a{guard}", 0));

            return d;
        }

        [Fact]
        public void The_chain_points_back_at_the_choice_that_caused_it()
        {
            var d = PlayThroughOpenFoodChain();
            var chains = AfterActionReport.BuildChains(d.Journal);

            var link = Assert.Single(chains);
            Assert.Equal("EVT_ANIMAL_AT_CAMP_002", link.Effect);
            Assert.Equal("SCENT_HIGH", link.Tag);
            Assert.Equal("lod maden stå åben", link.Cause);
            Assert.Equal(1, link.CauseDay);
            Assert.Equal(2, link.EffectDay);
            Assert.True(link.HasKnownCause);
        }

        [Fact]
        public void Produces_a_line_a_player_can_read()
        {
            var d = PlayThroughOpenFoodChain();
            var lines = AfterActionReport.Explain(d.Journal);

            foreach (var line in lines) _out.WriteLine(line);

            var line0 = Assert.Single(lines);
            Assert.Contains("fordi I", line0);
            Assert.Contains("dag 1", line0);
        }

        [Fact]
        public void An_event_without_a_recorded_cause_is_still_reported_but_marked()
        {
            var d = new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 3));
            d.Submit(new AdvancePhaseCommand("a0", 0));
            d.AddTag("SHELTER_WEAK");   // ingen kilde angivet
            d.Submit(new ScheduleDelayedEventCommand("s1", 0, "EVT_ROOF_LEAK_005",
                1, ScenarioPhase.Night, "SHELTER_WEAK"));

            var guard = 0;
            while (!(d.State.Phase == ScenarioPhase.Night && d.State.Day == 1) && guard++ < 20)
                d.Submit(new AdvancePhaseCommand($"a{guard}", 0));

            var link = Assert.Single(AfterActionReport.BuildChains(d.Journal));
            Assert.False(link.HasKnownCause);
            Assert.Equal("EVT_ROOF_LEAK_005", link.Effect);
        }

        [Fact]
        public void An_untriggered_event_never_appears_in_the_report()
        {
            var d = new ScenarioDirector(new ScenarioState("SCN_STORMNATTEN_001", 5));
            d.Submit(new AdvancePhaseCommand("a0", 0));
            d.Submit(new ScheduleDelayedEventCommand("s1", 0, "EVT_ANIMAL_AT_CAMP_002",
                2, ScenarioPhase.Night, "SCENT_HIGH"));   // tagget blev aldrig sat

            var guard = 0;
            while (!(d.State.Phase == ScenarioPhase.Night && d.State.Day == 2) && guard++ < 40)
                d.Submit(new AdvancePhaseCommand($"a{guard}", 0));

            Assert.Empty(AfterActionReport.BuildChains(d.Journal));
        }
    }
}
