#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Scenario;

namespace ProjectOen.Core.Persistence
{
    /// <summary>
    /// docs/06 §9: checkpoint er et immutable snapshot, ikke en kontinuerlig fysik-save.
    ///
    /// Feltnavnene og strukturen følger schemas/savegame.schema.json, som har
    /// additionalProperties:false. Alt der ikke har et navngivet felt i skemaet -
    /// plan, behandlede command-IDs, lejrstatus - ligger i sharedState, som skemaet
    /// bevidst lader være et frit objekt.
    ///
    /// Det, der gør snapshottet noget værd, er ikke serialiseringen. Det er, at
    /// HandledCommands og eventkøens Fired-flag følger med: uden dem ville et
    /// checkpoint-resume udløse forsinkede events igen, og gentagne commands efter
    /// reconnect ville tælle to gange. Det er præcis SAVE-001 i docs/13.
    /// </summary>
    public static class ScenarioSnapshot
    {
        public const int SchemaVersion = 1;

        public static IDictionary<string, object?> Capture(
            ScenarioState state, int protocolVersion, string contentVersion, int scenarioVersion, string checkpointId)
        {
            var save = new Dictionary<string, object?>
            {
                ["schemaVersion"] = (long)SchemaVersion,
                ["protocolVersion"] = (long)protocolVersion,
                ["contentVersion"] = contentVersion,
                ["scenarioId"] = state.ScenarioId,
                ["scenarioVersion"] = (long)scenarioVersion,
                ["seed"] = (long)state.Seed,
                ["checkpointId"] = checkpointId,
                ["phase"] = state.Phase.ToString(),
                ["revision"] = (long)state.Revision,

                ["sharedState"] = new Dictionary<string, object?>
                {
                    ["day"] = (long)state.Day,
                    ["planLocked"] = state.PlanLocked,
                    ["resources"] = state.Resources.ToDictionary(p => p.Key, p => (object?)(long)p.Value),
                    ["plan"] = state.Plan.ToDictionary(p => p.Key, p => (object?)(long)p.Value),
                    ["camp"] = new Dictionary<string, object?>
                    {
                        ["shelterIntegrity"] = (long)state.Camp.ShelterIntegrity,
                        ["fireStrength"] = (long)state.Camp.FireStrength,
                        ["foodSecurity"] = (long)state.Camp.FoodSecurity,
                        ["signalProgress"] = (long)state.Camp.SignalProgress,
                        ["campThreat"] = (long)state.Camp.CampThreat,
                    },
                    // Uden denne liste taeller en gentaget command to gange efter reconnect.
                    ["handledCommands"] = state.HandledCommands.OrderBy(c => c, StringComparer.Ordinal)
                                               .Select(c => (object?)c).ToList(),
                },

                ["playerStates"] = state.Players.Select(p => (object?)new Dictionary<string, object?>
                {
                    ["playerSlot"] = (long)p.Slot,
                    ["health"] = (long)p.Health,
                    ["fatigue"] = (long)p.Fatigue,
                    ["injuries"] = p.Injuries.Select(i => (object?)i).ToList(),
                }).ToList(),

                ["tags"] = state.Tags.OrderBy(t => t, StringComparer.Ordinal).Select(t => (object?)t).ToList(),

                ["eventQueue"] = state.EventQueue.Select(e => (object?)new Dictionary<string, object?>
                {
                    ["eventId"] = e.EventId,
                    ["sourceCommandId"] = e.SourceCommandId,
                    ["triggerOnDay"] = (long)e.TriggerOnDay,
                    ["triggerPhase"] = e.TriggerPhase.ToString(),
                    ["requiredTag"] = e.RequiredTag,
                    // Fired er hele forskellen mellem "udloest \u00e9n gang" og "udloest igen ved resume".
                    ["fired"] = e.Fired,
                }).ToList(),

                ["completedActions"] = state.CompletedActions.Select(a => (object?)a).ToList(),
            };

            SaveChecksum.Stamp(save);
            return save;
        }

        public static ScenarioState Restore(IDictionary<string, object?> save)
        {
            if (!SaveChecksum.Verify(save))
                throw new InvalidOperationException("Checksummen matcher ikke. Snapshottet afvises frem for at indlaese korrupt state.");

            var schema = ToInt(save["schemaVersion"]);
            if (schema != SchemaVersion)
                throw new InvalidOperationException($"Save schema {schema} kan ikke indlaeses af version {SchemaVersion}. Migrator kraeves - docs/10.");

            var shared = Map(save["sharedState"]);
            var state = new ScenarioState((string)save["scenarioId"]!, ToInt(save["seed"]))
            {
                Phase = (ScenarioPhase)Enum.Parse(typeof(ScenarioPhase), (string)save["phase"]!),
                Day = ToInt(shared["day"]),
                Revision = ToInt(save["revision"]),
                PlanLocked = (bool)shared["planLocked"]!,
            };

            foreach (var pair in Map(shared["resources"])) state.Resources[pair.Key] = ToInt(pair.Value);
            foreach (var pair in Map(shared["plan"])) state.Plan[pair.Key] = ToInt(pair.Value);

            var camp = Map(shared["camp"]);
            state.Camp.ShelterIntegrity = ToInt(camp["shelterIntegrity"]);
            state.Camp.FireStrength = ToInt(camp["fireStrength"]);
            state.Camp.FoodSecurity = ToInt(camp["foodSecurity"]);
            state.Camp.SignalProgress = ToInt(camp["signalProgress"]);
            state.Camp.CampThreat = ToInt(camp["campThreat"]);

            foreach (var handled in List(shared["handledCommands"])) state.HandledCommands.Add((string)handled!);
            foreach (var tag in List(save["tags"])) state.Tags.Add((string)tag!);
            foreach (var action in List(save["completedActions"])) state.CompletedActions.Add((string)action!);

            foreach (var raw in List(save["playerStates"]))
            {
                var p = Map(raw);
                var slot = ToInt(p["playerSlot"]);
                var player = state.Players[slot];
                player.Health = ToInt(p["health"]);
                player.Fatigue = ToInt(p["fatigue"]);
                foreach (var injury in List(p["injuries"])) player.AddInjury((string)injury!);
            }

            foreach (var raw in List(save["eventQueue"]))
            {
                var e = Map(raw);
                var scheduled = new ScheduledEvent(
                    (string)e["eventId"]!,
                    (string)e["sourceCommandId"]!,
                    ToInt(e["triggerOnDay"]),
                    (ScenarioPhase)Enum.Parse(typeof(ScenarioPhase), (string)e["triggerPhase"]!),
                    (string)e["requiredTag"]!)
                {
                    Fired = (bool)e["fired"]!,
                };
                state.EventQueue.Add(scheduled);
            }

            return state;
        }

        static IDictionary<string, object?> Map(object? value) =>
            value as IDictionary<string, object?>
            ?? throw new InvalidOperationException("Forventede et objekt i snapshottet.");

        static IEnumerable<object?> List(object? value) =>
            value as IEnumerable<object?>
            ?? throw new InvalidOperationException("Forventede en liste i snapshottet.");

        static int ToInt(object? value) => value switch
        {
            long l => (int)l,
            int i => i,
            double d => (int)d,
            _ => throw new InvalidOperationException($"Kunne ikke laese heltal af {value?.GetType().Name ?? "null"}.")
        };
    }
}
