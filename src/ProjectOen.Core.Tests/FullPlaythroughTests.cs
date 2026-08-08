using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Persistence;
using ProjectOen.Core.Scenario;
using ProjectOen.Core.Telemetry;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// Beviset på at delene komponerer. Alt andet i suiten tester ét system i isolation;
    /// de sidste fem fund kom alle fra sømme mellem systemer.
    ///
    /// Spiller et helt scenario: indlæs → tre dage → storm → udfald → efterspilsrapport,
    /// med et checkpoint undervejs.
    /// </summary>
    public class FullPlaythroughTests
    {
        readonly ITestOutputHelper _out;
        public FullPlaythroughTests(ITestOutputHelper output) => _out = output;

        static ScenarioDefinition Definition() => ScenarioLoader.Load(TestVector.LoadScenarioExample(), 1);

        static void AdvanceTo(ScenarioDirector d, ScenarioPhase phase, int day, string prefix)
        {
            var guard = 0;
            while (!(d.State.Phase == phase && d.State.Day == day) && guard++ < 60)
                d.Submit(new AdvancePhaseCommand($"{prefix}{guard}", 0));
            Assert.True(guard < 60, $"Nåede aldrig {phase} dag {day}, sad fast i {d.State.Phase} dag {d.State.Day}.");
        }

        static void PlayADay(ScenarioDirector d, ScenarioDefinition def, int day, double quality, string prefix)
        {
            AdvanceTo(d, ScenarioPhase.Planning, day, prefix + "plan");

            var available = def.Actions.Values
                .Where(a => a.UnlockedBy.Count == 0)
                .Where(a => !d.State.Players.Any(p => ConditionModel.IsBlockedFor(p, def.Conditions, a.Id)))
                .Take(2).ToList();

            foreach (var (action, i) in available.Select((a, i) => (a, i)))
                d.Submit(new PlaceEffortMarkerCommand($"{prefix}m{i}", i, action.Id, 2));

            d.Submit(new ConfirmPlanCommand($"{prefix}confirm", 0));
            AdvanceTo(d, ScenarioPhase.ActionSequence, day, prefix + "act");

            foreach (var (action, i) in available.Select((a, i) => (a, i)))
                d.Submit(new CompleteInteractionStepCommand($"{prefix}s{i}", i, action.Id,
                    new ExecutionSample(quality, quality)));
        }

        [Fact]
        public void A_competent_run_reaches_the_storm_and_produces_a_readable_report()
        {
            var def = Definition();
            var d = new ScenarioDirector(def.CreateState(1234), def);

            for (var day = 1; day <= 3; day++) PlayADay(d, def, day, 0.85, $"d{day}-");
            AdvanceTo(d, ScenarioPhase.Storm, 3, "storm");

            var storm = d.Journal.OfType<StormComplicationTriggered>().ToList();
            _out.WriteLine("=== rapport ===");
            foreach (var line in AfterActionReport.Explain(d.Journal)) _out.WriteLine(line);

            Assert.Equal(ScenarioPhase.Storm, d.State.Phase);
            Assert.NotEmpty(storm);
            Assert.All(storm, s => Assert.False(string.IsNullOrWhiteSpace(s.Reason)));
            Assert.NotEmpty(d.Journal.OfType<ActionResolved>());
        }

        /// <summary>Scenariet skal kunne slutte. Uden det spiller man til verdens ende.</summary>
        [Fact]
        public void The_scenario_actually_concludes()
        {
            var def = Definition();
            var d = new ScenarioDirector(def.CreateState(7), def);

            for (var day = 1; day <= 3; day++) PlayADay(d, def, day, 0.85, $"d{day}-");
            AdvanceTo(d, ScenarioPhase.Epilogue, 3, "end");

            var concluded = d.Journal.OfType<ScenarioConcluded>().ToList();
            _out.WriteLine($"udfald: {d.Verdict} | {concluded.Count} ScenarioConcluded i journalen");

            Assert.Single(concluded);
            Assert.NotEqual(ScenarioVerdict.InProgress, d.Verdict);
        }

        /// <summary>Samme lejr, samme storm. Ellers er tre dages beslutninger ligegyldige.</summary>
        [Fact]
        public void Two_identical_runs_produce_identical_journals()
        {
            IReadOnlyList<string> Run()
            {
                var def = Definition();
                var d = new ScenarioDirector(def.CreateState(55), def);
                for (var day = 1; day <= 3; day++) PlayADay(d, def, day, 0.8, $"d{day}-");
                AdvanceTo(d, ScenarioPhase.Epilogue, 3, "end");
                return d.Journal.Select(e => e.GetType().Name + ":" + e.Revision).ToList();
            }

            Assert.Equal(Run(), Run());
        }

        /// <summary>
        /// Et dårligt spil skal ramme hårdere end et godt. Ellers betyder udførelsen intet.
        ///
        /// Måler lejrens samlede tilstand, ikke ét felt: de handlinger et run faktisk
        /// vælger, rammer forskellige felter, og en måling af `shelterIntegrity` alene
        /// gav 0 mod 0 — ikke fordi udførelsen var ligegyldig, men fordi kørslen aldrig
        /// byggede læ. Testen målte det forkerte.
        /// </summary>
        [Fact]
        public void A_poor_run_leaves_the_camp_worse_off_after_the_storm()
        {
            (int total, string detail) CampAfterStorm(double quality)
            {
                var def = Definition();
                var d = new ScenarioDirector(def.CreateState(3), def);
                for (var day = 1; day <= 3; day++) PlayADay(d, def, day, quality, $"d{day}-");
                AdvanceTo(d, ScenarioPhase.Storm, 3, "storm");

                var c = d.State.Camp;
                var total = c.ShelterIntegrity + c.FireStrength + c.FoodSecurity + c.SignalProgress - c.CampThreat;
                return (total, $"læ {c.ShelterIntegrity} ild {c.FireStrength} mad {c.FoodSecurity} " +
                               $"signal {c.SignalProgress} trussel {c.CampThreat}");
            }

            var good = CampAfterStorm(0.95);
            var bad = CampAfterStorm(0.05);
            _out.WriteLine($"dygtigt spil: {good.total} ({good.detail})");
            _out.WriteLine($"dårligt spil: {bad.total} ({bad.detail})");

            Assert.True(bad.total < good.total, "Udførelsen skal kunne aflæses i lejren efter stormen.");
        }

        /// <summary>Et checkpoint midt i spillet skal kunne genoptages uden at ændre noget.</summary>
        [Fact]
        public void A_mid_game_checkpoint_resumes_into_the_same_ending()
        {
            var def = Definition();

            var straight = new ScenarioDirector(def.CreateState(88), def);
            for (var day = 1; day <= 3; day++) PlayADay(straight, def, day, 0.8, $"d{day}-");
            AdvanceTo(straight, ScenarioPhase.Epilogue, 3, "end");

            var interrupted = new ScenarioDirector(def.CreateState(88), def);
            PlayADay(interrupted, def, 1, 0.8, "d1-");
            PlayADay(interrupted, def, 2, 0.8, "d2-");

            var save = ScenarioSnapshot.Capture(interrupted.State, 1, def.ContentVersion, 1, "DAY2");
            var resumed = new ScenarioDirector(ScenarioSnapshot.Restore(save), def);
            PlayADay(resumed, def, 3, 0.8, "d3-");
            AdvanceTo(resumed, ScenarioPhase.Epilogue, 3, "end");

            _out.WriteLine($"uafbrudt: {straight.Verdict} | genoptaget: {resumed.Verdict}");
            Assert.Equal(straight.Verdict, resumed.Verdict);
            Assert.Equal(
                straight.Journal.OfType<StormComplicationTriggered>().Select(s => s.ComplicationId),
                resumed.Journal.OfType<StormComplicationTriggered>().Select(s => s.ComplicationId));
        }

        [Fact]
        public void No_event_in_a_full_run_is_journalled_twice()
        {
            var def = Definition();
            var d = new ScenarioDirector(def.CreateState(21), def);
            for (var day = 1; day <= 3; day++) PlayADay(d, def, day, 0.7, $"d{day}-");
            AdvanceTo(d, ScenarioPhase.Epilogue, 3, "end");

            var duplicates = d.Journal
                .GroupBy(e => new { Type = e.GetType().Name, e.Revision })
                .Where(g => g.Key.Revision > 0)
                .Where(g => g.Count() > 1).ToList();

            Assert.True(duplicates.Count == 0,
                "Dubletter: " + string.Join(", ", duplicates.Select(g => $"{g.Key.Type}@{g.Key.Revision}")));
        }
    }
}
