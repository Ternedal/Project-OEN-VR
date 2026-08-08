#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Telemetry
{
    public sealed class PassivePeriod
    {
        public PassivePeriod(int playerSlot, string actionId, double start, double end)
        {
            PlayerSlot = playerSlot;
            ActionId = actionId;
            Start = start;
            End = end;
        }

        public int PlayerSlot { get; }
        public string ActionId { get; }
        public double Start { get; }
        public double End { get; }
        public double Duration => End - Start;
    }

    public sealed class ParticipationReport
    {
        public ParticipationReport(double totalActionSeconds, double bothActiveSeconds, IReadOnlyList<PassivePeriod> passivePeriods)
        {
            TotalActionSeconds = totalActionSeconds;
            BothActiveSeconds = bothActiveSeconds;
            PassivePeriods = passivePeriods;
        }

        public double TotalActionSeconds { get; }
        public double BothActiveSeconds { get; }
        public IReadOnlyList<PassivePeriod> PassivePeriods { get; }

        /// <summary>docs/13 UX-002: gate er >= 70 %.</summary>
        public double BothActiveShare => TotalActionSeconds <= 0 ? 0 : BothActiveSeconds / TotalActionSeconds;

        public double LongestPassiveSeconds => PassivePeriods.Count == 0 ? 0 : PassivePeriods.Max(p => p.Duration);

        /// <summary>docs/04 afsnit 8: designreglen er 12 sekunder.</summary>
        public const double DesignRuleSeconds = 12.0;

        /// <summary>docs/05 og docs/13: testgraensen er 20 sekunder.</summary>
        public const double TestThresholdSeconds = 20.0;

        public const double BothActiveGate = 0.70;

        public int PeriodsOverDesignRule => PassivePeriods.Count(p => p.Duration > DesignRuleSeconds);
        public int PeriodsOverTestThreshold => PassivePeriods.Count(p => p.Duration > TestThresholdSeconds);

        public bool MeetsGate => BothActiveShare >= BothActiveGate && PeriodsOverTestThreshold == 0;

        public string Summarize() =>
            $"begge aktive {BothActiveShare * 100:0.0}% (gate {BothActiveGate * 100:0}%) | " +
            $"laengste passive {LongestPassiveSeconds:0.0}s | " +
            $"over designregel({DesignRuleSeconds:0}s): {PeriodsOverDesignRule} | " +
            $"over testgraense({TestThresholdSeconds:0}s): {PeriodsOverTestThreshold} | " +
            (MeetsGate ? "GATE OK" : "GATE FEJLET");
    }

    /// <summary>
    /// CR-007. Reviewet fandt, at "begge spillere aktive" er produktets vigtigste loefte,
    /// men at graensen stod i tre dokumenter med to vaerdier og skulle afgoeres ved
    /// manuel observation. En playtest ville dermed blive afgjort af hukommelse.
    ///
    /// Her maales det. Interaktionslaget kalder Sample() pr. frame med hvem der bidrager;
    /// rapporten er et tal, ikke et indtryk. Manuel observation bruges stadig til HVORFOR.
    ///
    /// docs/04 afsnit 8 undtager sekvenser, som begge observerer ("dramatisk sekvens").
    /// Derfor findes ExcludeFromPassivity - men den skal saettes bevidst pr. sekvens,
    /// saa undtagelsen ikke kan bruges til at bortforklare et daarligt resultat.
    /// </summary>
    public sealed class ActiveParticipationTracker
    {
        readonly List<PassivePeriod> _passive = new List<PassivePeriod>();
        readonly double?[] _passiveSince = new double?[2];

        string _actionId = "";
        double _actionStart;
        double _lastSampleTime;
        bool _inAction;
        bool _excluded;

        public double TotalActionSeconds { get; private set; }
        public double BothActiveSeconds { get; private set; }

        public void BeginAction(string actionId, double timestamp, bool excludeFromPassivity = false)
        {
            if (_inAction) EndAction(timestamp);
            _actionId = actionId;
            _actionStart = timestamp;
            _lastSampleTime = timestamp;
            _inAction = true;
            _excluded = excludeFromPassivity;
            _passiveSince[0] = null;
            _passiveSince[1] = null;
        }

        /// <param name="playerActive">Indeks 0 og 1. True = spilleren bidrager aktivt lige nu.</param>
        public void Sample(double timestamp, bool player0Active, bool player1Active)
        {
            if (!_inAction) throw new InvalidOperationException("Sample() uden for en handling.");
            var dt = timestamp - _lastSampleTime;
            if (dt < 0) throw new ArgumentOutOfRangeException(nameof(timestamp), "Tiden gaar baglaens.");

            TotalActionSeconds += dt;
            if (player0Active && player1Active) BothActiveSeconds += dt;

            if (!_excluded)
            {
                Track(0, player0Active, timestamp);
                Track(1, player1Active, timestamp);
            }

            _lastSampleTime = timestamp;
        }

        void Track(int slot, bool active, double timestamp)
        {
            if (active)
            {
                if (_passiveSince[slot].HasValue)
                {
                    _passive.Add(new PassivePeriod(slot, _actionId, _passiveSince[slot]!.Value, timestamp));
                    _passiveSince[slot] = null;
                }
            }
            else if (!_passiveSince[slot].HasValue)
            {
                _passiveSince[slot] = _lastSampleTime;
            }
        }

        public void EndAction(double timestamp)
        {
            if (!_inAction) return;
            for (var slot = 0; slot < 2; slot++)
            {
                if (_passiveSince[slot].HasValue)
                {
                    _passive.Add(new PassivePeriod(slot, _actionId, _passiveSince[slot]!.Value, timestamp));
                    _passiveSince[slot] = null;
                }
            }
            _inAction = false;
        }

        public ParticipationReport Build() =>
            new ParticipationReport(TotalActionSeconds, BothActiveSeconds, _passive.ToList());
    }
}
