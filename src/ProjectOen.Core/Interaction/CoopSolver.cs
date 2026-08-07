using System;
using ProjectOen.Core.Numerics;

namespace ProjectOen.Core.Interaction
{
    /// <summary>Tilstande fra docs/07 afsnit 8.</summary>
    public enum CoopObjectPhase
    {
        Idle, HeldByOne, HeldByBoth, Stabilizing, LockedToTarget, Released, Failed
    }

    public sealed class CoopSolverConfig
    {
        /// <summary>Maks lineaer hastighed. ADR-012: styret bevaegelse frem for raa kraftsimulation.</summary>
        public double MaxLinearSpeed { get; set; } = 2.0;

        /// <summary>0-1. Hoejere = objektet foelger haenderne taettere, men jitter slaar mere igennem.</summary>
        public double Responsiveness { get; set; } = 0.35;

        /// <summary>Med \u00e9n haand er objektet tungere og mere daempet - det er hele pointen med coop.</summary>
        public double SingleHandResponsivenessFactor { get; set; } = 0.4;

        /// <summary>
        /// Hastighedsloftet skal OGSAA saenkes ved \u00e9n haand. Uden det er de to tilstande
        /// identiske, naar objektet er langt fra haanden: loftet klipper begge til samme
        /// skridt, og "tung kasse kraever to spillere" holder kun taet paa maalet.
        /// Fundet ved test, ikke ved gennemlaesning - se docs/33.
        /// </summary>
        public double SingleHandSpeedFactor { get; set; } = 0.4;

        /// <summary>Objektets naturlige gribeafstand i meter.</summary>
        public double GripSpan { get; set; } = 0.8;

        /// <summary>Hvor meget gribeafstanden maa afvige, foer kvaliteten begynder at falde.</summary>
        public double GripTolerance { get; set; } = 0.25;

        /// <summary>Hvor hurtigt kvaliteten falder ved daarligt greb. Bevidst langsom, jf. docs/04 afsnit 7.</summary>
        public double QualityDecayPerSecond { get; set; } = 0.35;

        public double QualityRecoveryPerSecond { get; set; } = 0.5;
    }

    public readonly struct CoopStep
    {
        public CoopStep(Vec3 position, double quality, double gripError)
        {
            Position = position;
            Quality = quality;
            GripError = gripError;
        }

        public Vec3 Position { get; }

        /// <summary>0-1. Fodes videre som PhysicalExecution i OutcomeInput.</summary>
        public double Quality { get; }

        /// <summary>Afvigelse fra den naturlige gribeafstand i meter. 0 = perfekt.</summary>
        public double GripError { get; }
    }

    /// <summary>
    /// Kinematisk coop-solver. ADR-012 og docs/07 afsnit 8: netvaerket sender hand targets
    /// og quality samples, ikke raa kraefter. Objektet loeses mod et daempet midtpunkt med
    /// hastighedsloft, saa to klienter kan naa samme resultat uden fysik-desync.
    ///
    /// Ren C# med vilje. Solverens opfoersel - jitter, gribefejl, kvalitetsfald - kan
    /// dermed testes uden headset, hvilket er det eneste sted i coop-interaktionen,
    /// hvor det overhovedet er muligt.
    /// </summary>
    public sealed class CoopSolver
    {
        readonly CoopSolverConfig _config;

        public CoopSolver(CoopSolverConfig? config = null) => _config = config ?? new CoopSolverConfig();

        public Vec3 Position { get; private set; }
        public double Quality { get; private set; } = 1.0;
        public CoopObjectPhase Phase { get; private set; } = CoopObjectPhase.Idle;

        public void Reset(Vec3 position)
        {
            Position = position;
            Quality = 1.0;
            Phase = CoopObjectPhase.Idle;
        }

        /// <param name="left">Venstre spillers hand target, eller null hvis der ikke gribes.</param>
        /// <param name="right">Hoejre spillers hand target, eller null.</param>
        public CoopStep Step(Vec3? left, Vec3? right, double deltaTime)
        {
            if (deltaTime <= 0) throw new ArgumentOutOfRangeException(nameof(deltaTime));

            double gripError = 0;
            Vec3 desired;
            double responsiveness;
            double speedCeiling = _config.MaxLinearSpeed;

            if (left.HasValue && right.HasValue)
            {
                Phase = CoopObjectPhase.HeldByBoth;
                desired = Vec3.Midpoint(left.Value, right.Value);
                responsiveness = _config.Responsiveness;

                var span = Vec3.Distance(left.Value, right.Value);
                gripError = Math.Abs(span - _config.GripSpan);
            }
            else if (left.HasValue || right.HasValue)
            {
                Phase = CoopObjectPhase.HeldByOne;
                desired = left ?? right!.Value;
                responsiveness = _config.Responsiveness * _config.SingleHandResponsivenessFactor;
                speedCeiling *= _config.SingleHandSpeedFactor;

                // \u00c9n haand kan ikke holde gribeafstanden - det taeller som halv tolerance-overskridelse.
                gripError = _config.GripTolerance;
            }
            else
            {
                Phase = CoopObjectPhase.Released;
                return new CoopStep(Position, Quality, 0);
            }

            // Daempet traek mod maalet, derefter hastighedsloft. Loftet er det, der
            // holder jitter fra to klienter ude af resultatet.
            var delta = (desired - Position) * responsiveness;
            delta = delta.ClampMagnitude(speedCeiling * deltaTime);
            Position += delta;

            // docs/04 afsnit 7: "Hvis A mister stabiliteten, falder kvalitet gradvist
            // frem for at nulstille." Derfor et lineaert fald over tid, aldrig et spring.
            var overshoot = Math.Max(0, gripError - _config.GripTolerance);
            if (overshoot > 0)
            {
                var severity = Math.Min(1.0, overshoot / Math.Max(_config.GripTolerance, 1e-6));
                Quality -= _config.QualityDecayPerSecond * severity * deltaTime;
            }
            else if (Phase == CoopObjectPhase.HeldByBoth)
            {
                Quality += _config.QualityRecoveryPerSecond * deltaTime;
            }

            Quality = Clamp01(Quality);
            return new CoopStep(Position, Quality, gripError);
        }

        public void LockToTarget() => Phase = CoopObjectPhase.LockedToTarget;
        public void Fail() => Phase = CoopObjectPhase.Failed;

        static double Clamp01(double v) => v < 0 ? 0 : v > 1 ? 1 : v;
    }
}
