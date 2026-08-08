#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Scenario
{
    public enum ScenarioVerdict
    {
        InProgress,
        StrongWin,
        PressedWin,
        Loss
    }

    public sealed class RuleEvaluation
    {
        public RuleEvaluation(ScenarioVerdict verdict, IReadOnlyList<string> reasons)
        {
            Verdict = verdict;
            Reasons = reasons;
        }

        public ScenarioVerdict Verdict { get; }

        /// <summary>Hvilke regler der udloeste. Efterspilsrapporten skal kunne pege paa dem.</summary>
        public IReadOnlyList<string> Reasons { get; }
    }

    /// <summary>
    /// docs/05 win/lose states, gjort data-drevet. Scenariodata siger HVILKE regler
    /// der gaelder; koden siger hvad hver regeltype betyder.
    ///
    /// Det er bevidst ikke content: der staar ingen Stormnatten-vaerdier her. Reglerne
    /// kommer fra scenario-JSON'ens winRules/loseRules, saa balancering kan foregaa
    /// uden rebuild - jf. docs/10's princip om at design-data kan aendres uden at
    /// omskrive kode.
    ///
    /// En ukendt regeltype er en FEJL, ikke en no-op. Et scenario, der stille taber
    /// sin egen tabsbetingelse, er vaerre end et scenario der ikke kan starte.
    /// </summary>
    public static class ScenarioOutcomeRules
    {
        public const string SignalLitBeforeDeadline = "signalLitBeforeDeadline";
        public const string AllPlayersIncapacitated = "allPlayersIncapacitated";
        public const string SignalWindowMissed = "signalWindowMissed";
        public const string FireLostPermanently = "fireLostPermanently";
        public const string ShelterCollapsed = "shelterCollapsed";

        public static readonly IReadOnlyCollection<string> KnownTypes = new[]
        {
            SignalLitBeforeDeadline, AllPlayersIncapacitated, SignalWindowMissed,
            FireLostPermanently, ShelterCollapsed
        };

        /// <summary>En regel: type plus valgfri parametre fra scenariodata.</summary>
        public sealed class Rule
        {
            public Rule(string type, IDictionary<string, object?>? parameters = null)
            {
                Type = type;
                Parameters = parameters ?? new Dictionary<string, object?>();
            }

            public string Type { get; }
            public IDictionary<string, object?> Parameters { get; }

            public int IntParam(string key, int fallback) =>
                Parameters.TryGetValue(key, out var v) && v != null
                    ? Convert.ToInt32(v)
                    : fallback;
        }

        public static RuleEvaluation Evaluate(ScenarioState state, IEnumerable<Rule> winRules, IEnumerable<Rule> loseRules)
        {
            var loseReasons = loseRules.Where(r => Matches(r, state)).Select(Describe).ToList();
            if (loseReasons.Count > 0)
                return new RuleEvaluation(ScenarioVerdict.Loss, loseReasons);

            var winReasons = winRules.Where(r => Matches(r, state)).Select(Describe).ToList();
            if (winReasons.Count == 0)
                return new RuleEvaluation(ScenarioVerdict.InProgress, Array.Empty<string>());

            // docs/05 skelner mellem staerk og presset sejr. Forskellen er ikke en regel
            // i data - den er tilstanden af de to spillere og lejren, naar sejren indtraeffer.
            var bothStanding = state.Players.All(p => p.Health > 0 && p.Injuries.Count < 3);
            var campHeld = state.Camp.ShelterIntegrity > 0;

            return new RuleEvaluation(
                bothStanding && campHeld ? ScenarioVerdict.StrongWin : ScenarioVerdict.PressedWin,
                winReasons);
        }

        static bool Matches(Rule rule, ScenarioState state)
        {
            switch (rule.Type)
            {
                case SignalLitBeforeDeadline:
                    return state.Camp.SignalProgress >= rule.IntParam("threshold", 100)
                           && (state.Phase == ScenarioPhase.Signal || state.Phase == ScenarioPhase.Epilogue)
                           && state.Day <= rule.IntParam("deadlineDay", 3);

                case AllPlayersIncapacitated:
                    return state.Players.All(p => p.Health <= 0);

                case SignalWindowMissed:
                    return state.Phase == ScenarioPhase.Epilogue
                           && state.Camp.SignalProgress < rule.IntParam("threshold", 100);

                case FireLostPermanently:
                    return state.Camp.FireStrength <= 0 && state.Tags.Contains("FIRE_LOST");

                case ShelterCollapsed:
                    return state.Camp.ShelterIntegrity <= rule.IntParam("threshold", 0);

                default:
                    // Fail loud. Et scenario der stille taber sin egen tabsbetingelse
                    // er vaerre end et scenario der ikke kan starte.
                    throw new InvalidOperationException(
                        $"Ukendt regeltype '{rule.Type}'. Kendte typer: {string.Join(", ", KnownTypes)}.");
            }
        }

        static string Describe(Rule rule) => rule.Type;
    }
}
