#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Scenario
{
    public sealed class InjuryDefinition
    {
        public InjuryDefinition(string id, double penaltyContribution,
                                IEnumerable<string>? blocksActions = null,
                                IEnumerable<string>? healedBy = null)
        {
            Id = id;
            PenaltyContribution = penaltyContribution;
            BlocksActions = (blocksActions ?? Enumerable.Empty<string>()).ToList();
            HealedBy = (healedBy ?? Enumerable.Empty<string>()).ToList();
        }

        public string Id { get; }

        /// <summary>0-1. Laegges til modstanden i udfaldsformlen.</summary>
        public double PenaltyContribution { get; }

        /// <summary>Handlinger denne skade goer umulige for den ramte spiller.</summary>
        public IReadOnlyList<string> BlocksActions { get; }

        /// <summary>Handlinger der fjerner skaden.</summary>
        public IReadOnlyList<string> HealedBy { get; }
    }

    public sealed class ConditionTable
    {
        readonly Dictionary<string, InjuryDefinition> _injuries = new Dictionary<string, InjuryDefinition>(StringComparer.Ordinal);

        /// <summary>Traethed 0-100 bidrager op til denne vaerdi til modstanden.</summary>
        public double MaxFatiguePenalty { get; set; } = 0.20;

        public void Add(InjuryDefinition injury) => _injuries[injury.Id] = injury;

        public InjuryDefinition? Lookup(string id) => _injuries.TryGetValue(id, out var v) ? v : null;

        public IEnumerable<InjuryDefinition> All => _injuries.Values;

        public IReadOnlyList<string> Validate()
        {
            var problems = new List<string>();
            foreach (var injury in _injuries.Values.OrderBy(i => i.Id, StringComparer.Ordinal))
            {
                if (injury.PenaltyContribution < 0 || injury.PenaltyContribution > 1)
                    problems.Add($"{injury.Id}: penaltyContribution skal ligge mellem 0 og 1, var {injury.PenaltyContribution}.");

                // En skade uden vej ud er permanent. docs/04 afsnit 5 beskriver skader som
                // noget der kan behandles - en skade uden healedBy er en content-fejl,
                // ikke en svaer balancering.
                if (injury.HealedBy.Count == 0)
                    problems.Add($"{injury.Id}: mangler 'healedBy'. En skade uden vej ud er permanent.");
            }
            return problems;
        }
    }

    /// <summary>
    /// docs/07 afsnit 7: "Klienten sender intents, ikke faerdige resultater."
    ///
    /// Modstanden i udfaldsformlen bliver derfor UDLEDT af autoritativ state -
    /// skader, traethed og scenariemodstand - og ikke sendt med af klienten.
    /// Preparation udledes tilsvarende af planen: hvor mange indsatsmarkoerer
    /// spillerne faktisk lagde paa handlingen.
    ///
    /// Klienten kan kun rapportere det, den alene kan maale: hvor godt sekvensen
    /// blev udfoert fysisk, og hvor godt de to arbejdede sammen. Begge kommer fra
    /// coop-solverens quality samples.
    /// </summary>
    public static class ConditionModel
    {
        public static double PenaltyFor(ScenarioState state, ConditionTable conditions, double scenarioModifier = 0)
        {
            var injuryPenalty = state.Players
                .SelectMany(p => p.Injuries)
                .Select(conditions.Lookup)
                .Where(i => i != null)
                .Sum(i => i!.PenaltyContribution);

            var averageFatigue = state.Players.Average(p => p.Fatigue) / 100.0;
            var fatiguePenalty = averageFatigue * conditions.MaxFatiguePenalty;

            return Clamp01(injuryPenalty + fatiguePenalty + scenarioModifier);
        }

        /// <summary>Indsatsmarkoerer paa handlingen mod dens kostpris. To markoerer paa en 1-koster er over-investering, ikke en fejl.</summary>
        public static double PreparationFor(ScenarioState state, string actionId, int effortCost)
        {
            var placed = state.Plan.TryGetValue(actionId, out var m) ? m : 0;
            if (placed <= 0) return 0;
            return Clamp01(placed / (double)Math.Max(1, effortCost));
        }

        public static bool IsBlockedFor(PlayerState player, ConditionTable conditions, string actionId) =>
            player.Injuries
                .Select(conditions.Lookup)
                .Any(i => i != null && i!.BlocksActions.Contains(actionId));

        /// <summary>Fjerner de skader, en gennemfoert handling helbreder. Returnerer hvad der blev fjernet.</summary>
        public static IReadOnlyList<string> ApplyHealing(ScenarioState state, ConditionTable conditions, string actionId)
        {
            var healed = new List<string>();
            foreach (var player in state.Players)
            {
                var cured = player.Injuries
                    .Where(id => conditions.Lookup(id)?.HealedBy.Contains(actionId) == true)
                    .ToList();
                foreach (var id in cured)
                {
                    player.Injuries.Remove(id);
                    healed.Add(id);
                }
            }
            return healed;
        }

        static double Clamp01(double v) => v < 0 ? 0 : v > 1 ? 1 : v;
    }
}

namespace ProjectOen.Core.Scenario
{
    public sealed class InjuryHealed : ScenarioEvent
    {
        public InjuryHealed(string injuryId, string byActionId)
        {
            InjuryId = injuryId;
            ByActionId = byActionId;
        }

        public string InjuryId { get; }
        public string ByActionId { get; }
    }
}
