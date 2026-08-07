using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Scenario;
using Xunit;

namespace ProjectOen.Core.Tests
{
    public class ScenarioContractTests
    {
        const int BuildProtocol = 1;

        [Fact]
        public void Repository_scenario_example_satisfies_the_contract()
        {
            var scenario = TestVector.LoadScenarioExample();
            var violations = new ScenarioContract().Validate(scenario, BuildProtocol);
            Assert.True(violations.Count == 0,
                "Forventede ingen overtraedelser, fik: " + string.Join(" | ", violations.Select(v => v.ToString())));
        }

        [Fact]
        public void Rejects_a_phase_action_that_is_not_in_the_catalog()
        {
            var scenario = TestVector.LoadScenarioExample();
            var phases = (List<object?>)scenario["phases"]!;
            var planning = (IDictionary<string, object?>)phases.First(p =>
                ((IDictionary<string, object?>)p!)["id"] as string == "DAY1_PLANNING")!;
            ((List<object?>)planning["actions"]!).Add("INT_DOES_NOT_EXIST_999");

            var violations = new ScenarioContract().Validate(scenario, BuildProtocol);
            Assert.Contains(violations, v => v.Code == "ACTION_UNKNOWN");
        }

        [Fact]
        public void Rejects_a_protocol_mismatch()
        {
            var scenario = TestVector.LoadScenarioExample();
            var violations = new ScenarioContract().Validate(scenario, BuildProtocol + 1);
            Assert.Contains(violations, v => v.Code == "PROTOCOL_MISMATCH");
        }

        [Fact]
        public void Rejects_an_action_without_a_secondary_role()
        {
            var scenario = TestVector.LoadScenarioExample();
            var catalog = (List<object?>)scenario["actionCatalog"]!;
            ((IDictionary<string, object?>)catalog[0]!)["secondaryRole"] = "";

            var violations = new ScenarioContract().Validate(scenario, BuildProtocol);
            Assert.Contains(violations, v => v.Code == "ROLE_MISSING");
        }
    }
}
