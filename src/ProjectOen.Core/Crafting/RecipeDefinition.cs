#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using ProjectOen.Core.Interaction;
using ProjectOen.Core.Scenario;

namespace ProjectOen.Core.Crafting
{
    // Recipe-model (schemas/recipe.schema.json). En craftbar coop-opgave: ingredienser,
    // trin med primær/sekundær-roller, kvalitetstærskler og resultater. Trinene kan laves
    // om til en InteractionSequence (PO-040), og tærsklerne til OutcomeThresholds, så
    // recipe -> interaktion -> udfald hænger sammen som ét authorbart hele.

    public sealed class RecipeIngredient
    {
        public RecipeIngredient(string item, int quantity) { Item = item; Quantity = quantity; }
        public string Item { get; }
        public int Quantity { get; }
    }

    public sealed class RecipeStep
    {
        public RecipeStep(string id, string primaryRole, string secondaryRole, int durationSeconds)
        {
            Id = id;
            PrimaryRole = primaryRole;
            SecondaryRole = secondaryRole;
            DurationSeconds = durationSeconds;
        }

        public string Id { get; }
        public string PrimaryRole { get; }
        public string SecondaryRole { get; }
        public int DurationSeconds { get; }
    }

    public sealed class RecipeResult
    {
        public RecipeResult(string state, int integrityDelta, string? tag = null)
        {
            State = state;
            IntegrityDelta = integrityDelta;
            Tag = tag;
        }

        public string State { get; }
        public int IntegrityDelta { get; }
        public string? Tag { get; }
    }

    public sealed class QualityThresholds
    {
        public QualityThresholds(double functional, double good, double excellent)
        {
            Functional = functional;
            Good = good;
            Excellent = excellent;
        }

        public double Functional { get; }
        public double Good { get; }
        public double Excellent { get; }

        /// <summary>Recipe-tærskler -> OutcomeResolver-tærskler (functional=partial, good=success, excellent=critical).</summary>
        public OutcomeThresholds ToOutcomeThresholds() =>
            new OutcomeThresholds(success: Good, critical: Excellent, partial: Functional);
    }

    public sealed class RecipeDefinition
    {
        static readonly Regex IdPattern = new Regex("^RCP_[A-Z0-9_]+_[0-9]{3}$", RegexOptions.CultureInvariant);

        public RecipeDefinition(string id, IEnumerable<RecipeIngredient>? ingredients, string station,
                                IEnumerable<RecipeStep>? steps, IEnumerable<RecipeResult>? results,
                                IEnumerable<RecipeResult>? partialResults = null, QualityThresholds? thresholds = null)
        {
            Id = id;
            Ingredients = (ingredients ?? Enumerable.Empty<RecipeIngredient>()).ToList();
            Station = station;
            Steps = (steps ?? Enumerable.Empty<RecipeStep>()).ToList();
            Results = (results ?? Enumerable.Empty<RecipeResult>()).ToList();
            PartialResults = (partialResults ?? Enumerable.Empty<RecipeResult>()).ToList();
            Thresholds = thresholds;
        }

        public string Id { get; }
        public IReadOnlyList<RecipeIngredient> Ingredients { get; }
        public string Station { get; }
        public IReadOnlyList<RecipeStep> Steps { get; }
        public IReadOnlyList<RecipeResult> Results { get; }
        public IReadOnlyList<RecipeResult> PartialResults { get; }
        public QualityThresholds? Thresholds { get; }

        /// <summary>Content-validering: en malformet recipe skal fanges ved indlæsning.</summary>
        public IReadOnlyList<string> Validate()
        {
            var problems = new List<string>();

            if (string.IsNullOrEmpty(Id) || !IdPattern.IsMatch(Id))
                problems.Add($"id '{Id}' matcher ikke RCP_..._### (fx RCP_SHELTER_REINFORCEMENT_001).");

            foreach (var ing in Ingredients)
            {
                if (string.IsNullOrWhiteSpace(ing.Item))
                    problems.Add($"{Id}: en ingrediens mangler item-id.");
                if (ing.Quantity <= 0)
                    problems.Add($"{Id}/{ing.Item}: quantity skal være > 0 (var {ing.Quantity}).");
            }

            if (Steps.Count == 0)
                problems.Add($"{Id}: recipe uden trin.");

            foreach (var s in Steps)
            {
                if (string.IsNullOrWhiteSpace(s.PrimaryRole) || string.IsNullOrWhiteSpace(s.SecondaryRole))
                    problems.Add($"{Id}/{s.Id}: begge roller (primær + sekundær) skal være sat.");
                if (s.DurationSeconds <= 0)
                    problems.Add($"{Id}/{s.Id}: durationSeconds skal være > 0 (var {s.DurationSeconds}).");
            }

            foreach (var dup in Steps.GroupBy(s => s.Id, StringComparer.Ordinal).Where(g => g.Count() > 1).Select(g => g.Key))
                problems.Add($"{Id}/{dup}: trin-id optræder mere end én gang.");

            if (Results.Count == 0)
                problems.Add($"{Id}: recipe uden results — en craft skal give noget.");

            if (Thresholds != null)
            {
                var t = Thresholds;
                if (!(0 <= t.Functional && t.Functional <= t.Good && t.Good <= t.Excellent && t.Excellent <= 1))
                    problems.Add($"{Id}: qualityThresholds skal være 0 <= functional <= good <= excellent <= 1 " +
                                 $"(var {t.Functional}/{t.Good}/{t.Excellent}).");
            }

            return problems;
        }

        /// <summary>
        /// PO-040-bro: hvert recipe-trin bliver til ét primær- og ét sekundær-InteractionStep
        /// (begge roller arbejder trinnets varighed), så recipen kan resolves gennem
        /// InteractionResolver. Vægten er durationSeconds — længere trin vejer tungere.
        /// </summary>
        public InteractionSequence ToInteractionSequence()
        {
            var steps = new List<InteractionStep>();
            foreach (var s in Steps)
            {
                steps.Add(new InteractionStep(s.Id + ":primary", InteractionRole.Primary, s.DurationSeconds));
                steps.Add(new InteractionStep(s.Id + ":secondary", InteractionRole.Secondary, s.DurationSeconds));
            }
            return new InteractionSequence(Id, steps, requiresBothPlayers: true);
        }
    }
}
