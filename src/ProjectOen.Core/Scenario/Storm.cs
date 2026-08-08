using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Scenario
{
    public enum CampComparison { AtMost, AtLeast }

    public sealed class CampCondition
    {
        public CampCondition(string field, CampComparison comparison, int threshold)
        {
            Field = field;
            Comparison = comparison;
            Threshold = threshold;
        }

        public string Field { get; }
        public CampComparison Comparison { get; }
        public int Threshold { get; }

        public bool IsMet(CampState camp)
        {
            var value = Read(camp, Field);
            return Comparison == CampComparison.AtMost ? value <= Threshold : value >= Threshold;
        }

        public string Describe(CampState camp) =>
            $"{Field} {Read(camp, Field)} {(Comparison == CampComparison.AtMost ? "<=" : ">=")} {Threshold}";

        internal static int Read(CampState camp, string field) => field switch
        {
            "shelterIntegrity" => camp.ShelterIntegrity,
            "fireStrength" => camp.FireStrength,
            "foodSecurity" => camp.FoodSecurity,
            "signalProgress" => camp.SignalProgress,
            "campThreat" => camp.CampThreat,
            _ => throw new InvalidOperationException($"Ukendt lejrfelt '{field}'.")
        };
    }

    public sealed class StormComplication
    {
        public StormComplication(string id, int severity, ActionEffect effect,
            IEnumerable<CampCondition>? campConditions = null,
            IEnumerable<string>? requiredTags = null,
            IEnumerable<string>? forbiddenTags = null,
            bool isBaseline = false)
        {
            Id = id;
            Severity = severity;
            Effect = effect;
            CampConditions = (campConditions ?? Enumerable.Empty<CampCondition>()).ToList();
            RequiredTags = (requiredTags ?? Enumerable.Empty<string>()).ToList();
            ForbiddenTags = (forbiddenTags ?? Enumerable.Empty<string>()).ToList();
            IsBaseline = isBaseline;
        }

        public string Id { get; }

        /// <summary>Hoejere = vaerre. Bestemmer raekkefoelgen, naar der skal skaeres til loftet.</summary>
        public int Severity { get; }

        public ActionEffect Effect { get; }
        public IReadOnlyList<CampCondition> CampConditions { get; }
        public IReadOnlyList<string> RequiredTags { get; }
        public IReadOnlyList<string> ForbiddenTags { get; }

        /// <summary>
        /// Baseline-komplikationer udloeses uanset lejrens tilstand. Uden dem faar en
        /// velspillet gennemgang en stille finale - og stormen er scenariets klimaks,
        /// ikke dens belOnning for at have fejlet.
        /// </summary>
        public bool IsBaseline { get; }
    }

    public sealed class SelectedComplication
    {
        public SelectedComplication(StormComplication complication, string reason)
        {
            Complication = complication;
            Reason = reason;
        }

        public StormComplication Complication { get; }

        /// <summary>Hvorfor den ramte. En komplikation uden forklaring er ren straf.</summary>
        public string Reason { get; }
    }

    public sealed class StormCatalog
    {
        readonly List<StormComplication> _complications = new List<StormComplication>();

        /// <summary>
        /// Loft paa samtidige komplikationer. Stormen har 12-16 minutter i docs/05;
        /// uden loft giver en daarlig gennemgang en uspillelig ophobning.
        /// </summary>
        public int MaxSimultaneous { get; set; } = 3;

        public void Add(StormComplication complication) => _complications.Add(complication);
        public IReadOnlyList<StormComplication> All => _complications;

        public IReadOnlyList<string> Validate()
        {
            var problems = new List<string>();

            foreach (var group in _complications.GroupBy(c => c.Id).Where(g => g.Count() > 1))
                problems.Add($"Dubleret komplikations-ID: {group.Key}.");

            foreach (var c in _complications)
            {
                if (c.Effect.IsEmpty)
                    problems.Add($"{c.Id}: tom effekt. En komplikation der ikke goer noget, er ikke en komplikation.");

                // Hver komplikation skal kunne forklares bagefter. En der hverken haenger
                // paa lejrens tilstand eller et tag, kan ikke spores til en beslutning.
                if (!c.IsBaseline && c.CampConditions.Count == 0 && c.RequiredTags.Count == 0)
                    problems.Add($"{c.Id}: hverken campConditions, requiredTags eller isBaseline. Den kan ikke forklares.");
            }

            if (!_complications.Any(c => c.IsBaseline))
                problems.Add("Ingen baseline-komplikation. En velspillet gennemgang ville faa en stille storm.");

            return problems;
        }
    }

    /// <summary>
    /// docs/05's stormfinale: "Stormen laeser lejrens tilstand."
    ///
    /// Udvaelgelsen er DETERMINISTISK. Der er ingen terning her, og det er med vilje:
    /// stormen er udbetalingen paa tre dages beslutninger, og docs/04 afsnit 9 siger,
    /// at tilfaeldighed maa aendre omkostningen, ikke slette det spillerne opnaaede.
    /// Rammer et tag flaengen i taget, skal det vaere fordi taget aldrig blev forstaerket.
    /// </summary>
    public static class StormResolver
    {
        public static IReadOnlyList<SelectedComplication> Select(ScenarioState state, StormCatalog catalog)
        {
            var selected = new List<SelectedComplication>();

            foreach (var c in catalog.All)
            {
                if (c.ForbiddenTags.Any(state.Tags.Contains)) continue;
                if (!c.RequiredTags.All(state.Tags.Contains)) continue;
                if (!c.CampConditions.All(cond => cond.IsMet(state.Camp))) continue;

                selected.Add(new SelectedComplication(c, Explain(c, state)));
            }

            var cap = Math.Max(1, catalog.MaxSimultaneous);

            // Vaerst foerst. Ved samme severity afgoer ID, saa udvaelgelsen er reproducerbar.
            var ranked = selected
                .OrderByDescending(s => s.Complication.Severity)
                .ThenBy(s => s.Complication.Id, StringComparer.Ordinal)
                .ToList();

            var result = ranked.Take(cap).ToList();

            // Tag-drevne komplikationer er dem, der kan spores tilbage til en konkret
            // beslutning ("I lod maden staa aaben"). De har typisk lavere severity end
            // strukturelle svigt, saa et rent severity-loft skaerer netop dem vaek -
            // og stormen ville vise generiske katastrofer og skjule den, spillerne
            // selv havde tjent. Derfor er mindst én plads reserveret til dem.
            if (result.All(s => s.Complication.RequiredTags.Count == 0))
            {
                var earned = ranked.FirstOrDefault(s => s.Complication.RequiredTags.Count > 0);
                if (earned != null && result.Count > 0)
                {
                    result[result.Count - 1] = earned;
                    result = result
                        .OrderByDescending(s => s.Complication.Severity)
                        .ThenBy(s => s.Complication.Id, StringComparer.Ordinal)
                        .ToList();
                }
            }

            return result;
        }

        static string Explain(StormComplication c, ScenarioState state)
        {
            var parts = new List<string>();
            parts.AddRange(c.CampConditions.Select(cond => cond.Describe(state.Camp)));
            parts.AddRange(c.RequiredTags);
            return parts.Count > 0 ? string.Join(" + ", parts) : "stormen selv";
        }
    }
}

namespace ProjectOen.Core.Scenario
{
    public sealed class StormComplicationTriggered : ScenarioEvent
    {
        public StormComplicationTriggered(string complicationId, string reason)
        {
            ComplicationId = complicationId;
            Reason = reason;
        }

        public string ComplicationId { get; }

        /// <summary>Hvilken lejrtilstand eller hvilket tag der udloeste den.</summary>
        public string Reason { get; }
    }

    public sealed class ScenarioConcluded : ScenarioEvent
    {
        public ScenarioConcluded(ScenarioVerdict verdict, System.Collections.Generic.IReadOnlyList<string> reasons)
        {
            Verdict = verdict;
            Reasons = reasons;
        }

        public ScenarioVerdict Verdict { get; }
        public System.Collections.Generic.IReadOnlyList<string> Reasons { get; }
    }
}
