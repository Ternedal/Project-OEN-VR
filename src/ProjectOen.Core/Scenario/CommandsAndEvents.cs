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

    public sealed class CompleteInteractionStepCommand : ScenarioCommand
    {
        public CompleteInteractionStepCommand(string commandId, int playerSlot, string actionId, OutcomeInput outcome)
            : base(commandId, playerSlot)
        {
            ActionId = actionId;
            Outcome = outcome;
        }

        public string ActionId { get; }
        public OutcomeInput Outcome { get; }
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
        public int Revision { get; internal set; }
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
        public CampTagAdded(string tag) => Tag = tag;
        public string Tag { get; }
    }

    public sealed class DelayedEventTriggered : ScenarioEvent
    {
        public DelayedEventTriggered(string eventId) => EventId = eventId;
        public string EventId { get; }
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
