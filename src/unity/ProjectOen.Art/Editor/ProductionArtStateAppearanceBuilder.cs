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
    /// Adds bounded, state-specific MaterialPropertyBlock profiles to the canonical
    /// damaged/wet production prefabs. Profiles are authored on prefab roots so
    /// every ProductionArtPrefabStateController instance inherits the appearance
    /// automatically. No material assets are duplicated or mutated.
    /// </summary>
    public static class ProductionArtStateAppearanceBuilder
    {
        private const string ManifestPath = "Assets/ProductionArt/Docs/production_art_manifest.json";

        [Serializable]
        private sealed class ManifestEntry
        {
            public string asset_id;
            public string variant;
            public string kind;
            public string path;
        }

        [Serializable]
        private sealed class ManifestWrapper
        {
            public ManifestEntry[] entries;
        }

        internal readonly struct ProfileSpec
        {
            public readonly string assetId;
            public readonly string variant;
            public readonly string profileKey;
            public readonly Color tint;
            public readonly float normalScale;
            public readonly float emissionScale;

            public ProfileSpec(
                string sourceAssetId,
                string sourceVariant,
                string key,
                Color tintMultiplier,
                float normalScaleMultiplier,
                float fireEmissionScale)
            {
                assetId = sourceAssetId;
                variant = sourceVariant;
                profileKey = key;
                tint = tintMultiplier;
                normalScale = normalScaleMultiplier;
                emissionScale = fireEmissionScale;
            }
        }

        // Deliberately small set: these are the canonical states that need an
        // extra storm/damage read beyond their distinct mesh silhouette/texture.
        internal static readonly ProfileSpec[] Profiles =
        {
            new ProfileSpec("PR-001", "damaged", "pr001-damaged", new Color(0.84f, 0.82f, 0.80f, 1f), 0.90f, 1.00f),
            new ProfileSpec("PR-001", "wet", "pr001-wet", new Color(0.78f, 0.84f, 0.88f, 1f), 0.76f, 1.00f),
            new ProfileSpec("CS-004", null, "cs004-damaged", new Color(0.80f, 0.81f, 0.82f, 1f), 0.82f, 1.00f),
            new ProfileSpec("CS-005", null, "cs005-repaired", new Color(1.00f, 0.96f, 0.90f, 1f), 0.98f, 1.00f),
            new ProfileSpec("CS-010", null, "cs010-nearly-out-wet", new Color(0.72f, 0.76f, 0.80f, 1f), 0.72f, 0.22f),
            new ProfileSpec("CS-015", null, "cs015-storm-damaged", new Color(0.76f, 0.80f, 0.84f, 1f), 0.78f, 1.00f),
            new ProfileSpec("EN-016", "worn", "en016-worn", new Color(0.90f, 0.86f, 0.82f, 1f), 0.90f, 1.00f),
            new ProfileSpec("EN-016", "wet", "en016-wet", new Color(0.76f, 0.82f, 0.86f, 1f), 0.72f, 1.00f),
            new ProfileSpec("PR-014", "worn", "pr014-worn", new Color(0.90f, 0.86f, 0.82f, 1f), 0.90f, 1.00f),
            new ProfileSpec("PR-014", "storm-damaged", "pr014-storm-damaged", new Color(0.72f, 0.78f, 0.84f, 1f), 0.76f, 1.00f),
        };

        [MenuItem("Project OEN/Art/Build State-Specific Storm Appearance")]
        public static void BuildAll()
        {
            ManifestEntry[] entries = LoadManifest();
            int updated = 0;

            foreach (ProfileSpec spec in Profiles)
            {
                string prefabPath = ResolvePrefabPath(entries, spec.assetId, spec.variant);
                GameObject root = PrefabUtility.LoadPrefabContents(prefabPath);
                try
                {
                    ProductionArtStateAppearance[] existing = root.GetComponentsInChildren<ProductionArtStateAppearance>(true);
                    foreach (ProductionArtStateAppearance extra in existing)
                    {
                        if (extra != null && extra.gameObject != root)
                            UnityEngine.Object.DestroyImmediate(extra);
                    }

                    ProductionArtStateAppearance appearance = root.GetComponent<ProductionArtStateAppearance>();
                    if (appearance == null)
                        appearance = root.AddComponent<ProductionArtStateAppearance>();

                    appearance.Configure(spec.profileKey, spec.tint, spec.normalScale, spec.emissionScale);
                    EditorUtility.SetDirty(appearance);

                    GameObject saved = PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
                    if (saved == null)
                        throw new InvalidOperationException("Could not save state-appearance prefab: " + prefabPath);
                    updated++;
                }
                finally
                {
                    PrefabUtility.UnloadPrefabContents(root);
                }
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.StateAppearance] Authored " + updated +
                      " canonical state-specific storm/damage appearance profiles.");
        }

        internal static string ResolvePrefabPath(ProfileSpec spec)
        {
            return ResolvePrefabPath(LoadManifest(), spec.assetId, spec.variant);
        }

        private static string ResolvePrefabPath(ManifestEntry[] entries, string assetId, string variant)
        {
            string normalizedVariant = NormalizeState(variant);
            ManifestEntry entry = entries.FirstOrDefault(e =>
                e != null && e.kind == "mesh" && e.asset_id == assetId &&
                (string.IsNullOrEmpty(variant) || NormalizeState(e.variant) == normalizedVariant));

            if (entry == null)
                throw new InvalidOperationException("State-appearance source missing from manifest: " +
                                                    assetId + (string.IsNullOrEmpty(variant) ? string.Empty : "/" + variant));
            if (string.IsNullOrEmpty(entry.path) || !entry.path.EndsWith(".obj", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Unexpected mesh path for state appearance: " + entry.path);

            string prefabPath = entry.path.Replace("/Meshes/", "/Prefabs/");
            prefabPath = prefabPath.Substring(0, prefabPath.Length - 4) + ".prefab";
            if (AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath) == null)
                throw new InvalidOperationException("State-appearance prefab missing: " + prefabPath);
            return prefabPath;
        }

        private static ManifestEntry[] LoadManifest()
        {
            if (!File.Exists(ManifestPath))
                throw new InvalidOperationException("Production-art manifest missing: " + ManifestPath);

            string raw = File.ReadAllText(ManifestPath);
            ManifestWrapper wrapper = JsonUtility.FromJson<ManifestWrapper>("{\"entries\":" + raw + "}");
            if (wrapper == null || wrapper.entries == null || wrapper.entries.Length == 0)
                throw new InvalidOperationException("Production-art manifest could not be parsed for state appearance.");
            return wrapper.entries;
        }

        private static string NormalizeState(string value)
        {
            return string.IsNullOrWhiteSpace(value)
                ? string.Empty
                : value.Trim().ToLowerInvariant().Replace('-', '_').Replace(' ', '_');
        }
    }
}
