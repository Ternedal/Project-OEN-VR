#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Scenario
{
    /// <summary>
    /// PO-035: de autoritative ressourcenøgler (docs/04: træ/fiber/mad/urter). En handling
    /// der refererer en nøgle uden for kataloget — typisk en stavefejl — ville ellers stille
    /// skabe en fantom-ressource, ingen balancering tager højde for. Kataloget fanger det ved
    /// indlæsning i stedet for ved playtest.
    /// </summary>
    public static class ResourceCatalog
    {
        public const string Wood = "wood";
        public const string Fiber = "fiber";
        public const string Food = "food";
        public const string Herbs = "herbs";

        /// <summary>Ikke i docs/04's fire (træ/fiber/mad/urter), men brugt i det faktiske content
        /// (stormnatten.scenario, savegame, recipe). Medtaget så kataloget matcher virkeligheden;
        /// doc/content-uoverensstemmelsen er noteret til ejeren.</summary>
        public const string Supplies = "supplies";

        public static readonly IReadOnlyCollection<string> Known = new[] { Wood, Fiber, Food, Herbs, Supplies };

        static readonly HashSet<string> KnownSet = new HashSet<string>(Known, StringComparer.Ordinal);

        public static bool IsKnown(string? key) => key != null && KnownSet.Contains(key);

        /// <summary>Flag ukendte nøgler (ordinal, case-sensitivt). Tom liste = alt kendt.</summary>
        public static IReadOnlyList<string> Validate(IEnumerable<string>? keys, string context = "")
        {
            var problems = new List<string>();
            var seen = (keys ?? Enumerable.Empty<string>())
                .Distinct(StringComparer.Ordinal)
                .OrderBy(k => k, StringComparer.Ordinal);
            foreach (var key in seen)
            {
                if (!IsKnown(key))
                {
                    var where = string.IsNullOrEmpty(context) ? "" : context + ": ";
                    problems.Add($"{where}ukendt ressource '{key}'. Kendte: {string.Join(", ", Known)}.");
                }
            }
            return problems;
        }
    }
}
