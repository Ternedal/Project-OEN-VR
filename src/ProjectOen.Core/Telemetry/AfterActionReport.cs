using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Scenario;

namespace ProjectOen.Core.Telemetry
{
    public sealed class CausalLink
    {
        public CausalLink(string cause, int causeDay, string tag, string effect, int effectDay)
        {
            Cause = cause;
            CauseDay = causeDay;
            Tag = tag;
            Effect = effect;
            EffectDay = effectDay;
        }

        /// <summary>Handlingen der satte tagget. Tom hvis kilden ikke blev registreret.</summary>
        public string Cause { get; }

        public int CauseDay { get; }
        public string Tag { get; }
        public string Effect { get; }
        public int EffectDay { get; }

        public bool HasKnownCause => Cause.Length > 0;
    }

    /// <summary>
    /// docs/04 afsnit 10: "Efterspilsrapporten viser aarsagskaeden. Spilleren skal kunne
    /// forstaa: 'Det skete, fordi vi valgte X tidligere.'"
    ///
    /// M4's gate i docs/12 er, at en tester kan forklare mindst \u00e9n forsinket konsekvens.
    /// Rapporten bygges udelukkende af event-journalen - der findes ingen sideloebende
    /// bogfoering, som kan komme ud af trit med det, der faktisk skete.
    /// </summary>
    public static class AfterActionReport
    {
        public static IReadOnlyList<CausalLink> BuildChains(IReadOnlyList<ScenarioEvent> journal)
        {
            // Foerste gang et tag blev sat, og af hvad.
            var tagOrigin = new Dictionary<string, CampTagAdded>();
            foreach (var tagged in journal.OfType<CampTagAdded>())
            {
                if (!tagOrigin.ContainsKey(tagged.Tag)) tagOrigin[tagged.Tag] = tagged;
            }

            var links = new List<CausalLink>();
            foreach (var triggered in journal.OfType<DelayedEventTriggered>())
            {
                if (triggered.RequiredTag.Length > 0 && tagOrigin.TryGetValue(triggered.RequiredTag, out var origin))
                {
                    links.Add(new CausalLink(origin.SourceActionId, origin.Day, triggered.RequiredTag,
                                             triggered.EventId, triggered.Day));
                }
                else
                {
                    links.Add(new CausalLink("", 0, triggered.RequiredTag, triggered.EventId, triggered.Day));
                }
            }
            return links;
        }

        /// <summary>Menneskelaesbare linjer. Ordlyden er UI'ets ansvar; formen er rapportens.</summary>
        public static IReadOnlyList<string> Explain(IReadOnlyList<ScenarioEvent> journal)
        {
            var lines = BuildChains(journal).Select(link => link.HasKnownCause
                ? $"Dag {link.EffectDay}: {link.Effect} — fordi I {link.Cause} på dag {link.CauseDay} ({link.Tag})."
                : $"Dag {link.EffectDay}: {link.Effect}.").ToList();

            // Stormen er scenariets udbetaling. Uden dens linjer forklarer rapporten
            // alt undtagen det, spillerne husker bedst.
            lines.AddRange(journal.OfType<StormComplicationTriggered>()
                .Select(s => $"Stormen: {s.ComplicationId} — udløst af {s.Reason}."));

            var concluded = journal.OfType<ScenarioConcluded>().LastOrDefault();
            if (concluded != null)
                lines.Add($"Udfald: {concluded.Verdict} ({string.Join(", ", concluded.Reasons)}).");

            return lines;
        }
    }
}
