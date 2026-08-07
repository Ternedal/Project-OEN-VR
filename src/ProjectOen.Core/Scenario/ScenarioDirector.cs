using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Scenario
{
    /// <summary>
    /// docs/06 afsnit 5: "Kun ScenarioDirector maa skifte scenariofase. Andre systemer
    /// sender commands/events."
    ///
    /// Denne klasse er bevidst fri for Unity og Fusion. Netvaerkslaget kalder Submit()
    /// og publicerer de returnerede events - det er hele koblingen. docs/06 afsnit 11:
    /// "Gameplay maa ikke referere direkte til Photon-klasser."
    /// </summary>
    public sealed class ScenarioDirector
    {
        readonly OutcomeResolver _outcomes;
        readonly List<ScenarioEvent> _journal = new List<ScenarioEvent>();

        public ScenarioDirector(ScenarioState state, OutcomeResolver? outcomes = null)
        {
            State = state ?? throw new ArgumentNullException(nameof(state));
            _outcomes = outcomes ?? new OutcomeResolver();
        }

        public ScenarioState State { get; }

        /// <summary>Alle events i raekkefoelge. Grundlaget for UI, audio, save journal og telemetri.</summary>
        public IReadOnlyList<ScenarioEvent> Journal => _journal;

        static readonly ScenarioPhase[] DayCycle =
        {
            ScenarioPhase.Dawn, ScenarioPhase.Planning, ScenarioPhase.ResolvePlan,
            ScenarioPhase.ActionSequence, ScenarioPhase.Dusk, ScenarioPhase.Night
        };

        public IReadOnlyList<ScenarioEvent> Submit(ScenarioCommand command)
        {
            var produced = new List<ScenarioEvent>();

            // Idempotens (docs/07 afsnit 11). En gentaget command efter reconnect er
            // ikke en fejl - den er forventet, og den maa ikke taelle to gange.
            if (!State.HandledCommands.Add(command.CommandId))
                return produced;

            switch (command)
            {
                case PlaceEffortMarkerCommand place: Handle(place, produced); break;
                case ConfirmPlanCommand confirm: Handle(confirm, produced); break;
                case CompleteInteractionStepCommand step: Handle(step, produced); break;
                case ScheduleDelayedEventCommand schedule: Handle(schedule, produced); break;
                case AdvancePhaseCommand: Advance(produced); break;
                default:
                    Reject(produced, command.CommandId, "UNKNOWN_COMMAND", command.GetType().Name);
                    break;
            }

            foreach (var e in produced)
            {
                e.Revision = State.Revision;
                _journal.Add(e);
            }
            return produced;
        }

        void Handle(PlaceEffortMarkerCommand cmd, List<ScenarioEvent> produced)
        {
            if (State.Phase != ScenarioPhase.Planning)
            {
                Reject(produced, cmd.CommandId, "WRONG_PHASE", $"Markoerer kan kun placeres i Planning, ikke {State.Phase}.");
                return;
            }
            if (State.PlanLocked)
            {
                Reject(produced, cmd.CommandId, "PLAN_LOCKED", "Planen er allerede laast for denne dag.");
                return;
            }
            if (cmd.Markers < 1 || cmd.Markers > 2)
            {
                // docs/04 afsnit 3: 3+ markoerer er kun til saerlige scenariehandlinger og
                // bruges ikke i standardloopet. Reviewet anbefalede at fjerne kategorien.
                Reject(produced, cmd.CommandId, "MARKER_COUNT", "En handling modtager 1 eller 2 markoerer.");
                return;
            }

            var alreadyOnAction = State.Plan.TryGetValue(cmd.ActionId, out var existing) ? existing : 0;
            if (State.MarkersRemaining + alreadyOnAction < cmd.Markers)
            {
                Reject(produced, cmd.CommandId, "NO_MARKERS_LEFT",
                    $"Der er {State.MarkersRemaining} markoerer tilbage af {ScenarioState.TotalMarkers}.");
                return;
            }

            State.Plan[cmd.ActionId] = cmd.Markers;
            Bump();
        }

        void Handle(ConfirmPlanCommand cmd, List<ScenarioEvent> produced)
        {
            if (State.Phase != ScenarioPhase.Planning)
            {
                Reject(produced, cmd.CommandId, "WRONG_PHASE", $"Planen kan kun bekraeftes i Planning, ikke {State.Phase}.");
                return;
            }

            // FLOW-001 i docs/13: en spiller placerer sidste markoer mens den anden
            // bekraefter. Kun \u00e9n planversion maa laases.
            if (State.PlanLocked)
            {
                Reject(produced, cmd.CommandId, "ALREADY_LOCKED", "Planen er allerede laast.");
                return;
            }
            if (State.Plan.Count == 0)
            {
                Reject(produced, cmd.CommandId, "EMPTY_PLAN", "Planen er tom.");
                return;
            }

            State.PlanLocked = true;
            Bump();
            produced.Add(new PlanLocked(new Dictionary<string, int>(State.Plan)));
        }

        void Handle(CompleteInteractionStepCommand cmd, List<ScenarioEvent> produced)
        {
            if (State.Phase != ScenarioPhase.ActionSequence && State.Phase != ScenarioPhase.Storm)
            {
                Reject(produced, cmd.CommandId, "WRONG_PHASE", $"Handlinger udfoeres ikke i {State.Phase}.");
                return;
            }
            if (State.CompletedActions.Contains(cmd.ActionId))
            {
                // docs/07 afsnit 11: "Completed interaction step kan ikke taelles to gange."
                Reject(produced, cmd.CommandId, "ALREADY_COMPLETED", $"{cmd.ActionId} er allerede afsluttet.");
                return;
            }

            var score = _outcomes.Score(cmd.Outcome);
            var tier = _outcomes.Tier(score);

            State.CompletedActions.Add(cmd.ActionId);
            Bump();
            produced.Add(new ActionResolved(cmd.ActionId, tier, score));
        }

        void Handle(ScheduleDelayedEventCommand cmd, List<ScenarioEvent> produced)
        {
            // SAVE-001: samme planlaegning maa aldrig ende i koeen to gange, heller ikke
            // hvis commanden gentages efter et checkpoint-resume.
            if (State.EventQueue.Any(e => e.SourceCommandId == cmd.CommandId))
                return;

            State.EventQueue.Add(new ScheduledEvent(cmd.EventId, cmd.CommandId, cmd.TriggerOnDay, cmd.TriggerPhase, cmd.RequiredTag));
            Bump();
        }

        /// <param name="sourceActionId">Handlingen der satte tagget. Baeres med, saa efterspilsrapporten kan pege paa en aarsag.</param>
        public void AddTag(string tag, string sourceActionId = "", List<ScenarioEvent>? produced = null)
        {
            if (!State.Tags.Add(tag)) return;
            Bump();
            var evt = new CampTagAdded(tag, sourceActionId, State.Day) { Revision = State.Revision };
            _journal.Add(evt);
            produced?.Add(evt);
        }

        void Advance(List<ScenarioEvent> produced)
        {
            var from = State.Phase;
            var to = NextPhase(from, out var newDay);

            State.Phase = to;
            if (newDay) State.Day++;

            if (to == ScenarioPhase.Planning)
            {
                State.Plan.Clear();
                State.PlanLocked = false;
                State.CompletedActions.Clear();
            }

            Bump();
            produced.Add(new PhaseChanged(from, to, State.Day));

            // docs/06 afsnit 9 + docs/05: checkpoint ved dagens begyndelse og foer stormen.
            if (to == ScenarioPhase.Dawn || to == ScenarioPhase.Storm)
                produced.Add(new CheckpointCreated($"{to}_DAY{State.Day}"));

            FireDueEvents(produced);
        }

        void FireDueEvents(List<ScenarioEvent> produced)
        {
            foreach (var scheduled in State.EventQueue)
            {
                if (!scheduled.ShouldFire(State.Day, State.Phase, State.Tags)) continue;
                scheduled.Fired = true;
                Bump();
                produced.Add(new DelayedEventTriggered(scheduled.EventId, scheduled.RequiredTag, State.Day));
            }
        }

        ScenarioPhase NextPhase(ScenarioPhase current, out bool newDay)
        {
            newDay = false;
            switch (current)
            {
                case ScenarioPhase.Intro:
                    return ScenarioPhase.Dawn;
                case ScenarioPhase.Night:
                    // Dag 3's nat foerer ind i stormen; ellers ny dag.
                    if (State.Day >= 3) return ScenarioPhase.Storm;
                    newDay = true;
                    return ScenarioPhase.Dawn;
                case ScenarioPhase.Storm:
                    return ScenarioPhase.Signal;
                case ScenarioPhase.Signal:
                    return ScenarioPhase.Epilogue;
                case ScenarioPhase.Epilogue:
                    return ScenarioPhase.Epilogue;
                default:
                    var index = Array.IndexOf(DayCycle, current);
                    return index >= 0 && index < DayCycle.Length - 1 ? DayCycle[index + 1] : current;
            }
        }

        void Bump() => State.Revision++;

        void Reject(List<ScenarioEvent> produced, string commandId, string code, string message)
        {
            // En afvist command er behandlet: den maa ikke kunne "lykkes" ved gentagelse.
            produced.Add(new CommandRejected(commandId, code, message));
        }
    }
}
