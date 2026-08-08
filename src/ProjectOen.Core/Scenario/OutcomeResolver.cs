#nullable enable

using System;

namespace ProjectOen.Core.Scenario
{
    public enum OutcomeTier
    {
        FailForward,        // docs/04 afsnit 9: "Fejl med fremdrift" - aldrig "ingen effekt"
        PartialWithCost,
        Success,
        CriticalSuccess
    }

    /// <summary>Input til udfaldsformlen. Alle led 0-1, saa vaegtene ligger \u00e9t sted.</summary>
    public struct OutcomeInput
    {
        public OutcomeInput(double preparation, double physicalExecution, double cooperation, double penalty)
        {
            Preparation = preparation;
            PhysicalExecution = physicalExecution;
            Cooperation = cooperation;
            Penalty = penalty;
        }

        public double Preparation { get; }
        public double PhysicalExecution { get; }
        public double Cooperation { get; }

        /// <summary>Samlet modstand: skade, vejr og event risk lagt sammen af kaldstedet.</summary>
        public double Penalty { get; }
    }

    public sealed class OutcomeThresholds
    {
        public OutcomeThresholds(double success, double critical, double partial)
        {
            Success = success;
            Critical = critical;
            Partial = partial;
        }

        public double Partial { get; }
        public double Success { get; }
        public double Critical { get; }

        /// <summary>
        /// Startvaerdier, kalibreret mod maalingen i OutcomeDistributionTests.
        /// De hoerer hjemme i scenariodata, ikke i kode - se docs/10.
        /// </summary>
        public static OutcomeThresholds Default => new OutcomeThresholds(success: 0.55, critical: 0.74, partial: 0.35);
    }

    /// <summary>
    /// Reviewets afsnit 2 (CR-anbefaling): den oprindelige formel havde otte additive led
    /// uden vaegte eller skala. Med otte led lander resultatet naesten altid midt i feltet,
    /// og "Delvis succes med omkostning" bliver det eneste udfald spillerne ser - hvilket
    /// laeses som "spillet straffer os uanset hvad".
    ///
    /// Denne udgave har fire led. Taerskler ligger i data, ikke i kode, saa balancering
    /// kan foregaa uden rebuild.
    /// </summary>
    public sealed class OutcomeResolver
    {
        readonly OutcomeThresholds _thresholds;

        public OutcomeResolver(OutcomeThresholds? thresholds = null) =>
            _thresholds = thresholds ?? OutcomeThresholds.Default;

        public const double WeightPreparation = 0.30;
        public const double WeightExecution = 0.45;
        public const double WeightCooperation = 0.25;

        /// <summary>
        /// Hvor meget modstand maksimalt kan traekke scoren ned. Bevidst under 1.0:
        /// da de positive led summerer til 1.0, ville en fuldvaegtet subtraktion goere
        /// penalty til det dominerende led og kollapse alle udfald til én kategori.
        /// Det blev maalt, ikke gaettet - se OutcomeDistributionTests.
        /// </summary>
        public const double MaxPenaltyInfluence = 0.35;

        /// <summary>Den rene praestation, foer modstand. 0-1.</summary>
        public double BaseScore(OutcomeInput input) =>
            WeightPreparation * Clamp01(input.Preparation)
          + WeightExecution * Clamp01(input.PhysicalExecution)
          + WeightCooperation * Clamp01(input.Cooperation);

        public double Score(OutcomeInput input) =>
            Clamp01(BaseScore(input) - Clamp01(input.Penalty) * MaxPenaltyInfluence);

        /// <summary>
        /// docs/04 afsnit 9: "Tilfaeldighed maa modificere omkostningen, men ikke slette
        /// en dygtigt gennemfoert VR-sekvens uden forklaring."
        ///
        /// Derfor er der et gulv: modstand kan hoejst traekke udfaldet ét trin ned fra
        /// det, den rene praestation fortjente. En perfekt udfoert sekvens kan koste dyrt,
        /// men kan aldrig ende som FailForward. Reglen er selve grunden til, at Resolve()
        /// findes i stedet for at kalde Tier(Score(...)) direkte.
        /// </summary>
        public OutcomeTier Resolve(OutcomeInput input)
        {
            var earned = Tier(BaseScore(input));
            var afterPenalty = Tier(Score(input));
            var floor = earned == OutcomeTier.FailForward ? OutcomeTier.FailForward : (OutcomeTier)((int)earned - 1);
            return afterPenalty < floor ? floor : afterPenalty;
        }

        public OutcomeTier Tier(double score)
        {
            if (score >= _thresholds.Critical) return OutcomeTier.CriticalSuccess;
            if (score >= _thresholds.Success) return OutcomeTier.Success;
            if (score >= _thresholds.Partial) return OutcomeTier.PartialWithCost;
            return OutcomeTier.FailForward;
        }

        static double Clamp01(double v) => v < 0 ? 0 : v > 1 ? 1 : v;
    }
}
