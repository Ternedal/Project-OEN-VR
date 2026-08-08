#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Scenario
{
    /// <summary>Scenariofaser fra docs/06 afsnit 5. Kun ScenarioDirector maa skifte mellem dem.</summary>
    public enum ScenarioPhase
    {
        Intro, Dawn, Planning, ResolvePlan, ActionSequence, Dusk, Night, Storm, Signal, Epilogue
    }

    /// <summary>Lejrens tilstand. docs/04 afsnit 6: "Lejren er den faelles karakter."</summary>
    public sealed class CampState
    {
        public int ShelterIntegrity { get; set; }
        public int FireStrength { get; set; }
        public int FoodSecurity { get; set; }
        public int SignalProgress { get; set; }
        public int CampThreat { get; set; }

        public CampState Clone() => new CampState
        {
            ShelterIntegrity = ShelterIntegrity,
            FireStrength = FireStrength,
            FoodSecurity = FoodSecurity,
            SignalProgress = SignalProgress,
            CampThreat = CampThreat,
        };
    }

    public sealed class PlayerState
    {
        public PlayerState(int slot)
        {
            Slot = slot;
            Health = 100;
            Fatigue = 0;
            Injuries = new List<string>();
        }

        public int Slot { get; }
        public int Health { get; set; }
        public int Fatigue { get; set; }
        public List<string> Injuries { get; }

        /// <summary>docs/04 afsnit 5: 0-3 aktive injury-tags. Fjerde ignoreres frem for at vokse ubegraenset.</summary>
        public bool AddInjury(string tag)
        {
            if (Injuries.Count >= 3 || Injuries.Contains(tag)) return false;
            Injuries.Add(tag);
            return true;
        }
    }

    /// <summary>
    /// En planlagt konsekvens. docs/04 afsnit 10: haendelser bruger tags og deadlines.
    /// CommandId baeres med, saa den samme planlaegning aldrig kan koe'es to gange -
    /// det er praecis den fejl, SAVE-001 i docs/13 leder efter.
    /// </summary>
    public sealed class ScheduledEvent
    {
        public ScheduledEvent(string eventId, string sourceCommandId, int triggerOnDay, ScenarioPhase triggerPhase, string requiredTag)
        {
            EventId = eventId;
            SourceCommandId = sourceCommandId;
            TriggerOnDay = triggerOnDay;
            TriggerPhase = triggerPhase;
            RequiredTag = requiredTag;
        }

        public string EventId { get; }
        public string SourceCommandId { get; }
        public int TriggerOnDay { get; }
        public ScenarioPhase TriggerPhase { get; }

        /// <summary>Tom streng = ingen tag-betingelse. Ellers skal tagget stadig vaere aktivt.</summary>
        public string RequiredTag { get; }

        public bool Fired { get; set; }

        public bool ShouldFire(int day, ScenarioPhase phase, IReadOnlyCollection<string> tags) =>
            !Fired
            && day == TriggerOnDay
            && phase == TriggerPhase
            && (RequiredTag.Length == 0 || tags.Contains(RequiredTag));
    }

    /// <summary>Den autoritative delte gameplaystate. docs/06 afsnit 7.</summary>
    public sealed class ScenarioState
    {
        public ScenarioState(string scenarioId, int seed)
        {
            ScenarioId = scenarioId;
            Seed = seed;
            Phase = ScenarioPhase.Intro;
            Day = 1;
            Revision = 0;
            Resources = new Dictionary<string, int>();
            Tags = new HashSet<string>(StringComparer.Ordinal);
            Camp = new CampState();
            Players = new[] { new PlayerState(0), new PlayerState(1) };
            EventQueue = new List<ScheduledEvent>();
            CompletedActions = new List<string>();
            HandledCommands = new HashSet<string>(StringComparer.Ordinal);
            Plan = new Dictionary<string, int>();
        }

        public string ScenarioId { get; }
        public int Seed { get; }
        public ScenarioPhase Phase { get; internal set; }
        public int Day { get; internal set; }

        /// <summary>docs/07 afsnit 11: monotont voksende. Alt der aendrer state skal bumpe den.</summary>
        public int Revision { get; internal set; }

        public Dictionary<string, int> Resources { get; }
        public HashSet<string> Tags { get; }
        public CampState Camp { get; }
        public PlayerState[] Players { get; }
        public List<ScheduledEvent> EventQueue { get; }
        public List<string> CompletedActions { get; }

        /// <summary>Command-IDs der allerede er behandlet. Grundlaget for idempotens (docs/07 afsnit 11).</summary>
        public HashSet<string> HandledCommands { get; }

        /// <summary>Dagens plan: action-ID -> antal indsatsmarkoerer.</summary>
        public Dictionary<string, int> Plan { get; }

        public bool PlanLocked { get; internal set; }

        public const int MarkersPerPlayer = 2;
        public const int TotalMarkers = MarkersPerPlayer * 2;

        public int MarkersUsed => Plan.Values.Sum();
        public int MarkersRemaining => TotalMarkers - MarkersUsed;
    }
}
