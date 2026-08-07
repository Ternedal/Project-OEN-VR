using System;
using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// Evidens til OQ-008 ("Hvor meget randomness foeles fair?") og til reviewets
    /// indvending mod den oprindelige otte-leddede formel.
    ///
    /// Paastanden var: med otte additive led lander scoren naesten altid midt i feltet,
    /// og PartialWithCost bliver det eneste udfald spillerne ser. Her maales det
    /// i stedet for at blive diskuteret.
    /// </summary>
    public class OutcomeDistributionTests
    {
        readonly ITestOutputHelper _out;
        public OutcomeDistributionTests(ITestOutputHelper output) => _out = output;

        const int Runs = 20;
        const int ActionsPerRun = 12;

        static OutcomeInput SampleFour(Random rng, double skill, double penalty) =>
            new OutcomeInput(
                preparation: Clamp(skill + Gauss(rng, 0.12)),
                physicalExecution: Clamp(skill + Gauss(rng, 0.18)),
                cooperation: Clamp(skill + Gauss(rng, 0.15)),
                penalty: penalty);

        /// <summary>Den oprindelige formel: otte led, lige vaegt, ingen skala.</summary>
        static double ScoreEight(Random rng, double skill, double penalty)
        {
            double T() => Clamp(skill + Gauss(rng, 0.15));
            var positive = T() + T() + T() + T() + T();                    // prep, tool, role, exec, coop
            var negative = penalty + Clamp(Gauss(rng, 0.2) + 0.3) + Clamp(Gauss(rng, 0.2) + 0.3);
            return Clamp((positive - negative) / 5.0);
        }

        [Fact]
        public void Four_term_formula_produces_a_usable_spread_across_twenty_runs()
        {
            var resolver = new OutcomeResolver();
            var rng = new Random(20260807);

            var four = new Dictionary<OutcomeTier, int>();
            var eight = new Dictionary<OutcomeTier, int>();
            foreach (OutcomeTier t in Enum.GetValues(typeof(OutcomeTier)))
            {
                four[t] = 0;
                eight[t] = 0;
            }

            for (var run = 0; run < Runs; run++)
            {
                // Spillerne bliver bedre hen over de tre dage; modstanden stiger mod stormen.
                for (var i = 0; i < ActionsPerRun; i++)
                {
                    var skill = 0.45 + 0.30 * (i / (double)(ActionsPerRun - 1));
                    var penalty = 0.05 + 0.15 * (i / (double)(ActionsPerRun - 1));

                    four[resolver.Resolve(SampleFour(rng, skill, penalty))]++;
                    eight[resolver.Tier(ScoreEight(rng, skill, penalty))]++;
                }
            }

            var total = Runs * ActionsPerRun;
            _out.WriteLine($"{Runs} runs x {ActionsPerRun} handlinger = {total} udfald\n");
            _out.WriteLine("tier              4 led     8 led");
            foreach (OutcomeTier t in Enum.GetValues(typeof(OutcomeTier)))
                _out.WriteLine($"{t,-16} {four[t] * 100.0 / total,6:0.0}%  {eight[t] * 100.0 / total,6:0.0}%");

            var fourDominant = four.Values.Max() * 100.0 / total;
            var eightDominant = eight.Values.Max() * 100.0 / total;
            _out.WriteLine($"\nstoerste enkelt-tier: 4 led {fourDominant:0.0}%  |  8 led {eightDominant:0.0}%");

            // Gate 1: ingen enkelt kategori maa aede feltet. Sker det, er udfaldet
            // ikke information for spilleren - det er stoej.
            Assert.True(fourDominant < 70.0,
                $"Ét udfald daekker {fourDominant:0.0}% - formlen giver ikke spillerne brugbar feedback.");

            // Gate 2: alle fire tiers skal faktisk forekomme.
            Assert.All(four.Values, count => Assert.True(count > 0, "En udfaldskategori forekom aldrig."));

            // Gate 3 er bevidst FJERNET. Foerste maaling viste 4 led = 70,0 % og 8 led = 68,8 %:
            // antallet af led var ikke aarsagen. Klumpningen kom fra, at penalty blev
            // trukket fra med fuld vaegt fra en score, hvis positive led summerer til 1,0.
            // Reviewets CR-formulering ("otte additive led klumper") var derfor kun halvt
            // rigtig, og maalingen staar over formuleringen. Se docs/33.
        }

        [Fact]
        public void Weights_sum_to_one_so_a_perfect_run_without_penalty_is_a_critical_success()
        {
            Assert.Equal(1.0, OutcomeResolver.WeightPreparation + OutcomeResolver.WeightExecution + OutcomeResolver.WeightCooperation, 6);
            var resolver = new OutcomeResolver();
            Assert.Equal(OutcomeTier.CriticalSuccess, resolver.Resolve(new OutcomeInput(1, 1, 1, 0)));
        }

        /// <summary>
        /// docs/04 afsnit 9: "Tilfaeldighed maa modificere omkostningen, men ikke slette
        /// en dygtigt gennemfoert VR-sekvens." En perfekt udfoerelse maa aldrig blive FailForward.
        /// </summary>
        [Fact]
        public void Perfect_execution_is_never_reduced_to_fail_forward()
        {
            var resolver = new OutcomeResolver();
            for (var penalty = 0.0; penalty <= 1.0; penalty += 0.05)
            {
                var tier = resolver.Resolve(new OutcomeInput(1, 1, 1, penalty));
                Assert.NotEqual(OutcomeTier.FailForward, tier);
            }
        }

        static double Gauss(Random rng, double sigma)
        {
            var u1 = 1.0 - rng.NextDouble();
            var u2 = 1.0 - rng.NextDouble();
            return sigma * Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Sin(2.0 * Math.PI * u2);
        }

        static double Clamp(double v) => v < 0 ? 0 : v > 1 ? 1 : v;
    }
}
