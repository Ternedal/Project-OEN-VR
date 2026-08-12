using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Generates deterministic runtime state-set assets from the production-art
    /// manifest. One catalog asset is created per canonical master asset ID, plus
    /// three semantic construction progressions spanning CS-001..CS-015.
    /// </summary>
    public static class ProductionArtStateCatalogBuilder
    {
        private const string ManifestPath = "Assets/ProjectOEN/ProductionArt/Docs/production_art_manifest.json";
        private const string SpriteRoot = "Assets/ProjectOEN/ProductionArt/StateSets/Sprites";
        private const string WorldRoot = "Assets/ProjectOEN/ProductionArt/StateSets/World";
        private const string CompositeRoot = "Assets/ProjectOEN/ProductionArt/StateSets/Composite";

        [Serializable]
        private sealed class ManifestEntry
        {
            public string asset_id;
            public string name;
            public string category;
            public string variant;
            public string kind;
            public string path;
        }

        [Serializable]
        private sealed class ManifestWrapper
        {
            public ManifestEntry[] entries;
        }

        [MenuItem("Project OEN/Art/Build Runtime State Catalogs")]
        public static void BuildAll()
        {
            ManifestEntry[] entries = LoadManifest();
            EnsureFolder(SpriteRoot);
            EnsureFolder(WorldRoot);
            EnsureFolder(CompositeRoot);

            int spriteSets = BuildSpriteSets(entries);
            int worldSets = BuildWorldSets(entries);
            int compositeSets = BuildCompositeConstructionSets(entries);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.State] Built " + spriteSets + " sprite state sets + " +
                      worldSets + " world state sets + " + compositeSets +
                      " composite construction state sets.");
        }

        private static int BuildSpriteSets(ManifestEntry[] entries)
        {
            int count = 0;
            foreach (IGrouping<string, ManifestEntry> group in entries
                         .Where(e => e.kind == "sprite")
                         .GroupBy(e => e.asset_id)
                         .OrderBy(g => g.Key, StringComparer.Ordinal))
            {
                ManifestEntry first = group.First();
                List<ProductionArtSpriteStateSet.Entry> states = new List<ProductionArtSpriteStateSet.Entry>();
                foreach (ManifestEntry entry in group)
                {
                    Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(entry.path);
                    if (sprite == null)
                        throw new InvalidOperationException("Production sprite did not import: " + entry.path);
                    states.Add(new ProductionArtSpriteStateSet.Entry(NormalizeState(entry.variant), sprite));
                }

                string categoryFolder = SpriteRoot + "/" + Slug(first.category);
                EnsureFolder(categoryFolder);
                string assetPath = categoryFolder + "/" + first.asset_id.ToLowerInvariant() + "_" + Slug(first.name) + ".asset";
                ProductionArtSpriteStateSet set = LoadOrCreate<ProductionArtSpriteStateSet>(assetPath);
                set.Configure(first.asset_id, first.name, first.category, states[0].key, states);
                EditorUtility.SetDirty(set);
                count++;
            }
            return count;
        }

        private static int BuildWorldSets(ManifestEntry[] entries)
        {
            int count = 0;
            foreach (IGrouping<string, ManifestEntry> group in entries
                         .Where(e => e.kind == "mesh")
                         .GroupBy(e => e.asset_id)
                         .OrderBy(g => g.Key, StringComparer.Ordinal))
            {
                ManifestEntry first = group.First();
                List<ProductionArtPrefabStateSet.Entry> states = new List<ProductionArtPrefabStateSet.Entry>();
                foreach (ManifestEntry entry in group)
                {
                    string prefabPath = MeshToPrefabPath(entry.path);
                    GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
                    if (prefab == null)
                        throw new InvalidOperationException("Production prefab missing for state catalog: " + prefabPath);
                    states.Add(new ProductionArtPrefabStateSet.Entry(NormalizeState(entry.variant), prefab));
                }

                string categoryFolder = WorldRoot + "/" + Slug(first.category);
                EnsureFolder(categoryFolder);
                string assetPath = categoryFolder + "/" + first.asset_id.ToLowerInvariant() + "_" + Slug(first.name) + ".asset";
                ProductionArtPrefabStateSet set = LoadOrCreate<ProductionArtPrefabStateSet>(assetPath);
                set.Configure(first.asset_id, first.name, first.category, states[0].key, states);
                EditorUtility.SetDirty(set);
                count++;
            }
            return count;
        }

        private static int BuildCompositeConstructionSets(ManifestEntry[] entries)
        {
            BuildComposite(entries,
                "WORLD-SHELTER", "Shelter construction progression", "Construction states", "foundation",
                new[]
                {
                    Pair("foundation", "CS-001"),
                    Pair("partial_frame", "CS-002"),
                    Pair("covered_usable", "CS-003"),
                    Pair("damaged", "CS-004"),
                    Pair("repaired_reinforced", "CS-005"),
                },
                CompositeRoot + "/world_shelter_progression.asset");

            BuildComposite(entries,
                "WORLD-CAMPFIRE", "Campfire strength progression", "Construction states", "laid_unlit",
                new[]
                {
                    Pair("laid_unlit", "CS-006"),
                    Pair("ember", "CS-007"),
                    Pair("small_flame", "CS-008"),
                    Pair("strong_flame", "CS-009"),
                    Pair("nearly_out_wet", "CS-010"),
                },
                CompositeRoot + "/world_campfire_progression.asset");

            BuildComposite(entries,
                "WORLD-SIGNAL-BEACON", "Signal beacon construction progression", "Construction states", "base",
                new[]
                {
                    Pair("base", "CS-011"),
                    Pair("partial", "CS-012"),
                    Pair("complete", "CS-013"),
                    Pair("lit_active", "CS-014"),
                    Pair("storm_damaged", "CS-015"),
                },
                CompositeRoot + "/world_signal_beacon_progression.asset");
            return 3;
        }

        private static void BuildComposite(
            ManifestEntry[] entries,
            string id,
            string name,
            string category,
            string defaultState,
            KeyValuePair<string, string>[] mapping,
            string assetPath)
        {
            List<ProductionArtPrefabStateSet.Entry> states = new List<ProductionArtPrefabStateSet.Entry>();
            foreach (KeyValuePair<string, string> pair in mapping)
            {
                ManifestEntry manifestEntry = entries.FirstOrDefault(e => e.kind == "mesh" && e.asset_id == pair.Value);
                if (manifestEntry == null)
                    throw new InvalidOperationException("Composite state source missing from manifest: " + pair.Value);
                string prefabPath = MeshToPrefabPath(manifestEntry.path);
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
                if (prefab == null)
                    throw new InvalidOperationException("Composite state prefab missing: " + prefabPath);
                states.Add(new ProductionArtPrefabStateSet.Entry(pair.Key, prefab));
            }

            ProductionArtPrefabStateSet set = LoadOrCreate<ProductionArtPrefabStateSet>(assetPath);
            set.Configure(id, name, category, defaultState, states);
            EditorUtility.SetDirty(set);
        }

        private static ManifestEntry[] LoadManifest()
        {
            if (!File.Exists(ManifestPath))
                throw new InvalidOperationException("Production-art manifest missing: " + ManifestPath);
            string raw = File.ReadAllText(ManifestPath);
            ManifestWrapper wrapper = JsonUtility.FromJson<ManifestWrapper>("{\"entries\":" + raw + "}");
            if (wrapper == null || wrapper.entries == null || wrapper.entries.Length == 0)
                throw new InvalidOperationException("Production-art manifest could not be parsed by Unity JsonUtility.");
            return wrapper.entries;
        }

        private static string MeshToPrefabPath(string meshPath)
        {
            if (string.IsNullOrEmpty(meshPath) || !meshPath.EndsWith(".obj", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Unexpected mesh manifest path: " + meshPath);
            return meshPath.Replace("/Meshes/", "/Prefabs/").Substring(0, meshPath.Length - 4).Replace("/Meshes/", "/Prefabs/") + ".prefab";
        }

        private static string NormalizeState(string value)
        {
            return string.IsNullOrWhiteSpace(value) ? "default" : value.Trim().ToLowerInvariant().Replace('-', '_').Replace(' ', '_');
        }

        private static KeyValuePair<string, string> Pair(string state, string assetId)
        {
            return new KeyValuePair<string, string>(state, assetId);
        }

        private static T LoadOrCreate<T>(string assetPath) where T : ScriptableObject
        {
            T existing = AssetDatabase.LoadAssetAtPath<T>(assetPath);
            if (existing != null)
                return existing;

            UnityEngine.Object other = AssetDatabase.LoadMainAssetAtPath(assetPath);
            if (other != null)
                AssetDatabase.DeleteAsset(assetPath);

            T created = ScriptableObject.CreateInstance<T>();
            AssetDatabase.CreateAsset(created, assetPath);
            return created;
        }

        private static string Slug(string value)
        {
            if (string.IsNullOrWhiteSpace(value)) return "default";
            char[] chars = value.ToLowerInvariant()
                .Replace("ø", "oe").Replace("å", "aa").Replace("æ", "ae")
                .Select(c => char.IsLetterOrDigit(c) ? c : '_')
                .ToArray();
            string result = new string(chars);
            while (result.Contains("__")) result = result.Replace("__", "_");
            return result.Trim('_');
        }

        private static void EnsureFolder(string path)
        {
            string normalized = path.Replace('\\', '/').TrimEnd('/');
            if (AssetDatabase.IsValidFolder(normalized)) return;
            string[] parts = normalized.Split('/');
            string current = parts[0];
            for (int i = 1; i < parts.Length; i++)
            {
                string next = current + "/" + parts[i];
                if (!AssetDatabase.IsValidFolder(next)) AssetDatabase.CreateFolder(current, parts[i]);
                current = next;
            }
        }
    }
}
