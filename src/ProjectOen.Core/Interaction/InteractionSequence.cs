#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Interaction
{
    // PO-040 — InteractionSequence.
    //
    // Den authorbare model for en fysisk coop-opgave (docs/04 afsnit 5, docs/05).
    // To spillere udfører en sekvens af trin i en primær/sekundær rollefordeling;
    // deres bidrag bliver til én score i [0,1]. Scoren fødes videre til
    // OutcomeResolver.Tier(score) -> OutcomeTier -> EffectTable, så udfaldet vælger
    // effekten (aldrig omvendt). Kvalitetsvægtningen (prep/tool/execution) er PO-041
    // og bygges ovenpå denne model senere; her er kun data + deterministisk resolve.

    /// <summary>Rollen et trin kræver. Primær driver opgaven, sekundær assisterer.</summary>
    public enum InteractionRole
    {
        Primary,
        Secondary,
    }

    /// <summary>Ét trin i en coop-opgave. Vægten bestemmer trinnets andel af scoren.</summary>
    public sealed class InteractionStep
    {
        public InteractionStep(string stepId, InteractionRole role, double weight)
        {
            if (string.IsNullOrWhiteSpace(stepId))
                throw new ArgumentException("stepId må ikke være tom.", nameof(stepId));
            StepId = stepId;
            Role = role;
            Weight = weight;
        }

        public string StepId { get; }
        public InteractionRole Role { get; }
        public double Weight { get; }
    }

    /// <summary>
    /// En hel coop-opgave. <see cref="ActionId"/> peger på samme handling som
    /// EffectTable, så score -> tier -> effekt hænger sammen.
    /// </summary>
    public sealed class InteractionSequence
    {
        public InteractionSequence(string actionId, IEnumerable<InteractionStep>? steps, bool requiresBothPlayers = true)
        {
            if (string.IsNullOrWhiteSpace(actionId))
                throw new ArgumentException("actionId må ikke være tom.", nameof(actionId));
            ActionId = actionId;
            Steps = (steps ?? Enumerable.Empty<InteractionStep>()).ToList();
            RequiresBothPlayers = requiresBothPlayers;
        }

        public string ActionId { get; }
        public IReadOnlyList<InteractionStep> Steps { get; }

        /// <summary>Er opgaven ægte coop? Hvis ja, kan én spiller alene ikke nå topudfaldet.</summary>
        public bool RequiresBothPlayers { get; }

        public double TotalWeight => Steps.Sum(s => s.Weight);

        /// <summary>
        /// Content-validering, i samme ånd som EffectTable.Validate(): en dårligt
        /// forfattet sekvens skal fanges ved indlæsning, ikke når to spillere står og
        /// undrer sig. Returnerer en (tom = OK) liste af problemer.
        /// </summary>
        public IReadOnlyList<string> Validate()
        {
            var problems = new List<string>();

            if (Steps.Count == 0)
            {
                problems.Add($"{ActionId}: sekvensen har ingen trin.");
                return problems;
            }

            foreach (var step in Steps)
            {
                if (step.Weight <= 0)
                    problems.Add($"{ActionId}/{step.StepId}: vægt skal være > 0 (var {step.Weight}).");
            }

            var duplicates = Steps.GroupBy(s => s.StepId, StringComparer.Ordinal)
                                  .Where(g => g.Count() > 1)
                                  .Select(g => g.Key);
            foreach (var dup in duplicates)
                problems.Add($"{ActionId}/{dup}: trin-id optræder mere end én gang.");

            if (!Steps.Any(s => s.Role == InteractionRole.Primary))
                problems.Add($"{ActionId}: ingen primær-trin — en opgave uden fører giver ikke mening.");

            if (RequiresBothPlayers && !Steps.Any(s => s.Role == InteractionRole.Secondary))
                problems.Add($"{ActionId}: markeret som coop, men har intet sekundær-trin at dele.");

            return problems;
        }
    }

    /// <summary>Et registreret bidrag: hvem gjorde hvilket trin, og hvor godt (0..1).</summary>
    public readonly struct StepContribution
    {
        public StepContribution(string stepId, int playerSlot, double quality)
        {
            StepId = stepId;
            PlayerSlot = playerSlot;
            Quality = quality;
        }

        public string StepId { get; }
        public int PlayerSlot { get; }
        public double Quality { get; }
    }

    /// <summary>Resultatet af en resolve. Scoren fødes til OutcomeResolver; tieren afgøres der.</summary>
    public sealed class InteractionResult
    {
        public InteractionResult(double score, bool bothPlayersActive, IReadOnlyCollection<int> contributingSlots)
        {
            Score = score;
            BothPlayersActive = bothPlayersActive;
            ContributingSlots = contributingSlots;
        }

        /// <summary>Vægtet kvalitet i [0,1]. 0 = intet lykkedes, 1 = alt perfekt.</summary>
        public double Score { get; }

        /// <summary>Bidrog begge spillere reelt? Grundlaget for UX-002 (begge aktive ≥70%).</summary>
        public bool BothPlayersActive { get; }

        public IReadOnlyCollection<int> ContributingSlots { get; }
    }

    public static class InteractionResolver
    {
        /// <summary>
        /// Loftet for en coop-opgave løst af én spiller alene. Svarer til CoopSolverens
        /// "gradvist kvalitetsfald frem for nulstilling": en solo-løsning fejler ikke,
        /// men kan højst blive PartialWithCost. Se docs/04 afsnit 5 om coop-præmissen.
        /// </summary>
        public const double CoopSoloCeiling = 0.5;

        /// <summary>
        /// Deterministisk: samme sekvens + samme bidrag giver samme score, uanset
        /// bidragenes rækkefølge. Manglende trin tælles som kvalitet 0 (fejl med
        /// fremdrift, ikke crash). Gentagne bidrag til samme trin: det bedste tæller.
        /// </summary>
        public static InteractionResult Resolve(InteractionSequence sequence, IEnumerable<StepContribution>? contributions)
        {
            if (sequence == null) throw new ArgumentNullException(nameof(sequence));

            // Bedste kvalitet pr. trin, og hvilke slots der reelt løftede noget.
            var bestQuality = new Dictionary<string, double>(StringComparer.Ordinal);
            var activeSlots = new SortedSet<int>();

            foreach (var c in contributions ?? Enumerable.Empty<StepContribution>())
            {
                var q = Clamp01(c.Quality);
                if (bestQuality.TryGetValue(c.StepId, out var prev))
                {
                    if (q > prev) bestQuality[c.StepId] = q;
                }
                else
                {
                    bestQuality[c.StepId] = q;
                }

                if (q > 0) activeSlots.Add(c.PlayerSlot);
            }

            double weighted = 0;
            double totalWeight = 0;
            foreach (var step in sequence.Steps)
            {
                var q = bestQuality.TryGetValue(step.StepId, out var v) ? v : 0.0;
                weighted += step.Weight * q;
                totalWeight += step.Weight;
            }

            var score = totalWeight > 0 ? weighted / totalWeight : 0.0;

            var bothActive = activeSlots.Contains(0) && activeSlots.Contains(1);
            if (sequence.RequiresBothPlayers && !bothActive)
                score = Math.Min(score, CoopSoloCeiling);

            return new InteractionResult(score, bothActive, activeSlots.ToList());
        }

        static double Clamp01(double value)
        {
            if (value < 0) return 0;
            if (value > 1) return 1;
            return value;
        }
    }
}
