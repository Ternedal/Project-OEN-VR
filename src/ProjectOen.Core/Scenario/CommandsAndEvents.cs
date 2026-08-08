#nullable enable

using System.Collections.Generic;

namespace ProjectOen.Core.Scenario
{
    /// <summary>
    /// docs/07 afsnit 7: klienten sender intents, ikke faerdige resultater.
    /// Alle commands baerer et ID, saa gentagelse efter reconnect er gratis.
    /// </summary>
    public abstract class ScenarioCommand
    {
        protected ScenarioCommand(string commandId, int playerSlot)
        {
            CommandId = commandId;
            PlayerSlot = playerSlot;
        }

        public string CommandId { get; }
        public int PlayerSlot { get; }
    }

    public sealed class PlaceEffortMarkerCommand : ScenarioCommand
    {
        public PlaceEffortMarkerCommand(string commandId, int playerSlot, string actionId, int markers)
            : base(commandId, playerSlot)
        {
            ActionId = actionId;
            Markers = markers;
        }

        public string ActionId { get; }
        public int Markers { get; }
    }

    public sealed class ConfirmPlanCommand : ScenarioCommand
    {
        public ConfirmPlanCommand(string commandId, int playerSlot) : base(commandId, playerSlot) { }
    }

    /// <summary>
    /// docs/07 afsnit 7: klienten sender intents, ikke faerdige resultater.
    ///
    /// Derfor baerer commanden KUN det, klienten alene kan maale: hvor godt sekvensen
    /// blev udfoert fysisk, og hvor godt de to arbejdede sammen. Begge kommer fra
    /// coop-solverens quality samples. Preparation og Penalty udleder direktoren af
    /// autoritativ state - ellers ville klienten kunne fortaelle serveren, hvor haardt
    /// den skulle straffes.
    /// </summary>
    public sealed class CompleteInteractionStepCommand : ScenarioCommand
    {
        public CompleteInteractionStepCommand(string commandId, int playerSlot, string actionId, ExecutionSample execution)
            : base(commandId, playerSlot)
        {
            ActionId = actionId;
            Execution = execution;
        }

        public string ActionId { get; }
        public ExecutionSample Execution { get; }
    }

    /// <summary>Det maalte, ikke det vurderede. Begge vaerdier 0-1.</summary>
    public readonly struct ExecutionSample
    {
        public ExecutionSample(double physicalExecution, double cooperation)
        {
            PhysicalExecution = physicalExecution;
            Cooperation = cooperation;
        }

        public double PhysicalExecution { get; }
        public double Cooperation { get; }
    }

    public sealed class ScheduleDelayedEventCommand : ScenarioCommand
    {
        public ScheduleDelayedEventCommand(string commandId, int playerSlot, string eventId,
                                           int triggerOnDay, ScenarioPhase triggerPhase, string requiredTag)
            : base(commandId, playerSlot)
        {
            EventId = eventId;
            TriggerOnDay = triggerOnDay;
            TriggerPhase = triggerPhase;
            RequiredTag = requiredTag;
        }

        public string EventId { get; }
        public int TriggerOnDay { get; }
        public ScenarioPhase TriggerPhase { get; }
        public string RequiredTag { get; }
    }

    public sealed class AdvancePhaseCommand : ScenarioCommand
    {
        public AdvancePhaseCommand(string commandId, int playerSlot) : base(commandId, playerSlot) { }
    }

    // ---- Domaeneevents (docs/06 afsnit 6) ----

    public abstract class ScenarioEvent
    {
        /// <summary>
        /// Saettes af det Bump(), der ledsagede eventet. 0 = endnu ikke stemplet;
        /// Submit() giver da den aktuelle revision.
        /// </summary>
        public int Revision { get; set; }
    }

    public sealed class PlanLocked : ScenarioEvent
    {
        public PlanLocked(IReadOnlyDictionary<string, int> plan) => Plan = plan;
        public IReadOnlyDictionary<string, int> Plan { get; }
    }

    public sealed class ActionResolved : ScenarioEvent
    {
        public ActionResolved(string actionId, OutcomeTier tier, double score)
        {
            ActionId = actionId;
            Tier = tier;
            Score = score;
        }

        public string ActionId { get; }
        public OutcomeTier Tier { get; }
        public double Score { get; }
    }

    public sealed class CampTagAdded : ScenarioEvent
    {
        public CampTagAdded(string tag, string sourceActionId, int day)
        {
            Tag = tag;
            SourceActionId = sourceActionId;
            Day = day;
        }

        public string Tag { get; }

        /// <summary>Hvilken handling satte tagget. Uden proveniens kan aarsagskaeden i docs/04 afsnit 10 ikke bygges.</summary>
        public string SourceActionId { get; }

        public int Day { get; }
    }

    public sealed class DelayedEventTriggered : ScenarioEvent
    {
        public DelayedEventTriggered(string eventId, string requiredTag, int day)
        {
            EventId = eventId;
            RequiredTag = requiredTag;
            Day = day;
        }

        public string EventId { get; }

        /// <summary>Tagget der aabnede for eventet. Tom streng = ubetinget.</summary>
        public string RequiredTag { get; }

        public int Day { get; }
    }

    public sealed class PhaseChanged : ScenarioEvent
    {
        public PhaseChanged(ScenarioPhase from, ScenarioPhase to, int day)
        {
            From = from;
            To = to;
            Day = day;
        }

        public ScenarioPhase From { get; }
        public ScenarioPhase To { get; }
        public int Day { get; }
    }

    public sealed class CheckpointCreated : ScenarioEvent
    {
        public CheckpointCreated(string checkpointId) => CheckpointId = checkpointId;
        public string CheckpointId { get; }
    }

    /// <summary>Afvist command. Fejlen er data, ikke en exception - klienten skal kunne vise den.</summary>
    public sealed class CommandRejected : ScenarioEvent
    {
        public CommandRejected(string commandId, string code, string message)
        {
            CommandId = commandId;
            Code = code;
            Message = message;
        }

        public string CommandId { get; }
        public string Code { get; }
        public string Message { get; }
    }
}
