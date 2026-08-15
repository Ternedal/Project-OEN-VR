using System;
using System.Collections.Generic;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Hard gate for the small canonical set of state-specific storm/damage
    /// appearance profiles. Keeps the authored profiles bounded and prevents
    /// accidental profile duplication across generated prefabs.
    /// </summary>
    public static class ProductionArtStateAppearanceAudit
    {
        private const string PrefabRoot = "Assets/ProductionArt/Prefabs";
        private const float Epsilon = 0.001f;

        [MenuItem("Project OEN/Art/Audit State-Specific Storm Appearance")]
        public static void AuditAll()
        {
            var errors = new List<string>();
            var expectedPaths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

            foreach (ProductionArtStateAppearanceBuilder.ProfileSpec spec in ProductionArtStateAppearanceBuilder.Profiles)
            {
                string prefabPath;
                try
                {
                    prefabPath = ProductionArtStateAppearanceBuilder.ResolvePrefabPath(spec);
                }
                catch (Exception ex)
                {
                    errors.Add(ex.Message);
                    continue;
                }

                expectedPaths.Add(prefabPath);
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
                if (prefab == null)
                {
                    errors.Add("Missing configured prefab: " + prefabPath);
                    continue;
                }

                ProductionArtStateAppearance[] profiles = prefab.GetComponentsInChildren<ProductionArtStateAppearance>(true);
                if (profiles.Length != 1)
                {
                    errors.Add(prefabPath + " expected exactly one ProductionArtStateAppearance, found " + profiles.Length + ".");
                    continue;
                }

                ProductionArtStateAppearance appearance = profiles[0];
                if (appearance.gameObject != prefab)
                    errors.Add(prefabPath + " state appearance must live on prefab root.");
                if (!string.Equals(appearance.ProfileKey, spec.profileKey, StringComparison.Ordinal))
                    errors.Add(prefabPath + " profile key mismatch: " + appearance.ProfileKey + " != " + spec.profileKey + ".");
                if (!Approximately(appearance.TintMultiplier, spec.tint))
                    errors.Add(prefabPath + " tint mismatch for " + spec.profileKey + ".");
                if (Mathf.Abs(appearance.NormalScaleMultiplier - spec.normalScale) > Epsilon)
                    errors.Add(prefabPath + " normal-scale mismatch for " + spec.profileKey + ".");
                if (Mathf.Abs(appearance.EmissionScale - spec.emissionScale) > Epsilon)
                    errors.Add(prefabPath + " emission-scale mismatch for " + spec.profileKey + ".");
            }

            string[] guids = AssetDatabase.FindAssets("t:Prefab", new[] { PrefabRoot });
            int totalProfiles = 0;
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (prefab == null)
                    continue;

                ProductionArtStateAppearance[] profiles = prefab.GetComponentsInChildren<ProductionArtStateAppearance>(true);
                totalProfiles += profiles.Length;
                if (profiles.Length > 0 && !expectedPaths.Contains(path))
                    errors.Add("Unexpected state-appearance profile outside canonical target set: " + path + ".");
            }

            if (totalProfiles != ProductionArtStateAppearanceBuilder.Profiles.Length)
            {
                errors.Add("Expected " + ProductionArtStateAppearanceBuilder.Profiles.Length +
                           " total state-appearance profiles, found " + totalProfiles + ".");
            }

            if (errors.Count > 0)
                throw new InvalidOperationException("[ProjectOEN.Art.StateAppearance] Audit failed:\n - " + string.Join("\n - ", errors));

            Debug.Log("[ProjectOEN.Art.StateAppearance] PASS: " + totalProfiles +
                      " canonical state profiles are exact, root-local and bounded.");
        }

        private static bool Approximately(Color a, Color b)
        {
            return Mathf.Abs(a.r - b.r) <= Epsilon &&
                   Mathf.Abs(a.g - b.g) <= Epsilon &&
                   Mathf.Abs(a.b - b.b) <= Epsilon &&
                   Mathf.Abs(a.a - b.a) <= Epsilon;
        }
    }
}
