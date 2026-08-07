using ProjectOen.Core.Telemetry;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// CR-007 / UX-002. Reviewet krævede, at projektets centrale designgate måles
    /// i stedet for observeres. Det er dét, disse tests holder fast i.
    /// </summary>
    public class ParticipationTests
    {
        readonly ITestOutputHelper _out;
        public ParticipationTests(ITestOutputHelper output) => _out = output;

        const double Frame = 1.0 / 72.0;

        static ActiveParticipationTracker Run(string actionId, double seconds,
                                              System.Func<double, bool> p0, System.Func<double, bool> p1,
                                              bool excluded = false)
        {
            var t = new ActiveParticipationTracker();
            t.BeginAction(actionId, 0, excluded);
            for (var time = Frame; time <= seconds + 1e-9; time += Frame)
                t.Sample(time, p0(time), p1(time));
            t.EndAction(seconds);
            return t;
        }

        [Fact]
        public void Perfect_cooperation_scores_full_share_and_passes_the_gate()
        {
            var report = Run("INT_REINFORCE_ROOF_001", 20, _ => true, _ => true).Build();
            _out.WriteLine(report.Summarize());

            Assert.Equal(1.0, report.BothActiveShare, 2);
            Assert.Empty(report.PassivePeriods);
            Assert.True(report.MeetsGate);
        }

        [Fact]
        public void One_player_watching_the_whole_time_fails_the_gate()
        {
            var report = Run("INT_BUILD_SIGNAL_009", 30, _ => true, _ => false).Build();
            _out.WriteLine(report.Summarize());

            Assert.Equal(0.0, report.BothActiveShare, 2);
            Assert.True(report.LongestPassiveSeconds > 29);
            Assert.False(report.MeetsGate);
            Assert.Equal(1, report.PeriodsOverTestThreshold);
        }

        /// <summary>
        /// Den situation, reviewet var mest bekymret for: et resultat der ser fint ud
        /// i gennemsnit, men skjuler en lang passiv periode.
        /// </summary>
        [Fact]
        public void A_good_average_does_not_hide_a_long_passive_stretch()
        {
            // Spiller 1 er passiv i 25 sekunder midt i en 100-sekunders sekvens.
            var report = Run("INT_RAVINE_RESCUE_004", 100, _ => true, time => time < 30 || time > 55).Build();
            _out.WriteLine(report.Summarize());

            Assert.True(report.BothActiveShare > 0.70, "Gennemsnittet alene ville bestå.");
            Assert.Equal(1, report.PeriodsOverTestThreshold);
            Assert.False(report.MeetsGate);
        }

        [Fact]
        public void Fifteen_seconds_breaks_the_design_rule_but_not_the_test_threshold()
        {
            // 15 s passiv i en 60-sekunders sekvens = 75 % begge aktive, altså over andels-gaten.
            // Første udgave af testen brugte 40 s, hvilket giver 62,5 % — den fejlede på
            // andels-gaten og beviste dermed ikke det, den skulle. Målingen var rigtig;
            // forventningen var sjusket.
            var report = Run("INT_GATHER_WOOD_001", 60, _ => true, time => time < 10 || time > 25).Build();
            _out.WriteLine(report.Summarize());

            Assert.Equal(1, report.PeriodsOverDesignRule);
            Assert.Equal(0, report.PeriodsOverTestThreshold);
            Assert.True(report.MeetsGate, "12 s er designreglen, 20 s er gaten. Forskellen skal kunne aflæses.");
        }

        /// <summary>
        /// docs/04 afsnit 8 undtager sekvenser, begge observerer. Undtagelsen skal sættes
        /// bevidst, så den ikke kan bruges til at bortforklare et dårligt resultat.
        /// </summary>
        [Fact]
        public void An_excluded_dramatic_sequence_records_no_passive_periods()
        {
            var report = Run("SEQ_COLLAPSE_001", 30, _ => false, _ => false, excluded: true).Build();
            Assert.Empty(report.PassivePeriods);
            Assert.Equal(0.0, report.BothActiveShare, 2);
        }

        [Fact]
        public void Passivity_is_tracked_per_player()
        {
            var report = Run("INT_TREAT_INJURY_011", 60, time => time > 25, time => time < 35).Build();
            Assert.Contains(report.PassivePeriods, p => p.PlayerSlot == 0);
            Assert.Contains(report.PassivePeriods, p => p.PlayerSlot == 1);
        }

        [Fact]
        public void Exactly_seventy_percent_passes()
        {
            var report = Run("INT_FIND_FIBER_007", 100, _ => true, time => time <= 70).Build();
            _out.WriteLine(report.Summarize());
            Assert.True(report.BothActiveShare >= 0.699);
        }
    }
}
