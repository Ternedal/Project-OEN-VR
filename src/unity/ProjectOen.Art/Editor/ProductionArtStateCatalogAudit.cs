using System;
using System.Collections.Generic;
using System.Linq;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Audits the actually generated ScriptableObject state catalogs after Unity
    /// has imported production sprites/world prefabs and StateCatalogBuilder ran.
    /// This proves reference integrity inside Unity; repo-side Python validation
    /// alone cannot prove AssetDatabase/serialization resolution.
    /// </summary>
    public static class ProductionArtStateCatalogAudit
    {
        private const string ManifestPath = "Assets/ProjectOEN/ProductionArt/Docs/production_art_manifest.json";
        private const string SpriteRoot = "Assets/ProjectOEN/ProductionArt/StateSets/Sprites";
        private const string WorldRoot = "Assets/ProjectOEN/ProductionArt/StateSets/World";
        private const string CompositeRoot = "Assets/ProjectOEN/ProductionArt/StateSets/Composite";

        private const int ExpectedCanonicalIds = 148;
        private const int ExpectedSpriteSets = 87;
        private const int ExpectedWorldSets = 61;
        private const int ExpectedCompositeSets = 3;

        [Serializable]
        private sealed class ManifestEntry
        {
            public string asset_id;
            public string kind;
        }

        [Serializable]
        private sealed class ManifestWrapper
        {
            public ManifestEntry[] entries;
        }

        [MenuItem("Project OEN/Art/Audit Runtime State Catalogs")]
        public static void AuditAll()
        {
            HashSet<string> manifestIds = LoadManifestIds();
            if (manifestIds.Count != ExpectedCanonicalIds)
                throw new InvalidOperationException("Production manifest canonical ID count mismatch: " + manifestIds.Count +
                    " (expected " + ExpectedCanonicalIds + ")");

            ProductionArtSpriteStateSet[] spriteSets = LoadAll<ProductionArtSpriteStateSet>(SpriteRoot);
            ProductionArtPrefabStateSet[] worldSets = LoadAll<ProductionArtPrefabStateSet>(WorldRoot);
            ProductionArtPrefabStateSet[] compositeSets = LoadAll<ProductionArtPrefabStateSet>(CompositeRoot);

            if (spriteSets.Length != ExpectedSpriteSets)
                throw new InvalidOperationException("Sprite state-set count mismatch: " + spriteSets.Length +
                    " (expected " + ExpectedSpriteSets + ")");
            if (worldSets.Length != ExpectedWorldSets)
                throw new InvalidOperationException("World state-set count mismatch: " + worldSets.Length +
                    " (expected " + ExpectedWorldSets + ")");
            if (compositeSets.Length != ExpectedCompositeSets)
                throw new InvalidOperationException("Composite state-set count mismatch: " + compositeSets.Length +
                    " (expected " + ExpectedCompositeSets + ")");

            var seenCanonicalIds = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (ProductionArtSpriteStateSet set in spriteSets)
            {
                AuditSpriteSet(set);
                if (!seenCanonicalIds.Add(set.AssetId))
                    throw new InvalidOperationException("Duplicate canonical state-set ID: " + set.AssetId);
            }
            foreach (ProductionArtPrefabStateSet set in worldSets)
            {
                AuditWorldSet(set);
                if (!seenCanonicalIds.Add(set.AssetId))
                    throw new InvalidOperationException("Duplicate canonical state-set ID: " + set.AssetId);
            }

            if (!seenCanonicalIds.SetEquals(manifestIds))
            {
                string missing = string.Join(", ", manifestIds.Except(seenCanonicalIds).OrderBy(x => x));
                string extra = string.Join(", ", seenCanonicalIds.Except(manifestIds).OrderBy(x => x));
                throw new InvalidOperationException("State-catalog/manifest ID mismatch. Missing=[" + missing + "] Extra=[" + extra + "]");
            }

            AuditComposite(compositeSets, "WORLD-SHELTER",
                new[] { "foundation", "partial_frame", "covered_usable", "damaged", "repaired_reinforced" });
            AuditComposite(compositeSets, "WORLD-CAMPFIRE",
                new[] { "laid_unlit", "ember", "small_flame", "strong_flame", "nearly_out_wet" });
            AuditComposite(compositeSets, "WORLD-SIGNAL-BEACON",
                new[] { "base", "partial", "complete", "lit_active", "storm_damaged" });

            Debug.Log("[ProjectOEN.Art.State.Audit] PASS: 148 canonical state catalogs resolved in Unity " +
                      "(87 sprite + 61 world) plus 3 complete 5-state construction composites; all references non-null and IDs match manifest.");
        }

        private static HashSet<string> LoadManifestIds()
        {
            TextAsset asset = AssetDatabase.LoadAssetAtPath<TextAsset>(ManifestPath);
            if (asset == null)
                throw new InvalidOperationException("Production-art manifest was not imported by Unity: " + ManifestPath);

            ManifestWrapper wrapper = JsonUtility.FromJson<ManifestWrapper>("{\"entries\":" + asset.text + "}");
            if (wrapper == null || wrapper.entries == null)
                throw new InvalidOperationException("Production-art manifest could not be parsed by Unity JsonUtility.");

            var result = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (ManifestEntry entry in wrapper.entries)
            {
                if (entry == null || string.IsNullOrWhiteSpace(entry.asset_id))
                    throw new InvalidOperationException("Manifest contains an empty asset_id entry.");
                result.Add(entry.asset_id);
            }
            return result;
        }

        private static T[] LoadAll<T>(string root) where T : UnityEngine.Object
        {
            if (!AssetDatabase.IsValidFolder(root))
                throw new InvalidOperationException("State-set folder is missing: " + root);

            return AssetDatabase.FindAssets("t:" + typeof(T).Name, new[] { root })
                .Select(AssetDatabase.GUIDToAssetPath)
                .Select(AssetDatabase.LoadAssetAtPath<T>)
                .Where(x => x != null)
                .ToArray();
        }

        private static void AuditSpriteSet(ProductionArtSpriteStateSet set)
        {
            if (set == null || string.IsNullOrWhiteSpace(set.AssetId))
                throw new InvalidOperationException("Sprite state set has no canonical AssetId.");
            if (set.States == null || set.States.Count == 0)
                throw new InvalidOperationException(set.AssetId + " contains no sprite states.");

            var keys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (ProductionArtSpriteStateSet.Entry entry in set.States)
            {
                if (entry == null || string.IsNullOrWhiteSpace(entry.key) || entry.sprite == null)
                    throw new InvalidOperationException(set.AssetId + " has an empty/null sprite state entry.");
                if (!keys.Add(entry.key))
                    throw new InvalidOperationException(set.AssetId + " has duplicate sprite state key: " + entry.key);
            }
            if (!set.ContainsState(set.DefaultState))
                throw new InvalidOperationException(set.AssetId + " default sprite state is not present: " + set.DefaultState);
        }

        private static void AuditWorldSet(ProductionArtPrefabStateSet set)
        {
            if (set == null || string.IsNullOrWhiteSpace(set.AssetId))
                throw new InvalidOperationException("World state set has no canonical AssetId.");
            if (set.States == null || set.States.Count == 0)
                throw new InvalidOperationException(set.AssetId + " contains no world states.");

            var keys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (ProductionArtPrefabStateSet.Entry entry in set.States)
            {
                if (entry == null || string.IsNullOrWhiteSpace(entry.key) || entry.prefab == null)
                    throw new InvalidOperationException(set.AssetId + " has an empty/null prefab state entry.");
                if (!keys.Add(entry.key))
                    throw new InvalidOperationException(set.AssetId + " has duplicate world state key: " + entry.key);
            }
            if (!set.ContainsState(set.DefaultState))
                throw new InvalidOperationException(set.AssetId + " default world state is not present: " + set.DefaultState);
        }

        private static void AuditComposite(
            ProductionArtPrefabStateSet[] composites,
            string assetId,
            string[] expectedKeys)
        {
            ProductionArtPrefabStateSet set = composites.SingleOrDefault(x =>
                string.Equals(x.AssetId, assetId, StringComparison.OrdinalIgnoreCase));
            if (set == null)
                throw new InvalidOperationException("Composite state set missing: " + assetId);

            AuditWorldSet(set);
            string[] actual = set.States.Select(x => x.key).OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToArray();
            string[] expected = expectedKeys.OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToArray();
            if (!actual.SequenceEqual(expected, StringComparer.OrdinalIgnoreCase))
                throw new InvalidOperationException(assetId + " composite keys mismatch. Expected [" +
                    string.Join(", ", expected) + "] actual [" + string.Join(", ", actual) + "]");
        }
    }
}
