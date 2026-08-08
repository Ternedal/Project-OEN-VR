using System.Linq;
using ProjectOen.Core.Interaction;
using Xunit;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// PO-040. Beviser den authorbare coop-opgaves kontrakt uden headset: validering
    /// af content, deterministisk vægtet score, og coop-præmissen (én spiller alene
    /// kan ikke nå topudfaldet). Scoren fødes videre til OutcomeResolver.Tier(score).
    /// </summary>
    public class InteractionSequenceTests
    {
        static InteractionSequence Shelter(bool coop = true) => new InteractionSequence(
            "buildShelter",
            new[]
            {
                new InteractionStep("raiseFrame", InteractionRole.Primary, 2.0),
                new InteractionStep("lashCorners", InteractionRole.Secondary, 1.0),
            },
            requiresBothPlayers: coop);

        // ---- Validering ----

        [Fact]
        public void Validate_flags_empty_sequence()
        {
            var seq = new InteractionSequence("empty", new InteractionStep[0]);
            Assert.Contains(seq.Validate(), p => p.Contains("ingen trin"));
        }

        [Fact]
        public void Validate_flags_nonpositive_weight()
        {
            var seq = new InteractionSequence("bad", new[]
            {
                new InteractionStep("a", InteractionRole.Primary, 0.0),
                new InteractionStep("b", InteractionRole.Secondary, 1.0),
            });
            Assert.Contains(seq.Validate(), p => p.Contains("vægt skal være > 0"));
        }

        [Fact]
        public void Validate_flags_duplicate_step_ids()
        {
            var seq = new InteractionSequence("dup", new[]
            {
                new InteractionStep("a", InteractionRole.Primary, 1.0),
                new InteractionStep("a", InteractionRole.Secondary, 1.0),
            });
            Assert.Contains(seq.Validate(), p => p.Contains("optræder mere end én gang"));
        }

        [Fact]
        public void Validate_flags_missing_primary()
        {
            var seq = new InteractionSequence("noPrimary", new[]
            {
                new InteractionStep("a", InteractionRole.Secondary, 1.0),
            }, requiresBothPlayers: false);
            Assert.Contains(seq.Validate(), p => p.Contains("ingen primær-trin"));
        }

        [Fact]
        public void Validate_flags_coop_without_secondary()
        {
            var seq = new InteractionSequence("soloOnly", new[]
            {
                new InteractionStep("a", InteractionRole.Primary, 1.0),
            }, requiresBothPlayers: true);
            Assert.Contains(seq.Validate(), p => p.Contains("intet sekundær-trin"));
        }

        [Fact]
        public void Validate_passes_wellformed_sequence()
        {
            Assert.Empty(Shelter().Validate());
        }

        // ---- Resolve ----

        [Fact]
        public void Both_players_perfect_scores_one()
        {
            var r = InteractionResolver.Resolve(Shelter(), new[]
            {
                new StepContribution("raiseFrame", 0, 1.0),
                new StepContribution("lashCorners", 1, 1.0),
            });
            Assert.Equal(1.0, r.Score, 6);
            Assert.True(r.BothPlayersActive);
        }

        [Theory]
        [InlineData(1.0, 0.0, 0.6667)] // kun det tunge primær-trin (vægt 2 af 3)
        [InlineData(0.0, 1.0, 0.3333)] // kun det lette sekundær-trin (vægt 1 af 3)
        [InlineData(0.5, 0.5, 0.5000)]
        public void Weighted_average_respects_step_weights(double qPrimary, double qSecondary, double expected)
        {
            // Ikke-coop, så solo-loftet ikke maskerer vægtningen.
            var r = InteractionResolver.Resolve(Shelter(coop: false), new[]
            {
                new StepContribution("raiseFrame", 0, qPrimary),
                new StepContribution("lashCorners", 0, qSecondary),
            });
            Assert.Equal(expected, r.Score, 4);
        }

        [Fact]
        public void Missing_contribution_counts_as_zero()
        {
            // Kun primær udført; sekundær-trinnet mangler helt -> tæller som 0.
            var r = InteractionResolver.Resolve(Shelter(coop: false), new[]
            {
                new StepContribution("raiseFrame", 0, 1.0),
            });
            Assert.Equal(2.0 / 3.0, r.Score, 6);
        }

        [Fact]
        public void Best_of_duplicate_contributions_is_used()
        {
            var r = InteractionResolver.Resolve(Shelter(coop: false), new[]
            {
                new StepContribution("raiseFrame", 0, 0.2),
                new StepContribution("raiseFrame", 0, 0.9), // bedste forsøg tæller
                new StepContribution("lashCorners", 0, 1.0),
            });
            Assert.Equal((2.0 * 0.9 + 1.0 * 1.0) / 3.0, r.Score, 6);
        }

        [Fact]
        public void Solo_completion_is_capped_on_a_coop_task()
        {
            // Perfekt udført, men af samme spiller på begge trin.
            var r = InteractionResolver.Resolve(Shelter(coop: true), new[]
            {
                new StepContribution("raiseFrame", 0, 1.0),
                new StepContribution("lashCorners", 0, 1.0),
            });
            Assert.False(r.BothPlayersActive);
            Assert.Equal(InteractionResolver.CoopSoloCeiling, r.Score, 6);
        }

        [Fact]
        public void Two_active_players_are_not_capped()
        {
            var r = InteractionResolver.Resolve(Shelter(coop: true), new[]
            {
                new StepContribution("raiseFrame", 0, 1.0),
                new StepContribution("lashCorners", 1, 1.0),
            });
            Assert.True(r.BothPlayersActive);
            Assert.Equal(1.0, r.Score, 6);
            Assert.Equal(new[] { 0, 1 }, r.ContributingSlots.OrderBy(s => s).ToArray());
        }

        [Fact]
        public void Non_coop_task_allows_solo_full_score()
        {
            var r = InteractionResolver.Resolve(Shelter(coop: false), new[]
            {
                new StepContribution("raiseFrame", 0, 1.0),
                new StepContribution("lashCorners", 0, 1.0),
            });
            Assert.Equal(1.0, r.Score, 6);
        }

        [Theory]
        [InlineData(1.7, 1.0)]
        [InlineData(-0.4, 0.0)]
        public void Quality_is_clamped_to_unit_interval(double raw, double effective)
        {
            var r = InteractionResolver.Resolve(Shelter(coop: false), new[]
            {
                new StepContribution("raiseFrame", 0, raw),
                new StepContribution("lashCorners", 0, effective),
            });
            var expected = (2.0 * effective + 1.0 * effective) / 3.0;
            Assert.Equal(expected, r.Score, 6);
        }

        [Fact]
        public void Score_is_independent_of_contribution_order()
        {
            var a = InteractionResolver.Resolve(Shelter(), new[]
            {
                new StepContribution("raiseFrame", 0, 0.8),
                new StepContribution("lashCorners", 1, 0.4),
            });
            var b = InteractionResolver.Resolve(Shelter(), new[]
            {
                new StepContribution("lashCorners", 1, 0.4),
                new StepContribution("raiseFrame", 0, 0.8),
            });
            Assert.Equal(a.Score, b.Score, 9);
            Assert.Equal(a.BothPlayersActive, b.BothPlayersActive);
        }
    }
}
