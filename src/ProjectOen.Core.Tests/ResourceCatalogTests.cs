using System;
using System.Collections.Generic;
using ProjectOen.Core.Scenario;
using Xunit;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// PO-035. Beviser at ukendte ressourcenøgler fanges — både direkte i kataloget og
    /// via EffectTable.Validate(), så en stavefejl ikke bliver til en fantom-ressource.
    /// </summary>
    public class ResourceCatalogTests
    {
        [Theory]
        [InlineData("wood")]
        [InlineData("fiber")]
        [InlineData("food")]
        [InlineData("herbs")]
        public void IsKnown_recognizes_catalog_keys(string key) => Assert.True(ResourceCatalog.IsKnown(key));

        [Theory]
        [InlineData("wod")]
        [InlineData("gold")]
        [InlineData("Wood")]
        [InlineData("")]
        public void IsKnown_rejects_unknown_or_miscased(string key) => Assert.False(ResourceCatalog.IsKnown(key));

        [Fact]
        public void Validate_flags_unknown_and_passes_all_known()
        {
            Assert.Contains(ResourceCatalog.Validate(new[] { "wood", "wod" }), p => p.Contains("wod"));
            Assert.Empty(ResourceCatalog.Validate(new[] { "wood", "fiber", "food", "herbs" }));
        }

        static EffectTable TableWithResource(string actionId, string resourceKey)
        {
            var table = new EffectTable();
            foreach (OutcomeTier tier in Enum.GetValues(typeof(OutcomeTier)))
                table.Set(actionId, tier, new ActionEffect(
                    resourceDeltas: new Dictionary<string, int> { [resourceKey] = 1 }));
            return table;
        }

        [Fact]
        public void EffectTable_validate_flags_unknown_resource_key()
        {
            var problems = TableWithResource("INT_TYPO", "wod").Validate();
            Assert.Contains(problems, p => p.Contains("ukendt ressource") && p.Contains("wod"));
        }

        [Fact]
        public void EffectTable_validate_accepts_catalog_resource_key()
        {
            var problems = TableWithResource("INT_OK", ResourceCatalog.Wood).Validate();
            Assert.DoesNotContain(problems, p => p.Contains("ukendt ressource"));
        }
    }
}
