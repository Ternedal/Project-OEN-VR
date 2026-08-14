using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Builds a standalone Stormnatten visual-review scene from the generated
    /// production prefabs. This scene is intentionally NOT added to the M0b
    /// network/performance build list; CoopGame.unity must remain the minimal
    /// 72 Hz feasibility scene.
    ///
    /// The showcase gives the art pack a concrete, reproducible composition:
    /// cool storm ambience, one shadow-casting moon/key light, storm-damaged
    /// shelter/fire/signal states, wet camp dressing, repair/storage/rain-catcher
    /// dressing, radio/crates, real puddle/shoreline decal states, shipwreck and
    /// jungle framing.
    /// </summary>
    public static class ProductionArtShowcaseBuilder
    {
        private const string PrefabRoot = "Assets/ProjectOEN/ProductionArt/Prefabs";
        private const string MaterialRoot = "Assets/ProjectOEN/ProductionArt/UnityMaterials";
        private const string SceneRoot = "Assets/ProjectOEN/ProductionArt/Scenes";
        private const string ScenePath = SceneRoot + "/StormnattenArtShowcase.unity";

        private static readonly List<string> Missing = new List<string>();

        [MenuItem("Project OEN/Art/Build Stormnatten Art Showcase")]
        public static void BuildShowcase()
        {
            Missing.Clear();
            if (!AssetDatabase.IsValidFolder(PrefabRoot))
            {
                Debug.LogError("[ProjectOEN.Art] Production prefabs are missing. Run Build Production Art Prefabs first.");
                return;
            }

            EnsureFolder(SceneRoot);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            ConfigureEnvironment();
            BuildGround();
            BuildGroundWeatherAccents();
            BuildCampComposition();
            BuildCampDressing();
            BuildSignalComposition();
            BuildBeachWreckage();
            BuildVegetationFrame();
            BuildPreviewCamera();

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            if (Missing.Count == 0)
            {
                Debug.Log("[ProjectOEN.Art] Built Stormnatten art showcase: " + ScenePath);
            }
            else
            {
                Debug.LogWarning("[ProjectOEN.Art] Built Stormnatten art showcase with " + Missing.Count +
                                 " optional/missing prefab request(s): " + string.Join(", ", Missing));
            }
        }

        private static void ConfigureEnvironment()
        {
            RenderSettings.skybox = null;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.105f, 0.145f, 0.185f);
            RenderSettings.ambientEquatorColor = new Color(0.075f, 0.105f, 0.120f);
            RenderSettings.ambientGroundColor = new Color(0.035f, 0.045f, 0.045f);
            RenderSettings.ambientIntensity = 0.82f;
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.085f, 0.115f, 0.135f);
            RenderSettings.fogStartDistance = 11f;
            RenderSettings.fogEndDistance = 34f;

            QualitySettings.shadowDistance = 24f;

            var key = new GameObject("Storm Key Light").AddComponent<Light>();
            key.type = LightType.Directional;
            key.color = new Color(0.66f, 0.78f, 0.92f);
            key.intensity = 0.82f;
            key.shadows = LightShadows.Soft;
            key.shadowStrength = 0.68f;
            key.shadowBias = 0.07f;
            key.transform.rotation = Quaternion.Euler(48f, -32f, 0f);

            // Non-shadowing horizon fill keeps silhouettes readable without adding
            // another expensive shadow caster on Quest 2.
            var fill = new GameObject("Cool Horizon Fill").AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.color = new Color(0.20f, 0.31f, 0.38f);
            fill.intensity = 0.24f;
            fill.shadows = LightShadows.None;
            fill.transform.rotation = Quaternion.Euler(18f, 142f, 0f);
        }

        private static void BuildGround()
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Stormnatten Ground";
            ground.transform.position = new Vector3(0f, -0.02f, 0f);
            ground.transform.localScale = new Vector3(4.4f, 1f, 4.4f);

            var material = AssetDatabase.LoadAssetAtPath<Material>(MaterialRoot + "/mud.mat");
            var renderer = ground.GetComponent<Renderer>();
            if (renderer != null && material != null)
                renderer.sharedMaterial = material;

            MarkEnvironmentStatic(ground);
        }

        private static void BuildGroundWeatherAccents()
        {
            // These holder-prefabs receive state-specific transparent materials from
            // ProductionArtDecalBuilder before the showcase is authored.
            Place("en-011_", "large", new Vector3(0.75f, 0.004f, -1.75f), 12f, 1.45f, "Wet Mud Puddle Large", false);
            Place("en-011_", "medium", new Vector3(-3.15f, 0.003f, 2.20f), -19f, 0.95f, "Wet Mud Puddle Medium", false);
            Place("en-025_", "storm", new Vector3(0.15f, 0.002f, -7.25f), -4f, 4.10f, "Storm Shoreline Foam", false);
        }

        private static void BuildCampComposition()
        {
            // Stormnatten should read as active pressure, not a calm pre-storm camp.
            // Use the canonical storm-damaged shelter and nearly-out/wet fire states.
            Place("cs-004_", "", new Vector3(-1.5f, 0f, 1.0f), 18f, 1.35f, "Storm-Damaged Shelter", true);
            Place("cs-010_", "", new Vector3(0.0f, 0f, 0.15f), 0f, 1.0f, "Campfire Nearly Out Wet", false);

            Place("pr-005_", "active", new Vector3(-0.65f, 0.12f, -0.75f), -18f, 0.82f, "Portable Radio", false);
            Place("pr-004_", "closed", new Vector3(1.15f, 0f, 0.55f), -22f, 0.86f, "Supply Crate", false);
            Place("pr-020_", "idle", new Vector3(1.55f, 0f, -0.55f), 12f, 0.82f, "Shared Carry Box", false);
            Place("pr-002_", "coil", new Vector3(0.55f, 0.04f, 1.3f), 15f, 0.9f, "Rope Coil", false);
            Place("pr-003_", "bundle", new Vector3(-0.15f, 0.02f, 1.55f), 82f, 0.88f, "Wood Bundle", false);

            // PR-001 has a dedicated wet production state. Keeping it loose next
            // to the damaged shelter makes the storm consequence readable at a glance.
            Place("pr-001_", "wet", new Vector3(-2.42f, 0.025f, 0.08f), 48f, 0.92f, "Wet Tarp", false);
        }

        private static void BuildCampDressing()
        {
            Place("en-016_", "wet", new Vector3(-1.10f, 0.012f, -0.38f), -9f, 0.82f, "Wet Camp Groundsheet", false);
            Place("cs-016_", "mid_repair", new Vector3(-3.25f, 0f, -0.10f), 12f, 0.95f, "Radio Repair Station", false);
            Place("en-017_", "pot", new Vector3(0.62f, 0f, -0.05f), -18f, 0.80f, "Cooking Corner Pot", false);
            Place("en-018_", "sack", new Vector3(1.72f, 0f, 1.20f), -28f, 0.92f, "Storage Sack", false);

            // Rain catcher components are authored as individual master-list assets;
            // place the three states/components together as one readable camp cluster.
            Vector3 catcher = new Vector3(2.95f, 0f, 1.85f);
            Place("en-020_", "frame", catcher, -8f, 0.88f, "Rain Catcher Frame", true);
            Place("en-020_", "cloth", catcher + new Vector3(0f, 0.02f, 0f), -8f, 0.88f, "Rain Catcher Cloth", false);
            Place("en-020_", "basin", catcher + new Vector3(0f, 0.01f, 0f), -8f, 0.88f, "Rain Catcher Basin", false);

            Place("en-023_", "loose_cloth", new Vector3(-2.35f, 0.01f, 2.78f), 31f, 0.78f, "Loose Storm Cloth", false);
        }

        private static void BuildSignalComposition()
        {
            // The finale objective is visibly under storm pressure: use the
            // canonical damaged beacon and storm-damaged signal-cloth states.
            Place("cs-015_", "", new Vector3(5.4f, 0f, 5.8f), -28f, 1.25f, "Signal Beacon Storm Damaged", true);
            // Keep this scene-object name stable because the wind-response builder
            // targets it, while the underlying prefab state is storm_damaged.
            Place("pr-014_", "storm_damaged", new Vector3(4.85f, 0f, 5.15f), -12f, 1.0f, "Signal Cloth", true);
            Place("en-019_", "logs", new Vector3(4.45f, 0f, 6.50f), 26f, 0.90f, "Signal Fuel Logs", true);
            Place("en-019_", "ropes", new Vector3(5.75f, 0f, 4.95f), -18f, 0.78f, "Signal Spare Ropes", false);
            Place("en-019_", "stones", new Vector3(6.25f, 0f, 6.05f), 0f, 0.92f, "Signal Hill Stones", true);
        }

        private static void BuildBeachWreckage()
        {
            Place("en-001_", "large", new Vector3(-6.4f, 0f, -3.8f), 32f, 1.45f, "Shipwreck Hull", true);
            Place("en-002_", "medium", new Vector3(-4.25f, 0f, -2.2f), -16f, 1.0f, "Broken Planks", true);
            Place("en-003_", "broken", new Vector3(-3.55f, 0f, -3.15f), 24f, 0.9f, "Broken Barrel", true);
            Place("en-004_", "medium", new Vector3(-5.05f, 0.02f, -1.65f), -14f, 0.95f, "Rope Debris", false);
            Place("en-005_", "medium", new Vector3(3.15f, 0f, -3.8f), 0f, 1.15f, "Beach Stones A", true);
            Place("en-005_", "small", new Vector3(4.4f, 0f, -2.75f), 76f, 0.8f, "Beach Stones B", true);
            Place("en-006_", "large", new Vector3(-0.75f, 0f, -4.65f), 68f, 1.15f, "Driftwood", true);
        }

        private static void BuildVegetationFrame()
        {
            Place("en-007_", "mature", new Vector3(-7.0f, 0f, 4.8f), 12f, 1.35f, "Palm Mature A", true);
            Place("en-007_", "mature", new Vector3(7.5f, 0f, 2.9f), -38f, 1.12f, "Palm Mature B", true);
            Place("en-007_", "broken", new Vector3(5.8f, 0f, -5.5f), 34f, 1.0f, "Palm Broken", true);

            Place("en-008_", "medium", new Vector3(-2.9f, 0f, 4.0f), 15f, 1.0f, "Palm Frond Clutter A", true);
            Place("en-008_", "small", new Vector3(3.6f, 0f, 3.65f), -46f, 0.9f, "Palm Frond Clutter B", true);
            Place("en-009_", "dense", new Vector3(-5.3f, 0f, 5.7f), 35f, 1.15f, "Broadleaf Bush A", true);
            Place("en-009_", "medium", new Vector3(6.1f, 0f, 6.6f), -15f, 0.95f, "Broadleaf Bush B", true);
            Place("en-010_", "hanging", new Vector3(-6.25f, 0f, 2.9f), 10f, 1.0f, "Vines", true);
            Place("en-013_", "dense", new Vector3(7.15f, 0f, -1.30f), -20f, 1.1f, "Cliff Edge Grass", true);
        }

        private static void BuildPreviewCamera()
        {
            var cameraGo = new GameObject("Art Review Camera");
            cameraGo.tag = "MainCamera";
            cameraGo.transform.position = new Vector3(7.4f, 3.15f, -8.8f);
            cameraGo.transform.rotation = Quaternion.Euler(10.5f, -39f, 0f);

            var camera = cameraGo.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = RenderSettings.fogColor;
            camera.fieldOfView = 58f;
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 45f;
        }

        private static GameObject Place(
            string prefix,
            string preferredToken,
            Vector3 position,
            float yaw,
            float scale,
            string instanceName,
            bool environmentStatic)
        {
            GameObject prefab = FindPrefab(prefix, preferredToken);
            if (prefab == null)
            {
                Missing.Add(prefix + (string.IsNullOrEmpty(preferredToken) ? string.Empty : "*" + preferredToken));
                return null;
            }

            var instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (instance == null)
            {
                Missing.Add(prefix + "(instantiate)");
                return null;
            }

            instance.name = instanceName;
            instance.transform.position = position;
            instance.transform.rotation = Quaternion.Euler(0f, yaw, 0f);
            instance.transform.localScale = Vector3.one * scale;

            if (environmentStatic)
                MarkEnvironmentStatic(instance);

            return instance;
        }

        private static GameObject FindPrefab(string prefix, string preferredToken)
        {
            string p = prefix.ToLowerInvariant();
            string token = (preferredToken ?? string.Empty).ToLowerInvariant();
            string[] guids = AssetDatabase.FindAssets("t:Prefab", new[] { PrefabRoot });

            var candidates = guids
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

            return AssetDatabase.LoadAssetAtPath<GameObject>(chosen);
        }

        private static void MarkEnvironmentStatic(GameObject root)
        {
            var flags = StaticEditorFlags.BatchingStatic |
                        StaticEditorFlags.OccluderStatic |
                        StaticEditorFlags.OccludeeStatic;

            foreach (Transform t in root.GetComponentsInChildren<Transform>(true))
                GameObjectUtility.SetStaticEditorFlags(t.gameObject, flags);
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
