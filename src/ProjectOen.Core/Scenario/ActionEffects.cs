#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Scenario
{
    /// <summary>Hvad et udfald goer ved verden. Kommer fra scenariodata, ikke fra kode.</summary>
    public sealed class ActionEffect
    {
        public ActionEffect(
            IDictionary<string, int>? resourceDeltas = null,
            IDictionary<string, int>? campDeltas = null,
            IEnumerable<string>? addTags = null,
            IEnumerable<string>? removeTags = null,
            int fatigueCost = 0)
        {
            ResourceDeltas = resourceDeltas ?? new Dictionary<string, int>();
            CampDeltas = campDeltas ?? new Dictionary<string, int>();
            AddTags = (addTags ?? Enumerable.Empty<string>()).ToList();
            RemoveTags = (removeTags ?? Enumerable.Empty<string>()).ToList();
            FatigueCost = fatigueCost;
        }

        public IDictionary<string, int> ResourceDeltas { get; }

        /// <summary>Noegler: shelterIntegrity, fireStrength, foodSecurity, signalProgress, campThreat.</summary>
        public IDictionary<string, int> CampDeltas { get; }

        public IReadOnlyList<string> AddTags { get; }
        public IReadOnlyList<string> RemoveTags { get; }
        public int FatigueCost { get; }

        /// <summary>
        /// docs/04 afsnit 9: "Fejl med fremdrift" - resultatet er aldrig "ingen effekt".
        /// Et tomt udfald er en content-fejl, ikke en gyldig balancering.
        /// </summary>
        public bool IsEmpty =>
            ResourceDeltas.Count == 0 && CampDeltas.Count == 0
            && AddTags.Count == 0 && RemoveTags.Count == 0 && FatigueCost == 0;
    }

    /// <summary>
    /// Opslagstabel: handling + udfaldstier -> effekt. Retningen er \u00e9nvejs.
    /// Udfaldet vaelger effekten; effekten kan aldrig aendre udfaldet.
    /// </summary>
    public sealed class EffectTable
    {
        readonly Dictionary<string, Dictionary<OutcomeTier, ActionEffect>> _table =
            new Dictionary<string, Dictionary<OutcomeTier, ActionEffect>>(StringComparer.Ordinal);

        public void Set(string actionId, OutcomeTier tier, ActionEffect effect)
        {
            if (!_table.TryGetValue(actionId, out var perTier))
            {
                perTier = new Dictionary<OutcomeTier, ActionEffect>();
                _table[actionId] = perTier;
            }
            perTier[tier] = effect;
        }

        public ActionEffect? Lookup(string actionId, OutcomeTier tier) =>
            _table.TryGetValue(actionId, out var perTier) && perTier.TryGetValue(tier, out var effect)
                ? effect : null;

        public IEnumerable<string> Actions => _table.Keys;

        /// <summary>
        /// Hver handling skal daekke alle fire tiers, og ingen af dem maa vaere tom.
        /// Kaldes ved indlaesning - en manglende FailForward-effekt opdages ellers
        /// foerst, naar to spillere staar og undrer sig over, at intet skete.
        /// </summary>
        public IReadOnlyList<string> Validate()
        {
            var problems = new List<string>();
            foreach (var action in _table.Keys.OrderBy(k => k, StringComparer.Ordinal))
            {
                foreach (OutcomeTier tier in Enum.GetValues(typeof(OutcomeTier)))
                {
                    var effect = Lookup(action, tier);
                    if (effect == null)
                        problems.Add($"{action}: mangler effekt for {tier}.");
                    else if (effect.IsEmpty)
                        problems.Add($"{action}/{tier}: tom effekt. docs/04 afsnit 9 forbyder 'ingen effekt'.");
                }
            }
            return problems;
        }
    }

    public sealed class ResourceChanged : ScenarioEvent
    {
        public ResourceChanged(string key, int delta, int newValue)
        {
            Key = key;
            Delta = delta;
            NewValue = newValue;
        }

        public string Key { get; }
        public int Delta { get; }
        public int NewValue { get; }
    }

    public sealed class CampChanged : ScenarioEvent
    {
        public CampChanged(string key, int delta, int newValue)
        {
            Key = key;
            Delta = delta;
            NewValue = newValue;
        }

        public string Key { get; }
        public int Delta { get; }
        public int NewValue { get; }
    }

    public static class EffectApplier
    {
        public const int CampMin = 0;
        public const int CampMax = 100;

        /// <param name="sourceId">
        /// Hvad der forAarsagede effekten - en handling eller en stormkomplikation.
        /// Uden den kan efterspilsrapporten ikke pege paa en aarsag.
        /// </param>
        public static IReadOnlyList<ScenarioEvent> Apply(ScenarioState state, ActionEffect effect, int[] participants,
                                                         string sourceId = "")
        {
            var events = new List<ScenarioEvent>();

            foreach (var pair in effect.ResourceDeltas.OrderBy(p => p.Key, StringComparer.Ordinal))
            {
                var current = state.Resources.TryGetValue(pair.Key, out var v) ? v : 0;
                // Ressourcer kan ikke gaa i minus. En handling der koster mere,
                // end der findes, bruger hvad der er - den skaber ikke gaeld.
                var updated = Math.Max(0, current + pair.Value);
                state.Resources[pair.Key] = updated;
                events.Add(new ResourceChanged(pair.Key, updated - current, updated));
            }

            foreach (var pair in effect.CampDeltas.OrderBy(p => p.Key, StringComparer.Ordinal))
            {
                var current = Read(state.Camp, pair.Key);
                var updated = Math.Min(CampMax, Math.Max(CampMin, current + pair.Value));
                Write(state.Camp, pair.Key, updated);
                events.Add(new CampChanged(pair.Key, updated - current, updated));
            }

            foreach (var slot in participants)
            {
                if (slot < 0 || slot >= state.Players.Length) continue;
                state.Players[slot].Fatigue = Math.Min(100, Math.Max(0, state.Players[slot].Fatigue + effect.FatigueCost));
            }

            foreach (var tag in effect.RemoveTags) state.Tags.Remove(tag);

            // Symmetrisk med RemoveTags. Tidligere tilfoejede applier'en ikke tags,
            // saa en effekt anvendt uden for direktoren tabte dem stiltiende.
            foreach (var tag in effect.AddTags)
            {
                if (state.Tags.Add(tag))
                    events.Add(new CampTagAdded(tag, sourceId, state.Day));
            }

            return events;
        }

        static int Read(CampState camp, string key) => key switch
        {
            "shelterIntegrity" => camp.ShelterIntegrity,
            "fireStrength" => camp.FireStrength,
            "foodSecurity" => camp.FoodSecurity,
            "signalProgress" => camp.SignalProgress,
            "campThreat" => camp.CampThreat,
            _ => throw new InvalidOperationException($"Ukendt lejrfelt '{key}'.")
        };

        static void Write(CampState camp, string key, int value)
        {
            switch (key)
            {
                case "shelterIntegrity": camp.ShelterIntegrity = value; break;
                case "fireStrength": camp.FireStrength = value; break;
                case "foodSecurity": camp.FoodSecurity = value; break;
                case "signalProgress": camp.SignalProgress = value; break;
                case "campThreat": camp.CampThreat = value; break;
                default: throw new InvalidOperationException($"Ukendt lejrfelt '{key}'.");
            }
        }
    }
}
