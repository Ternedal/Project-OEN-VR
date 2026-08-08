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

        readonly EffectTable? _effects;
        readonly ConditionTable _conditions;
        readonly IReadOnlyDictionary<string, ActionDefinition>? _actions;

        public ScenarioDirector(ScenarioState state, OutcomeResolver? outcomes = null, EffectTable? effects = null,
                                ConditionTable? conditions = null,
                                IReadOnlyDictionary<string, ActionDefinition>? actions = null)
        {
            State = state ?? throw new ArgumentNullException(nameof(state));
            _outcomes = outcomes ?? new OutcomeResolver();
            _effects = effects;
            _conditions = conditions ?? new ConditionTable();
            _actions = actions;
        }

        readonly StormCatalog? _storm;
        readonly IReadOnlyList<ScenarioOutcomeRules.Rule> _winRules = new List<ScenarioOutcomeRules.Rule>();
        readonly IReadOnlyList<ScenarioOutcomeRules.Rule> _loseRules = new List<ScenarioOutcomeRules.Rule>();
        bool _concluded;

        /// <summary>
        /// Den normale vej: et indlaest scenario leverer alle regler paa én gang.
        /// Den granulaere constructor findes stadig, saa tests kan isolere ét system.
        /// </summary>
        public ScenarioDirector(ScenarioState state, ScenarioDefinition definition)
            : this(state, definition.CreateResolver(), definition.Effects, definition.Conditions, definition.Actions)
        {
            _storm = definition.Storm;
            _winRules = definition.WinRules;
            _loseRules = definition.LoseRules;
        }

        /// <summary>Ekstra modstand fra vejr og hAendelser. Saettes af scenariet, ikke af klienten.</summary>
        public double ScenarioPenaltyModifier { get; set; }

        public ScenarioVerdict Verdict { get; private set; } = ScenarioVerdict.InProgress;

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
                // Kun events der ikke allerede har faaet en revision af et Bump().
                // Tidligere overskrev vi dem alle med slutvaerdien, saa den per-event
                // revision, Bump() havde til formaal at give, gik tabt.
                if (e.Revision == 0) e.Revision = State.Revision;
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
            produced.Add(new PlanLocked(new Dictionary<string, int>(State.Plan)) { Revision = State.Revision });
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

            var blocked = State.Players.Any(p => ConditionModel.IsBlockedFor(p, _conditions, cmd.ActionId));
            if (blocked)
            {
                Reject(produced, cmd.CommandId, "BLOCKED_BY_INJURY",
                    $"En skade forhindrer {cmd.ActionId}. Behandl den foerst.");
                return;
            }

            // Kun de to maalte led kommer fra klienten. Resten udledes her.
            var effortCost = _actions != null && _actions.TryGetValue(cmd.ActionId, out var def) ? def.EffortCost : 1;
            var input = new OutcomeInput(
                preparation: ConditionModel.PreparationFor(State, cmd.ActionId, effortCost),
                physicalExecution: cmd.Execution.PhysicalExecution,
                cooperation: cmd.Execution.Cooperation,
                penalty: ConditionModel.PenaltyFor(State, _conditions, ScenarioPenaltyModifier));

            var score = _outcomes.Score(input);
            var tier = _outcomes.Tier(score);

            State.CompletedActions.Add(cmd.ActionId);
            Bump();
            produced.Add(new ActionResolved(cmd.ActionId, tier, score) { Revision = State.Revision });

            // Retningen er énvejs: udfaldet vaelger effekten. Effekten kan aldrig
            // aendre udfaldet, og der findes derfor ingen vej tilbage fra verden
            // til scoren - det er dét, der holder resultatet forudsigeligt for spillerne.
            var effect = _effects?.Lookup(cmd.ActionId, tier);
            if (effect != null)
            {
                // Applier'en ejer hele effekten inkl. tags, saa der findes én vej ind
                // i state og ét journaliseringspunkt.
                foreach (var e in EffectApplier.Apply(State, effect, new[] { 0, 1 }, cmd.ActionId))
                {
                    Bump();
                    e.Revision = State.Revision;
                    produced.Add(e);
                }
            }

            // En gennemfoert behandling fjerner de skader, den helbreder.
            foreach (var healed in ConditionModel.ApplyHealing(State, _conditions, cmd.ActionId))
            {
                Bump();
                produced.Add(new InjuryHealed(healed, cmd.ActionId) { Revision = State.Revision });
            }
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
        /// <param name="sourceActionId">Handlingen der satte tagget. Baeres med, saa efterspilsrapporten kan pege paa en aarsag.</param>
        /// <param name="produced">
        /// Naar den er sat, er vi midt i Submit(), som journaliserer til sidst. Journaliserer
        /// vi ogsaa her, ender eventet to gange i journalen - og efterspilsrapporten faar
        /// dubletter i aarsagskaeden. Der er praecis ét journaliseringspunkt pr. event.
        /// </param>
        public void AddTag(string tag, string sourceActionId = "", List<ScenarioEvent>? produced = null)
        {
            if (!State.Tags.Add(tag)) return;
            Bump();
            var evt = new CampTagAdded(tag, sourceActionId, State.Day);

            if (produced != null)
            {
                produced.Add(evt);   // Submit() saetter Revision og journaliserer.
                return;
            }

            evt.Revision = State.Revision;
            _journal.Add(evt);
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
            produced.Add(new PhaseChanged(from, to, State.Day) { Revision = State.Revision });

            // docs/06 afsnit 9 + docs/05: checkpoint ved dagens begyndelse og foer stormen.
            if (to == ScenarioPhase.Dawn || to == ScenarioPhase.Storm)
                produced.Add(new CheckpointCreated($"{to}_DAY{State.Day}"));

            FireDueEvents(produced);

            // Stormen laeser lejrens tilstand i det oejeblik, den bryder los.
            if (to == ScenarioPhase.Storm && _storm != null) ResolveStorm(produced);

            EvaluateVerdict(produced);
        }

        void ResolveStorm(List<ScenarioEvent> produced)
        {
            foreach (var selected in StormResolver.Select(State, _storm!))
            {
                Bump();
                produced.Add(new StormComplicationTriggered(selected.Complication.Id, selected.Reason) { Revision = State.Revision });

                foreach (var e in EffectApplier.Apply(State, selected.Complication.Effect, new[] { 0, 1 },
                                                      selected.Complication.Id))
                {
                    Bump();
                    e.Revision = State.Revision;
                    produced.Add(e);
                }
            }
        }

        void EvaluateVerdict(List<ScenarioEvent> produced)
        {
            if (_concluded || (_winRules.Count == 0 && _loseRules.Count == 0)) return;

            var result = ScenarioOutcomeRules.Evaluate(State, _winRules, _loseRules);
            if (result.Verdict == ScenarioVerdict.InProgress) return;

            _concluded = true;
            Verdict = result.Verdict;
            Bump();
            produced.Add(new ScenarioConcluded(result.Verdict, result.Reasons) { Revision = State.Revision });
        }

        void FireDueEvents(List<ScenarioEvent> produced)
        {
            foreach (var scheduled in State.EventQueue)
            {
                if (!scheduled.ShouldFire(State.Day, State.Phase, State.Tags)) continue;
                scheduled.Fired = true;
                Bump();
                produced.Add(new DelayedEventTriggered(scheduled.EventId, scheduled.RequiredTag, State.Day) { Revision = State.Revision });
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
