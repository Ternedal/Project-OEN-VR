using System;
using System.Collections.Generic;
using System.Linq;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Binds generated state catalogs to the production UI prefabs and creates
    /// lightweight stateful world-controller prefabs for the canonical shelter,
    /// campfire, signal-beacon and radio-repair progressions.
    /// </summary>
    public static class ProductionArtStateBindingBuilder
    {
        private const string SpriteStateRoot = "Assets/ProjectOEN/ProductionArt/StateSets/Sprites";
        private const string WorldStateRoot = "Assets/ProjectOEN/ProductionArt/StateSets";
        private const string UiPrefabRoot = "Assets/ProjectOEN/ProductionArt/UiPrefabs";
        private const string StatefulPrefabRoot = "Assets/ProjectOEN/ProductionArt/StatefulPrefabs";

        private sealed class SpriteBinding
        {
            public string ChildName;
            public string AssetId;
            public string InitialState;

            public SpriteBinding(string childName, string assetId, string initialState)
            {
                ChildName = childName;
                AssetId = assetId;
                InitialState = initialState;
            }
        }

        [MenuItem("Project OEN/Art/Bind Runtime Art States")]
        public static void BuildAll()
        {
            if (!AssetDatabase.IsValidFolder(SpriteStateRoot))
                throw new InvalidOperationException("Sprite state catalogs are missing. Build Runtime State Catalogs first.");
            if (!AssetDatabase.IsValidFolder(UiPrefabRoot))
                throw new InvalidOperationException("Diegetic UI prefabs are missing. Build Diegetic UI Prefabs first.");

            EnsureFolder(StatefulPrefabRoot);

            BindUiPrefab("WristStatus_Diegetic.prefab", new[]
            {
                B("Health", "UI-002", "normal"),
                B("Fatigue", "UI-003", "normal"),
                B("ColdWet", "UI-004", "dry"),
                B("Injury", "UI-005", "minor"),
                B("Shelter", "UI-012", "intact"),
                B("Fire", "UI-013", "strong"),
                B("Signal", "UI-014", "ready"),
            });

            BindUiPrefab("PlanningBoard_Diegetic.prefab", new[]
            {
                B("Time Slots", "PL-002", "4_slots"),
                B("Gather Token", "PL-003", "idle"),
                B("Build Token", "PL-004", "idle"),
                B("Scout Token", "PL-005", "idle"),
                B("Repair Token", "PL-006", "idle"),
                B("Camp Summary", "PL-008", "signal"),
                B("Objective", "PL-010", "current_objective"),
            });

            BindUiPrefab("InteractionMarkers_Diegetic.prefab", new[]
            {
                B("Grab", "WK-001", "hover"),
                B("TwoHandCarry", "WK-002", "active"),
                B("SnapZone", "WK-003", "valid"),
                B("Objective", "WK-005", "primary"),
                B("FireFuel", "WK-010", "warning"),
                B("ShelterRepair", "WK-011", "warning"),
                B("PlanningBoard", "WK-013", "active"),
            });

            BindUiPrefab("MetaStatus_Diegetic.prefab", new[]
            {
                B("Pause Panel", "MN-004", "default"),
                B("Reconnect", "MN-005", "trying"),
                B("Reconnect Icon", "WK-015", "reconnecting"),
            });

            BuildStatefulWorldPrefab(
                "StatefulShelter.prefab",
                "WORLD-SHELTER",
                "foundation");
            BuildStatefulWorldPrefab(
                "StatefulCampfire.prefab",
                "WORLD-CAMPFIRE",
                "laid_unlit");
            BuildStatefulWorldPrefab(
                "StatefulSignalBeacon.prefab",
                "WORLD-SIGNAL-BEACON",
                "base");
            BuildStatefulWorldPrefab(
                "StatefulRadioRepair.prefab",
                "CS-016",
                "broken");

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.State] Bound 24 UI renderers and built 4 stateful world controller prefabs.");
        }

        private static SpriteBinding B(string child, string assetId, string initial)
        {
            return new SpriteBinding(child, assetId, initial);
        }

        private static void BindUiPrefab(string prefabName, IEnumerable<SpriteBinding> bindings)
        {
            string path = UiPrefabRoot + "/" + prefabName;
            GameObject root = PrefabUtility.LoadPrefabContents(path);
            if (root == null)
                throw new InvalidOperationException("Could not load UI prefab for state binding: " + path);

            try
            {
                foreach (SpriteBinding binding in bindings)
                {
                    Transform child = FindChild(root.transform, binding.ChildName);
                    if (child == null)
                        throw new InvalidOperationException(prefabName + " is missing child for state binding: " + binding.ChildName);

                    SpriteRenderer renderer = child.GetComponent<SpriteRenderer>();
                    if (renderer == null)
                        throw new InvalidOperationException(binding.ChildName + " has no SpriteRenderer in " + prefabName);

                    ProductionArtSpriteStateSet set = FindSpriteStateSet(binding.AssetId);
                    if (set == null)
                        throw new InvalidOperationException("Sprite state set missing for " + binding.AssetId);
                    if (!set.ContainsState(binding.InitialState))
                        throw new InvalidOperationException(binding.AssetId + " has no initial state '" + binding.InitialState + "'.");

                    ProductionArtSpriteStateController controller = child.GetComponent<ProductionArtSpriteStateController>();
                    if (controller == null)
                        controller = child.gameObject.AddComponent<ProductionArtSpriteStateController>();
                    controller.Configure(set, renderer, binding.InitialState);
                    EditorUtility.SetDirty(controller);
                }

                if (PrefabUtility.SaveAsPrefabAsset(root, path) == null)
                    throw new InvalidOperationException("Could not save state-bound UI prefab: " + path);
            }
            finally
            {
                PrefabUtility.UnloadPrefabContents(root);
            }
        }

        private static void BuildStatefulWorldPrefab(string prefabName, string stateSetId, string initialState)
        {
            ProductionArtPrefabStateSet set = FindWorldStateSet(stateSetId);
            if (set == null)
                throw new InvalidOperationException("World state set missing for " + stateSetId);
            if (!set.ContainsState(initialState))
                throw new InvalidOperationException(stateSetId + " has no initial state '" + initialState + "'.");

            GameObject root = new GameObject(System.IO.Path.GetFileNameWithoutExtension(prefabName));
            try
            {
                GameObject mount = new GameObject("State Mount");
                mount.transform.SetParent(root.transform, false);
                ProductionArtPrefabStateController controller = root.AddComponent<ProductionArtPrefabStateController>();
                controller.Configure(set, mount.transform, initialState);

                string path = StatefulPrefabRoot + "/" + prefabName;
                if (PrefabUtility.SaveAsPrefabAsset(root, path) == null)
                    throw new InvalidOperationException("Could not save stateful world prefab: " + path);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static ProductionArtSpriteStateSet FindSpriteStateSet(string assetId)
        {
            foreach (string guid in AssetDatabase.FindAssets("t:ProductionArtSpriteStateSet", new[] { SpriteStateRoot }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                ProductionArtSpriteStateSet set = AssetDatabase.LoadAssetAtPath<ProductionArtSpriteStateSet>(path);
                if (set != null && string.Equals(set.AssetId, assetId, StringComparison.OrdinalIgnoreCase))
                    return set;
            }
            return null;
        }

        private static ProductionArtPrefabStateSet FindWorldStateSet(string assetId)
        {
            foreach (string guid in AssetDatabase.FindAssets("t:ProductionArtPrefabStateSet", new[] { WorldStateRoot }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                ProductionArtPrefabStateSet set = AssetDatabase.LoadAssetAtPath<ProductionArtPrefabStateSet>(path);
                if (set != null && string.Equals(set.AssetId, assetId, StringComparison.OrdinalIgnoreCase))
                    return set;
            }
            return null;
        }

        private static Transform FindChild(Transform root, string childName)
        {
            Transform[] all = root.GetComponentsInChildren<Transform>(true);
            return all.FirstOrDefault(t => string.Equals(t.name, childName, StringComparison.Ordinal));
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
