using System;
using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;

namespace ProjectOen.Core.Tests
{
    public class ScenarioOutcomeRulesTests
    {
        static ScenarioState AtSignal(int signalProgress, int shelter = 60, int health0 = 90, int health1 = 85)
        {
            var s = new ScenarioState("SCN_STORMNATTEN_001", 1) { Phase = ScenarioPhase.Signal, Day = 3 };
            s.Camp.SignalProgress = signalProgress;
            s.Camp.ShelterIntegrity = shelter;
            s.Camp.FireStrength = 40;
            s.Players[0].Health = health0;
            s.Players[1].Health = health1;
            return s;
        }

        static ScenarioOutcomeRules.Rule R(string type, params (string, object?)[] p) =>
            new ScenarioOutcomeRules.Rule(type, p.ToDictionary(x => x.Item1, x => x.Item2));

        static readonly ScenarioOutcomeRules.Rule[] Win = { R(ScenarioOutcomeRules.SignalLitBeforeDeadline) };
        static readonly ScenarioOutcomeRules.Rule[] Lose =
        {
            R(ScenarioOutcomeRules.AllPlayersIncapacitated),
            R(ScenarioOutcomeRules.SignalWindowMissed),
        };

        /// <summary>docs/05: begge står oprejst, signal tændt, lejren overlever.</summary>
        [Fact]
        public void Signal_lit_with_both_standing_and_camp_intact_is_a_strong_win()
        {
            var result = ScenarioOutcomeRules.Evaluate(AtSignal(100), Win, Lose);
            Assert.Equal(ScenarioVerdict.StrongWin, result.Verdict);
            Assert.Contains(ScenarioOutcomeRules.SignalLitBeforeDeadline, result.Reasons);
        }

        /// <summary>docs/05: signal tændt, men lejren kollapsede eller en spiller er hårdt skadet.</summary>
        [Fact]
        public void Signal_lit_with_a_collapsed_camp_is_only_a_pressed_win()
        {
            var result = ScenarioOutcomeRules.Evaluate(AtSignal(100, shelter: 0), Win, Lose);
            Assert.Equal(ScenarioVerdict.PressedWin, result.Verdict);
        }

        [Fact]
        public void Three_injuries_on_one_player_downgrades_the_win()
        {
            var state = AtSignal(100);
            state.Players[1].AddInjury("HAND_CUT");
            state.Players[1].AddInjury("SPRAINED_ANKLE");
            state.Players[1].AddInjury("INFECTION");

            Assert.Equal(ScenarioVerdict.PressedWin, ScenarioOutcomeRules.Evaluate(state, Win, Lose).Verdict);
        }

        /// <summary>Tab slår sejr. Man vinder ikke, mens begge ligger ned.</summary>
        [Fact]
        public void A_lose_rule_takes_precedence_over_a_win_rule()
        {
            var state = AtSignal(100, health0: 0, health1: 0);
            var result = ScenarioOutcomeRules.Evaluate(state, Win, Lose);

            Assert.Equal(ScenarioVerdict.Loss, result.Verdict);
            Assert.Contains(ScenarioOutcomeRules.AllPlayersIncapacitated, result.Reasons);
        }

        [Fact]
        public void An_unfinished_signal_at_signal_phase_is_still_in_progress()
        {
            Assert.Equal(ScenarioVerdict.InProgress, ScenarioOutcomeRules.Evaluate(AtSignal(70), Win, Lose).Verdict);
        }

        [Fact]
        public void Reaching_the_epilogue_without_the_signal_is_a_loss()
        {
            var state = AtSignal(70);
            state.Phase = ScenarioPhase.Epilogue;

            var result = ScenarioOutcomeRules.Evaluate(state, Win, Lose);
            Assert.Equal(ScenarioVerdict.Loss, result.Verdict);
            Assert.Contains(ScenarioOutcomeRules.SignalWindowMissed, result.Reasons);
        }

        /// <summary>Tærskler kommer fra scenariodata, ikke fra kode - jf. docs/10.</summary>
        [Fact]
        public void Thresholds_come_from_the_rule_parameters()
        {
            var lenient = new[] { R(ScenarioOutcomeRules.SignalLitBeforeDeadline, ("threshold", 70)) };
            Assert.Equal(ScenarioVerdict.StrongWin, ScenarioOutcomeRules.Evaluate(AtSignal(70), lenient, Lose).Verdict);
            Assert.Equal(ScenarioVerdict.InProgress, ScenarioOutcomeRules.Evaluate(AtSignal(70), Win, Lose).Verdict);
        }

        /// <summary>
        /// Et scenario, der stille taber sin egen tabsbetingelse, er værre end
        /// et scenario der ikke kan starte.
        /// </summary>
        [Fact]
        public void An_unknown_rule_type_throws_instead_of_silently_passing()
        {
            var bogus = new[] { R("everyoneGetsIceCream") };
            var ex = Assert.Throws<InvalidOperationException>(
                () => ScenarioOutcomeRules.Evaluate(AtSignal(100), Win, bogus));
            Assert.Contains("Ukendt regeltype", ex.Message);
        }

        [Fact]
        public void The_contract_rejects_an_unknown_rule_type_at_load_time()
        {
            var scenario = TestVector.LoadScenarioExample();
            ((List<object?>)scenario["loseRules"]!).Add(new Dictionary<string, object?> { ["type"] = "everyoneGetsIceCream" });

            var violations = new ScenarioContract().Validate(scenario, 1);
            Assert.Contains(violations, v => v.Code == "RULE_TYPE_UNKNOWN");
        }

        [Fact]
        public void The_repository_scenario_example_uses_only_known_rule_types()
        {
            var violations = new ScenarioContract().Validate(TestVector.LoadScenarioExample(), 1);
            Assert.DoesNotContain(violations, v => v.Code == "RULE_TYPE_UNKNOWN" || v.Code == "RULES_MISSING");
        }
    }
}
