using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Builds lightweight world-space/diegetic visual prefabs from the generated
    /// Project ØEN production sprites. These are art prefabs, not gameplay logic:
    /// runtime systems can bind state/interaction later without replacing the art.
    ///
    /// SpriteRenderer is used deliberately instead of Canvas/TMP so this layer has
    /// no extra package dependency and remains inexpensive on Quest 2.
    /// </summary>
    public static class ProductionArtDiegeticUiBuilder
    {
        private const string SpriteRoot = "Assets/ProductionArt/Sprites";
        private const string OutputRoot = "Assets/ProductionArt/UiPrefabs";

        [MenuItem("Project OEN/Art/Build Diegetic UI Prefabs")]
        public static void BuildAll()
        {
            if (!AssetDatabase.IsValidFolder(SpriteRoot))
                throw new InvalidOperationException("Production sprite root is missing: " + SpriteRoot);

            EnsureFolder(OutputRoot);
            BuildWristStatus();
            BuildPlanningBoard();
            BuildInteractionMarkerSet();
            BuildMetaStatusPanel();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.UI] Built diegetic UI prefabs: wrist, planning board, interaction markers and meta status.");
        }

        private static void BuildWristStatus()
        {
            GameObject root = new GameObject("WristStatus_Diegetic");
            try
            {
                root.transform.localScale = Vector3.one;
                AddSprite(root.transform, "ui-001_", "active", "Wrist Frame", new Vector3(0f, 0f, 0f), 0.34f, 0);

                AddSprite(root.transform, "ui-002_", "normal", "Health", new Vector3(-0.105f, 0.025f, -0.006f), 0.072f, 3);
                AddSprite(root.transform, "ui-003_", "normal", "Fatigue", new Vector3(-0.035f, 0.025f, -0.006f), 0.072f, 3);
                AddSprite(root.transform, "ui-004_", "dry", "ColdWet", new Vector3(0.035f, 0.025f, -0.006f), 0.072f, 3);
                AddSprite(root.transform, "ui-005_", "minor", "Injury", new Vector3(0.105f, 0.025f, -0.006f), 0.072f, 3);

                AddSprite(root.transform, "ui-012_", "intact", "Shelter", new Vector3(-0.070f, -0.052f, -0.006f), 0.058f, 4);
                AddSprite(root.transform, "ui-013_", "strong", "Fire", new Vector3(0.0f, -0.052f, -0.006f), 0.058f, 4);
                AddSprite(root.transform, "ui-014_", "ready", "Signal", new Vector3(0.070f, -0.052f, -0.006f), 0.058f, 4);

                SavePrefab(root, OutputRoot + "/WristStatus_Diegetic.prefab");
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static void BuildPlanningBoard()
        {
            GameObject root = new GameObject("PlanningBoard_Diegetic");
            try
            {
                AddSprite(root.transform, "pl-001_", "populated", "Board", Vector3.zero, 0.92f, 0);
                AddSprite(root.transform, "pl-002_", "4_slots", "Time Slots", new Vector3(0f, 0.13f, -0.008f), 0.62f, 2);

                AddSprite(root.transform, "pl-003_", "idle", "Gather Token", new Vector3(-0.245f, -0.105f, -0.010f), 0.12f, 5);
                AddSprite(root.transform, "pl-004_", "idle", "Build Token", new Vector3(-0.082f, -0.105f, -0.010f), 0.12f, 5);
                AddSprite(root.transform, "pl-005_", "idle", "Scout Token", new Vector3(0.082f, -0.105f, -0.010f), 0.12f, 5);
                AddSprite(root.transform, "pl-006_", "idle", "Repair Token", new Vector3(0.245f, -0.105f, -0.010f), 0.12f, 5);

                AddSprite(root.transform, "pl-008_", "signal", "Camp Summary", new Vector3(-0.23f, 0.00f, -0.009f), 0.21f, 3);
                AddSprite(root.transform, "pl-010_", "current_objective", "Objective", new Vector3(0.23f, 0.00f, -0.009f), 0.21f, 3);

                var collider = root.AddComponent<BoxCollider>();
                collider.center = Vector3.zero;
                collider.size = new Vector3(0.96f, 0.50f, 0.018f);

                SavePrefab(root, OutputRoot + "/PlanningBoard_Diegetic.prefab");
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static void BuildInteractionMarkerSet()
        {
            GameObject root = new GameObject("InteractionMarkers_Diegetic");
            try
            {
                string[] prefixes = { "wk-001_", "wk-002_", "wk-003_", "wk-005_", "wk-010_", "wk-011_", "wk-013_" };
                string[] tokens = { "hover", "active", "valid", "primary", "warning", "warning", "active" };
                string[] names = { "Grab", "TwoHandCarry", "SnapZone", "Objective", "FireFuel", "ShelterRepair", "PlanningBoard" };

                for (int i = 0; i < prefixes.Length; i++)
                {
                    float x = (i - (prefixes.Length - 1) * 0.5f) * 0.105f;
                    AddSprite(root.transform, prefixes[i], tokens[i], names[i], new Vector3(x, 0f, 0f), 0.082f, i);
                }

                SavePrefab(root, OutputRoot + "/InteractionMarkers_Diegetic.prefab");
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static void BuildMetaStatusPanel()
        {
            GameObject root = new GameObject("MetaStatus_Diegetic");
            try
            {
                AddSprite(root.transform, "mn-004_", "default", "Pause Panel", Vector3.zero, 0.64f, 0, optional: true);
                AddSprite(root.transform, "mn-005_", "trying", "Reconnect", new Vector3(0f, -0.11f, -0.008f), 0.18f, 3, optional: true);
                AddSprite(root.transform, "wk-015_", "reconnecting", "Reconnect Icon", new Vector3(0f, 0.09f, -0.008f), 0.105f, 4, optional: true);
                SavePrefab(root, OutputRoot + "/MetaStatus_Diegetic.prefab");
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static SpriteRenderer AddSprite(
            Transform parent,
            string prefix,
            string preferredToken,
            string objectName,
            Vector3 localPosition,
            float targetWidthMeters,
            int sortingOrder,
            bool optional = false)
        {
            Sprite sprite = FindSprite(prefix, preferredToken);
            if (sprite == null)
            {
                if (optional)
                {
                    Debug.LogWarning("[ProjectOEN.Art.UI] Optional sprite not found: " + prefix + "*" + preferredToken);
                    return null;
                }
                throw new InvalidOperationException("Required production sprite not found: " + prefix + "*" + preferredToken);
            }

            GameObject go = new GameObject(objectName);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPosition;

            SpriteRenderer renderer = go.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.sortingOrder = sortingOrder;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            renderer.receiveShadows = false;

            float spriteWidth = Mathf.Max(0.0001f, sprite.bounds.size.x);
            float scale = targetWidthMeters / spriteWidth;
            go.transform.localScale = Vector3.one * scale;
            return renderer;
        }

        private static Sprite FindSprite(string prefix, string preferredToken)
        {
            string p = prefix.ToLowerInvariant();
            string token = (preferredToken ?? string.Empty).ToLowerInvariant();
            string[] guids = AssetDatabase.FindAssets("t:Sprite", new[] { SpriteRoot });

            List<string> candidates = guids
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(path => Path.GetFileNameWithoutExtension(path).ToLowerInvariant().StartsWith(p))
                .OrderBy(path => path, StringComparer.Ordinal)
                .ToList();

            if (candidates.Count == 0)
                return null;

            string chosen = string.IsNullOrEmpty(token)
                ? candidates[0]
                : candidates.FirstOrDefault(path => Path.GetFileNameWithoutExtension(path)
                    .ToLowerInvariant().Contains(token)) ?? candidates[0];

            return AssetDatabase.LoadAssetAtPath<Sprite>(chosen);
        }

        private static void SavePrefab(GameObject root, string path)
        {
            GameObject saved = PrefabUtility.SaveAsPrefabAsset(root, path);
            if (saved == null)
                throw new InvalidOperationException("Could not save diegetic UI prefab: " + path);
        }

        private static void EnsureFolder(string path)
        {
            string normalized = path.Replace('\\', '/').TrimEnd('/');
            if (AssetDatabase.IsValidFolder(normalized))
                return;

            string[] parts = normalized.Split('/');
            string current = parts[0];
            for (int i = 1; i < parts.Length; i++)
            {
                string next = current + "/" + parts[i];
                if (!AssetDatabase.IsValidFolder(next))
                    AssetDatabase.CreateFolder(current, parts[i]);
                current = next;
            }
        }
    }
}
