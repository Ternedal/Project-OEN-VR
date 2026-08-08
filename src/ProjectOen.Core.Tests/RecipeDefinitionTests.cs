using System.Linq;
using ProjectOen.Core.Crafting;
using ProjectOen.Core.Interaction;
using ProjectOen.Core.Scenario;
using Xunit;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// Recipe-modellen (schemas/recipe.schema.json), bygget efter shelter-eksemplet.
    /// Beviser content-validering + broen hele vejen: recipe -> InteractionSequence ->
    /// InteractionResolver -> OutcomeResolver(recipe-tærskler) -> OutcomeTier.
    /// </summary>
    public class RecipeDefinitionTests
    {
        static RecipeDefinition Shelter() => new RecipeDefinition(
            "RCP_SHELTER_REINFORCEMENT_001",
            new[] { new RecipeIngredient("ITM_WOOD_001", 2), new RecipeIngredient("ITM_FIBER_001", 2) },
            "CAMP_SHELTER",
            new[]
            {
                new RecipeStep("POSITION_BEAM", "holder", "navigator", 8),
                new RecipeStep("TIE_LEFT", "binder", "stabilizer", 10),
                new RecipeStep("TIE_RIGHT", "binder", "stabilizer", 10),
            },
            new[] { new RecipeResult("SHELTER_REINFORCED", 35) },
            new[] { new RecipeResult("SHELTER_PATCHED", 18, "SHELTER_WEAK") },
            new QualityThresholds(0.45, 0.7, 0.9));

        [Fact]
        public void The_example_recipe_is_valid() => Assert.Empty(Shelter().Validate());

        [Fact]
        public void Validate_flags_bad_id_pattern()
        {
            var r = new RecipeDefinition("shelter", null, "CAMP",
                new[] { new RecipeStep("a", "p", "s", 1) }, new[] { new RecipeResult("X", 1) });
            Assert.Contains(r.Validate(), p => p.Contains("matcher ikke RCP"));
        }

        [Fact]
        public void Validate_flags_nonpositive_quantity()
        {
            var r = new RecipeDefinition("RCP_X_001", new[] { new RecipeIngredient("ITM_A", 0) }, "C",
                new[] { new RecipeStep("a", "p", "s", 1) }, new[] { new RecipeResult("X", 1) });
            Assert.Contains(r.Validate(), p => p.Contains("quantity skal være > 0"));
        }

        [Fact]
        public void Validate_flags_empty_steps()
        {
            var r = new RecipeDefinition("RCP_X_001", null, "C", null, new[] { new RecipeResult("X", 1) });
            Assert.Contains(r.Validate(), p => p.Contains("uden trin"));
        }

        [Fact]
        public void Validate_flags_duplicate_step_ids()
        {
            var r = new RecipeDefinition("RCP_X_001", null, "C",
                new[] { new RecipeStep("a", "p", "s", 1), new RecipeStep("a", "p", "s", 1) },
                new[] { new RecipeResult("X", 1) });
            Assert.Contains(r.Validate(), p => p.Contains("optræder mere end én gang"));
        }

        [Fact]
        public void Validate_flags_missing_role()
        {
            var r = new RecipeDefinition("RCP_X_001", null, "C",
                new[] { new RecipeStep("a", "", "s", 1) }, new[] { new RecipeResult("X", 1) });
            Assert.Contains(r.Validate(), p => p.Contains("begge roller"));
        }

        [Fact]
        public void Validate_flags_nonpositive_duration()
        {
            var r = new RecipeDefinition("RCP_X_001", null, "C",
                new[] { new RecipeStep("a", "p", "s", 0) }, new[] { new RecipeResult("X", 1) });
            Assert.Contains(r.Validate(), p => p.Contains("durationSeconds skal være > 0"));
        }

        [Fact]
        public void Validate_flags_empty_results()
        {
            var r = new RecipeDefinition("RCP_X_001", null, "C",
                new[] { new RecipeStep("a", "p", "s", 1) }, null);
            Assert.Contains(r.Validate(), p => p.Contains("uden results"));
        }

        [Fact]
        public void Validate_flags_unordered_thresholds()
        {
            var r = new RecipeDefinition("RCP_X_001", null, "C",
                new[] { new RecipeStep("a", "p", "s", 1) }, new[] { new RecipeResult("X", 1) },
                null, new QualityThresholds(0.8, 0.5, 0.9));
            Assert.Contains(r.Validate(), p => p.Contains("qualityThresholds"));
        }

        [Fact]
        public void ToInteractionSequence_yields_a_valid_coop_sequence()
        {
            var seq = Shelter().ToInteractionSequence();
            Assert.Empty(seq.Validate());
            Assert.Contains(seq.Steps, s => s.Role == InteractionRole.Primary);
            Assert.Contains(seq.Steps, s => s.Role == InteractionRole.Secondary);
            Assert.True(seq.RequiresBothPlayers);
        }

        [Fact]
        public void Recipe_pipeline_resolves_perfect_coop_to_critical()
        {
            var recipe = Shelter();
            var seq = recipe.ToInteractionSequence();
            var contributions = seq.Steps.Select(s =>
                new StepContribution(s.StepId, s.Role == InteractionRole.Primary ? 0 : 1, 1.0));
            var resolver = new OutcomeResolver(recipe.Thresholds!.ToOutcomeThresholds());
            var tier = InteractionResolver.ResolveTier(seq, contributions, resolver, preparation: 1.0, penalty: 0.0);
            Assert.Equal(OutcomeTier.CriticalSuccess, tier);
        }
    }
}
