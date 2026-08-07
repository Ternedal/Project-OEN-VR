using System;
using ProjectOen.Core.Ids;
using Xunit;

namespace ProjectOen.Core.Tests
{
    public class TypedIdTests
    {
        [Theory]
        [InlineData("SCN_STORMNATTEN_001")]
        [InlineData("SCN_VRAGET_012")]
        public void Accepts_valid_scenario_ids(string value) => Assert.Equal(value, new ScenarioId(value).Value);

        [Theory]
        [InlineData("EVT_STORMNATTEN_001")]   // forkert praefiks for typen
        [InlineData("SCN_stormnatten_001")]   // smaa bogstaver
        [InlineData("SCN_STORMNATTEN_1")]     // ikke tre cifre
        [InlineData("SCN__001")]              // tomt navnesegment
        public void Rejects_malformed_scenario_ids(string value) =>
            Assert.Throws<FormatException>(() => new ScenarioId(value));

        [Fact]
        public void Rejects_empty() => Assert.Throws<ArgumentException>(() => new ScenarioId("   "));

        [Fact]
        public void Ids_of_different_types_are_never_equal()
        {
            var a = new EventId("EVT_OPEN_FOOD_001");
            var b = new ItemId("ITM_OPEN_FOOD_001");
            Assert.False(a.Equals((TypedId)b));
        }

        [Fact]
        public void Same_type_and_value_are_equal()
        {
            Assert.Equal(new EventId("EVT_SPLINTER_001"), new EventId("EVT_SPLINTER_001"));
            Assert.Equal(new EventId("EVT_SPLINTER_001").GetHashCode(), new EventId("EVT_SPLINTER_001").GetHashCode());
        }
    }
}
