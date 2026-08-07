using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace ProjectOen.Core.Tests
{
    /// <summary>Laeser repoets egne eksempelfiler, saa testene binder mod den faktiske kontrakt.</summary>
    internal static class TestVector
    {
        public static string RepoRoot
        {
            get
            {
                var dir = new DirectoryInfo(AppContext.BaseDirectory);
                while (dir != null && !File.Exists(Path.Combine(dir.FullName, "00_READ_ME_FIRST.md")))
                    dir = dir.Parent;
                if (dir == null) throw new InvalidOperationException("Kunne ikke finde repo-roden.");
                return dir.FullName;
            }
        }

        public static IDictionary<string, object?> LoadSavegameExample() =>
            LoadJsonObject(Path.Combine(RepoRoot, "examples", "savegame.example.json"));

        public static IDictionary<string, object?> LoadScenarioExample() =>
            LoadJsonObject(Path.Combine(RepoRoot, "examples", "stormnatten.scenario.json"));

        static IDictionary<string, object?> LoadJsonObject(string path)
        {
            using var doc = JsonDocument.Parse(File.ReadAllText(path));
            return (IDictionary<string, object?>)Convert(doc.RootElement)!;
        }

        static object? Convert(JsonElement element)
        {
            switch (element.ValueKind)
            {
                case JsonValueKind.Object:
                    var map = new Dictionary<string, object?>();
                    foreach (var prop in element.EnumerateObject()) map[prop.Name] = Convert(prop.Value);
                    return map;
                case JsonValueKind.Array:
                    var list = new List<object?>();
                    foreach (var item in element.EnumerateArray()) list.Add(Convert(item));
                    return list;
                case JsonValueKind.String: return element.GetString();
                case JsonValueKind.True: return true;
                case JsonValueKind.False: return false;
                case JsonValueKind.Null: return null;
                case JsonValueKind.Number:
                    if (element.TryGetInt64(out var l)) return l;
                    return element.GetDouble();
                default:
                    throw new InvalidOperationException($"Uventet JSON-type: {element.ValueKind}");
            }
        }
    }
}
