using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Scenario
{
    /// <summary>Et indlaest, kontrolleret scenario. Alt spillet skal bruge for at koere en session.</summary>
    public sealed class ScenarioDefinition
    {
        public ScenarioDefinition(string id, int supportedBuildProtocol, string contentVersion,
            IReadOnlyDictionary<string, ActionDefinition> actions, EffectTable effects,
            OutcomeThresholds thresholds,
            IReadOnlyList<ScenarioOutcomeRules.Rule> winRules,
            IReadOnlyList<ScenarioOutcomeRules.Rule> loseRules,
            ConditionTable conditions, StormCatalog storm)
        {
            Id = id;
            SupportedBuildProtocol = supportedBuildProtocol;
            ContentVersion = contentVersion;
            Actions = actions;
            Effects = effects;
            Thresholds = thresholds;
            WinRules = winRules;
            LoseRules = loseRules;
            Conditions = conditions;
            Storm = storm;
        }

        public string Id { get; }
        public int SupportedBuildProtocol { get; }
        public string ContentVersion { get; }
        public IReadOnlyDictionary<string, ActionDefinition> Actions { get; }
        public EffectTable Effects { get; }
        public OutcomeThresholds Thresholds { get; }
        public IReadOnlyList<ScenarioOutcomeRules.Rule> WinRules { get; }
        public IReadOnlyList<ScenarioOutcomeRules.Rule> LoseRules { get; }
        public ConditionTable Conditions { get; }
        public StormCatalog Storm { get; }

        public OutcomeResolver CreateResolver() => new OutcomeResolver(Thresholds);

        /// <summary>
        /// Startilstanden fra scenariodata. Uden den starter hver lejr paa nul,
        /// hvilket goer sejrsbetingelser uopnaaelige og udloeser alle stormens
        /// taerskelbetingelser fra foerste oejeblik.
        /// </summary>
        public InitialState Initial { get; internal set; } = new InitialState();

        public ScenarioState CreateState(int seed)
        {
            var state = new ScenarioState(Id, seed);
            state.Camp.ShelterIntegrity = Initial.ShelterIntegrity;
            state.Camp.FireStrength = Initial.FireStrength;
            state.Camp.FoodSecurity = Initial.FoodSecurity;
            state.Camp.SignalProgress = Initial.SignalProgress;
            state.Camp.CampThreat = Initial.CampThreat;
            foreach (var pair in Initial.Resources) state.Resources[pair.Key] = pair.Value;
            foreach (var tag in Initial.Tags) state.Tags.Add(tag);
            return state;
        }
    }

    public sealed class InitialState
    {
        public int ShelterIntegrity { get; set; }
        public int FireStrength { get; set; }
        public int FoodSecurity { get; set; }
        public int SignalProgress { get; set; }
        public int CampThreat { get; set; }
        public IDictionary<string, int> Resources { get; } = new Dictionary<string, int>();
        public IList<string> Tags { get; } = new List<string>();
    }

    public sealed class ActionDefinition
    {
        public ActionDefinition(string id, int effortCost, string primaryRole, string secondaryRole, IReadOnlyList<string> unlockedBy)
        {
            Id = id;
            EffortCost = effortCost;
            PrimaryRole = primaryRole;
            SecondaryRole = secondaryRole;
            UnlockedBy = unlockedBy;
        }

        public string Id { get; }
        public int EffortCost { get; }
        public string PrimaryRole { get; }
        public string SecondaryRole { get; }

        /// <summary>Event-IDs der skal vaere udloest, foer handlingen er tilgaengelig. Tom = altid.</summary>
        public IReadOnlyList<string> UnlockedBy { get; }

        public bool IsAvailable(IReadOnlyCollection<string> firedEvents) =>
            UnlockedBy.Count == 0 || UnlockedBy.All(firedEvents.Contains);
    }

    public sealed class ScenarioLoadException : Exception
    {
        public ScenarioLoadException(IReadOnlyList<string> problems)
            : base("Scenariet kunne ikke indlaeses:" + Environment.NewLine + string.Join(Environment.NewLine, problems))
            => Problems = problems;

        public IReadOnlyList<string> Problems { get; }
    }

    /// <summary>
    /// Bindeleddet, der manglede. Fem data-drevne systemer var bygget - effekter, regler,
    /// taerskler, action-katalog, kontraktvalidering - men der fandtes ingen vej fra JSON
    /// til et koerende scenario. Uden den her er "data-drevet" kun en paastand.
    ///
    /// Loaderen fejler HELE indlaesningen ved den mindste kontraktbrud og samler alle
    /// problemer foerst. Et scenario der starter halvt indlaest, fejler foerst midt i
    /// en session - og det er det dyreste tidspunkt at opdage en manglende effekt paa.
    /// </summary>
    public static class ScenarioLoader
    {
        public static ScenarioDefinition Load(IDictionary<string, object?> json, int buildProtocolVersion)
        {
            var problems = new ScenarioContract().Validate(json, buildProtocolVersion)
                .Select(v => v.ToString()).ToList();

            var actions = new Dictionary<string, ActionDefinition>(StringComparer.Ordinal);
            foreach (var entry in Enumerate(json, "actionCatalog"))
            {
                var id = Str(entry, "id");
                if (id.Length == 0) continue;
                actions[id] = new ActionDefinition(
                    id,
                    Int(entry, "effortCost", 1),
                    Str(entry, "primaryRole"),
                    Str(entry, "secondaryRole"),
                    entry.TryGetValue("unlockedBy", out var raw) && raw is IEnumerable<object?> list
                        ? list.OfType<string>().ToList()
                        : new List<string>());
            }

            var effects = new EffectTable();
            if (json.TryGetValue("effects", out var rawEffects) && rawEffects is IDictionary<string, object?> perAction)
            {
                foreach (var pair in perAction)
                {
                    if (!actions.ContainsKey(pair.Key))
                        problems.Add($"effects: '{pair.Key}' findes ikke i actionCatalog.");

                    if (!(pair.Value is IDictionary<string, object?> tiers)) continue;
                    foreach (var tierPair in tiers)
                    {
                        if (!TryParseTier(tierPair.Key, out var tier))
                        {
                            problems.Add($"effects/{pair.Key}: ukendt tier '{tierPair.Key}'.");
                            continue;
                        }
                        effects.Set(pair.Key, tier, ReadEffect(tierPair.Value));
                    }
                }
            }
            else
            {
                problems.Add("Scenariet mangler 'effects'.");
            }

            // Hver handling i kataloget skal have en komplet effekttabel - ikke kun
            // dem, der tilfaeldigvis er naevnt i effects.
            foreach (var missing in actions.Keys.Where(a => !effects.Actions.Contains(a)))
                problems.Add($"effects: mangler helt for '{missing}'.");
            problems.AddRange(effects.Validate());

            var conditions = ReadConditions(json);
            problems.AddRange(conditions.Validate());
            foreach (var injury in conditions.All)
            {
                foreach (var blocked in injury.BlocksActions.Where(a => !actions.ContainsKey(a)))
                    problems.Add($"conditions/{injury.Id}: blocksActions peger paa ukendt handling '{blocked}'.");
                foreach (var healer in injury.HealedBy.Where(a => !actions.ContainsKey(a)))
                    problems.Add($"conditions/{injury.Id}: healedBy peger paa ukendt handling '{healer}'.");
            }

            var storm = ReadStorm(json, problems);
            problems.AddRange(storm.Validate());

            var thresholds = ReadThresholds(json, problems);
            var winRules = ReadRules(json, "winRules");
            var loseRules = ReadRules(json, "loseRules");

            if (problems.Count > 0) throw new ScenarioLoadException(problems);

            var definition = new ScenarioDefinition(
                (string)json["id"]!,
                Convert.ToInt32(json["supportedBuildProtocol"]),
                json.TryGetValue("contentVersion", out var cv) ? cv as string ?? "" : "",
                actions, effects, thresholds, winRules, loseRules, conditions, storm);
            definition.Initial = ReadInitialState(json);
            return definition;
        }

        static InitialState ReadInitialState(IDictionary<string, object?> json)
        {
            var initial = new InitialState();
            if (!json.TryGetValue("initialState", out var raw) || !(raw is IDictionary<string, object?> map))
                return initial;

            if (map.TryGetValue("camp", out var rawCamp) && rawCamp is IDictionary<string, object?> camp)
            {
                initial.ShelterIntegrity = Int(camp, "shelterIntegrity", 0);
                initial.FireStrength = Int(camp, "fireStrength", 0);
                initial.FoodSecurity = Int(camp, "foodSecurity", 0);
                initial.SignalProgress = Int(camp, "signalProgress", 0);
                initial.CampThreat = Int(camp, "campThreat", 0);
            }
            foreach (var pair in ReadIntMap(map, "resources") ?? new Dictionary<string, int>())
                initial.Resources[pair.Key] = pair.Value;
            foreach (var tag in ReadStrings(map, "tags") ?? new List<string>())
                initial.Tags.Add(tag);
            return initial;
        }

        static StormCatalog ReadStorm(IDictionary<string, object?> json, List<string> problems)
        {
            var catalog = new StormCatalog();
            if (!json.TryGetValue("storm", out var raw) || !(raw is IDictionary<string, object?> map))
            {
                problems.Add("Scenariet mangler 'storm'.");
                return catalog;
            }

            if (map.TryGetValue("maxSimultaneous", out var ms) && ms != null)
                catalog.MaxSimultaneous = Convert.ToInt32(ms);

            if (!map.TryGetValue("complications", out var rawList) || !(rawList is IEnumerable<object?> list))
                return catalog;

            foreach (var entry in list.OfType<IDictionary<string, object?>>())
            {
                var conditions = new List<CampCondition>();
                if (entry.TryGetValue("campConditions", out var rawConds) && rawConds is IEnumerable<object?> conds)
                {
                    foreach (var c in conds.OfType<IDictionary<string, object?>>())
                    {
                        conditions.Add(new CampCondition(
                            Str(c, "field"),
                            Str(c, "comparison") == "atLeast" ? CampComparison.AtLeast : CampComparison.AtMost,
                            Int(c, "threshold", 0)));
                    }
                }

                catalog.Add(new StormComplication(
                    Str(entry, "id"),
                    Int(entry, "severity", 1),
                    ReadEffect(entry.TryGetValue("effect", out var e) ? e : null),
                    conditions,
                    ReadStrings(entry, "requiredTags"),
                    ReadStrings(entry, "forbiddenTags"),
                    entry.TryGetValue("isBaseline", out var b) && b is bool flag && flag));
            }
            return catalog;
        }

        static ConditionTable ReadConditions(IDictionary<string, object?> json)
        {
            var table = new ConditionTable();
            if (!json.TryGetValue("conditions", out var raw) || !(raw is IDictionary<string, object?> map))
                return table;

            if (map.TryGetValue("maxFatiguePenalty", out var mf) && mf != null)
                table.MaxFatiguePenalty = Convert.ToDouble(mf);

            if (map.TryGetValue("injuries", out var rawInjuries) && rawInjuries is IEnumerable<object?> list)
            {
                foreach (var entry in list.OfType<IDictionary<string, object?>>())
                {
                    table.Add(new InjuryDefinition(
                        Str(entry, "id"),
                        Dbl(entry, "penaltyContribution"),
                        ReadStrings(entry, "blocksActions"),
                        ReadStrings(entry, "healedBy")));
                }
            }
            return table;
        }

        static bool TryParseTier(string name, out OutcomeTier tier)
        {
            switch (name)
            {
                case "failForward": tier = OutcomeTier.FailForward; return true;
                case "partialWithCost": tier = OutcomeTier.PartialWithCost; return true;
                case "success": tier = OutcomeTier.Success; return true;
                case "criticalSuccess": tier = OutcomeTier.CriticalSuccess; return true;
                default: tier = OutcomeTier.FailForward; return false;
            }
        }

        static ActionEffect ReadEffect(object? raw)
        {
            if (!(raw is IDictionary<string, object?> map)) return new ActionEffect();
            return new ActionEffect(
                resourceDeltas: ReadIntMap(map, "resourceDeltas"),
                campDeltas: ReadIntMap(map, "campDeltas"),
                addTags: ReadStrings(map, "addTags"),
                removeTags: ReadStrings(map, "removeTags"),
                fatigueCost: Int(map, "fatigueCost", 0));
        }

        static OutcomeThresholds ReadThresholds(IDictionary<string, object?> json, List<string> problems)
        {
            if (!json.TryGetValue("outcomeThresholds", out var raw) || !(raw is IDictionary<string, object?> map))
                return OutcomeThresholds.Default;

            var partial = Dbl(map, "partial");
            var success = Dbl(map, "success");
            var critical = Dbl(map, "critical");

            if (!(partial < success && success < critical))
                problems.Add($"outcomeThresholds: skal vaere stigende, fik partial={partial}, success={success}, critical={critical}.");

            return new OutcomeThresholds(success, critical, partial);
        }

        static IReadOnlyList<ScenarioOutcomeRules.Rule> ReadRules(IDictionary<string, object?> json, string key) =>
            Enumerate(json, key)
                .Select(r => new ScenarioOutcomeRules.Rule(
                    Str(r, "type"),
                    r.Where(p => p.Key != "type").ToDictionary(p => p.Key, p => p.Value)))
                .ToList();

        static IEnumerable<IDictionary<string, object?>> Enumerate(IDictionary<string, object?> json, string key) =>
            json.TryGetValue(key, out var raw) && raw is IEnumerable<object?> list
                ? list.OfType<IDictionary<string, object?>>()
                : Enumerable.Empty<IDictionary<string, object?>>();

        static Dictionary<string, int>? ReadIntMap(IDictionary<string, object?> map, string key) =>
            map.TryGetValue(key, out var raw) && raw is IDictionary<string, object?> inner
                ? inner.ToDictionary(p => p.Key, p => Convert.ToInt32(p.Value))
                : null;

        static List<string>? ReadStrings(IDictionary<string, object?> map, string key) =>
            map.TryGetValue(key, out var raw) && raw is IEnumerable<object?> list
                ? list.OfType<string>().ToList()
                : null;

        static string Str(IDictionary<string, object?> map, string key) =>
            map.TryGetValue(key, out var v) ? v as string ?? "" : "";

        static int Int(IDictionary<string, object?> map, string key, int fallback) =>
            map.TryGetValue(key, out var v) && v != null ? Convert.ToInt32(v) : fallback;

        static double Dbl(IDictionary<string, object?> map, string key) =>
            map.TryGetValue(key, out var v) && v != null ? Convert.ToDouble(v) : 0;
    }
}
