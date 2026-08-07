using System;
using System.Collections.Generic;
using System.Linq;
using ProjectOen.Core.Ids;

namespace ProjectOen.Core.Scenario
{
    /// <summary>
    /// Kontraktvalidering af en ScenarioDefinition. Samme regler som
    /// tools/validate_handoff.py haandhaever i CI, men her hvor spillet loader
    /// data - saa en fejl fanges ved indlaesning i stedet for midt i en session.
    ///
    /// docs/10: build stopper ved action-ID uden post i actionCatalog og ved
    /// supportedBuildProtocol der ikke matcher buildet.
    /// </summary>
    public sealed class ScenarioContract
    {
        public sealed class Violation
        {
            public Violation(string code, string message)
            {
                Code = code;
                Message = message;
            }

            public string Code { get; }
            public string Message { get; }
            public override string ToString() => $"{Code}: {Message}";
        }

        public IReadOnlyList<Violation> Validate(IDictionary<string, object?> scenario, int buildProtocolVersion)
        {
            var violations = new List<Violation>();

            if (!scenario.TryGetValue("id", out var rawId) || !(rawId is string idText))
            {
                violations.Add(new Violation("SCN_ID_MISSING", "Scenariet mangler 'id'."));
            }
            else
            {
                try { _ = new ScenarioId(idText); }
                catch (Exception ex) { violations.Add(new Violation("SCN_ID_FORMAT", ex.Message)); }
            }

            if (!scenario.TryGetValue("supportedBuildProtocol", out var rawProtocol) || !(rawProtocol is long or int))
            {
                violations.Add(new Violation("PROTOCOL_MISSING",
                    "Scenariet mangler 'supportedBuildProtocol'. Compatibility handshake i docs/07 afsnit 5 afhaenger af det."));
            }
            else
            {
                var protocol = Convert.ToInt32(rawProtocol);
                if (protocol != buildProtocolVersion)
                {
                    violations.Add(new Violation("PROTOCOL_MISMATCH",
                        $"Scenariet kraever protocol {protocol}, men buildet koerer {buildProtocolVersion}."));
                }
            }

            var catalog = new HashSet<string>();
            if (scenario.TryGetValue("actionCatalog", out var rawCatalog) && rawCatalog is IEnumerable<object?> entries)
            {
                foreach (var entry in entries.OfType<IDictionary<string, object?>>())
                {
                    if (!entry.TryGetValue("id", out var rawEntryId) || !(rawEntryId is string entryId))
                    {
                        violations.Add(new Violation("ACTION_ID_MISSING", "En post i actionCatalog mangler 'id'."));
                        continue;
                    }

                    try { _ = new InteractionId(entryId); }
                    catch (Exception ex) { violations.Add(new Violation("ACTION_ID_FORMAT", ex.Message)); }

                    if (!catalog.Add(entryId))
                        violations.Add(new Violation("ACTION_ID_DUPLICATE", $"Dubleret action-ID: {entryId}."));

                    // docs/04 afsnit 8: hver handling dokumenterer to roller.
                    // En sekundaer rolle der bare er "se paa" er praecis det, reglen forbyder.
                    foreach (var role in new[] { "primaryRole", "secondaryRole" })
                    {
                        if (!entry.TryGetValue(role, out var value) || string.IsNullOrWhiteSpace(value as string))
                            violations.Add(new Violation("ROLE_MISSING", $"{entryId} mangler '{role}'."));
                    }
                }
            }
            else
            {
                violations.Add(new Violation("CATALOG_MISSING", "Scenariet mangler 'actionCatalog'."));
            }

            // Ukendte win/lose-regeltyper skal fanges her - ved indlaesning - og ikke
            // foerst naar spillet forsoeger at afgoere, om spillerne har tabt.
            foreach (var listKey in new[] { "winRules", "loseRules" })
            {
                if (!scenario.TryGetValue(listKey, out var rawRules) || !(rawRules is IEnumerable<object?> rules))
                {
                    violations.Add(new Violation("RULES_MISSING", $"Scenariet mangler '{listKey}'."));
                    continue;
                }

                foreach (var rule in rules.OfType<IDictionary<string, object?>>())
                {
                    var type = rule.TryGetValue("type", out var raw) ? raw as string : null;
                    if (string.IsNullOrWhiteSpace(type))
                    {
                        violations.Add(new Violation("RULE_TYPE_MISSING", $"En regel i {listKey} mangler 'type'."));
                    }
                    else if (!ScenarioOutcomeRules.KnownTypes.Contains(type))
                    {
                        violations.Add(new Violation("RULE_TYPE_UNKNOWN",
                            $"{listKey}: ukendt regeltype '{type}'. Kendte: {string.Join(", ", ScenarioOutcomeRules.KnownTypes)}."));
                    }
                }
            }

            if (scenario.TryGetValue("phases", out var rawPhases) && rawPhases is IEnumerable<object?> phases)
            {
                foreach (var phase in phases.OfType<IDictionary<string, object?>>())
                {
                    var phaseId = phase.TryGetValue("id", out var pid) ? pid as string ?? "?" : "?";
                    if (!phase.TryGetValue("actions", out var rawActions) || !(rawActions is IEnumerable<object?> actions))
                        continue;

                    foreach (var action in actions.OfType<string>())
                    {
                        if (!catalog.Contains(action))
                        {
                            violations.Add(new Violation("ACTION_UNKNOWN",
                                $"Fase {phaseId} refererer til ukendt action '{action}'."));
                        }
                    }
                }
            }
            else
            {
                violations.Add(new Violation("PHASES_MISSING", "Scenariet mangler 'phases'."));
            }

            return violations;
        }
    }
}
