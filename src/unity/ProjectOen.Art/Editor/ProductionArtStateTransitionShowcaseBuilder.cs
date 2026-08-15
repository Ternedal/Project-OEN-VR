using System;
using System.Linq;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Builds an isolated 6x3 state-transition matrix for the canonical world-art
    /// states most important to Stormnatten. The scene isolates state-local art
    /// appearance from global wetness so baseline, pressure and aftermath/recovery
    /// reads can be compared directly.
    ///
    /// It is visual QA only: no build-settings changes, no particles, no runtime
    /// update loops and no material clones.
    /// </summary>
    public static class ProductionArtStateTransitionShowcaseBuilder
    {
        public const string ScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/StateTransitionShowcase.unity";
        public const int ExpectedSampleCount = 18;

        private const string SceneRoot = "Assets/ProjectOEN/ProductionArt/Scenes";
        private const string StateSetRoot = "Assets/ProjectOEN/ProductionArt/StateSets";
        private const float FirstRowY = 5.15f;
        private const float RowSpacing = 2.05f;

        private static readonly float[] ColumnX = { -3.75f, 0.00f, 3.75f };
        private static readonly string[] ColumnLabels = { "BASELINE", "PRESSURE", "AFTERMATH / WET" };

        internal readonly struct RowSpec
        {
            public readonly string label;
            public readonly string assetId;
            public readonly string[] states;
            public readonly string[] expectedProfiles;
            public readonly float displayScale;
            public readonly float yaw;

            public RowSpec(string rowLabel, string setAssetId, string[] stateKeys, string[] profileKeys, float scale, float rotationYaw)
            {
                label = rowLabel;
                assetId = setAssetId;
                states = stateKeys;
                expectedProfiles = profileKeys;
                displayScale = scale;
                yaw = rotationYaw;
            }
        }

        internal static readonly RowSpec[] Rows =
        {
            new RowSpec(
                "Shelter", "WORLD-SHELTER",
                new[] { "covered_usable", "damaged", "repaired_reinforced" },
                new string[] { null, "cs004-damaged", "cs005-repaired" },
                0.60f, 18f),
            new RowSpec(
                "Campfire", "WORLD-CAMPFIRE",
                new[] { "strong_flame", "nearly_out_wet", "small_flame" },
                new string[] { null, "cs010-nearly-out-wet", null },
                1.10f, 10f),
            new RowSpec(
                "Signal Beacon", "WORLD-SIGNAL-BEACON",
                new[] { "complete", "storm_damaged", "lit_active" },
                new string[] { null, "cs015-storm-damaged", null },
                0.62f, 18f),
            new RowSpec(
                "Tarp", "PR-001",
                new[] { "placed", "damaged", "wet" },
                new string[] { null, "pr001-damaged", "pr001-wet" },
                0.95f, 24f),
            new RowSpec(
                "Groundsheet", "EN-016",
                new[] { "clean", "worn", "wet" },
                new string[] { null, "en016-worn", "en016-wet" },
                1.05f, 20f),
            new RowSpec(
                "Signal Cloth", "PR-014",
                new[] { "clean", "worn", "storm_damaged" },
                new string[] { null, "pr014-worn", "pr014-storm-damaged" },
                1.05f, 22f),
        };

        [MenuItem("Project OEN/Art/Build State Transition Showcase")]
        public static void BuildShowcase()
        {
            EnsureFolder(SceneRoot);
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            ConfigureLighting();
            BuildCamera();
            Font font = LoadBuiltinFont();
            var labels = new GameObject("State Transition Labels");
            var matrix = new GameObject("State Transition Matrix");

            for (int column = 0; column < ColumnLabels.Length; column++)
                CreateLabel(labels.transform, "Header_" + column, ColumnLabels[column], new Vector3(ColumnX[column], 7.05f, -1.0f), font, true);

            int sampleCount = 0;
            for (int rowIndex = 0; rowIndex < Rows.Length; rowIndex++)
            {
                RowSpec row = Rows[rowIndex];
                float y = FirstRowY - rowIndex * RowSpacing;
                ProductionArtPrefabStateSet stateSet = LoadStateSet(row.assetId);

                CreateLabel(labels.transform, "Row_" + Slug(row.assetId), row.label.ToUpperInvariant(), new Vector3(-6.20f, y, -1.0f), font, false);

                for (int column = 0; column < row.states.Length; column++)
                {
                    string stateKey = row.states[column];
                    GameObject prefab;
                    if (!stateSet.TryGetPrefab(stateKey, out prefab) || prefab == null)
                        throw new InvalidOperationException("State-transition prefab missing: " + row.assetId + "/" + stateKey);

                    GameObject instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
                    if (instance == null)
                        throw new InvalidOperationException("Could not instantiate state-transition sample: " + row.assetId + "/" + stateKey);

                    instance.name = SampleObjectName(row.assetId, stateKey);
                    instance.transform.SetParent(matrix.transform, false);
                    instance.transform.localPosition = new Vector3(ColumnX[column], y, 0f);
                    instance.transform.localRotation = Quaternion.Euler(0f, row.yaw, 0f);
                    instance.transform.localScale = Vector3.one * row.displayScale;

                    StripReviewOnlyCost(instance);
                    ProductionArtStateAppearance appearance = instance.GetComponentInChildren<ProductionArtStateAppearance>(true);
                    if (appearance != null)
                        appearance.ApplyAppearance();

                    CreateLabel(
                        labels.transform,
                        "State_" + Slug(row.assetId) + "_" + Slug(stateKey),
                        stateKey.Replace('_', ' ').ToUpperInvariant(),
                        new Vector3(ColumnX[column], y - 0.76f, -1.0f),
                        font,
                        false);
                    sampleCount++;
                }
            }

            if (sampleCount != ExpectedSampleCount)
                throw new InvalidOperationException("State-transition matrix expected " + ExpectedSampleCount + " samples, built " + sampleCount + ".");

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.StateTransition] Built " + ExpectedSampleCount +
                      " side-by-side state samples in: " + ScenePath);
        }

        [MenuItem("Project OEN/Art/Open State Transition Showcase")]
        public static void OpenShowcase()
        {
            SceneAsset scene = AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath);
            if (scene == null)
                throw new InvalidOperationException("State-transition scene missing. Build it first: " + ScenePath);
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Selection.activeObject = scene;
        }

        internal static ProductionArtPrefabStateSet LoadStateSet(string assetId)
        {
            string[] guids = AssetDatabase.FindAssets("t:ProductionArtPrefabStateSet", new[] { StateSetRoot });
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                ProductionArtPrefabStateSet set = AssetDatabase.LoadAssetAtPath<ProductionArtPrefabStateSet>(path);
                if (set != null && string.Equals(set.AssetId, assetId, StringComparison.Ordinal))
                    return set;
            }
            throw new InvalidOperationException("Production state set missing for state-transition review: " + assetId);
        }

        internal static string SampleObjectName(string assetId, string stateKey)
        {
            return "StateSample_" + Slug(assetId) + "_" + Slug(stateKey);
        }

        private static void StripReviewOnlyCost(GameObject root)
        {
            foreach (Collider collider in root.GetComponentsInChildren<Collider>(true))
                UnityEngine.Object.DestroyImmediate(collider);

            foreach (ParticleSystem particleSystem in root.GetComponentsInChildren<ParticleSystem>(true))
                UnityEngine.Object.DestroyImmediate(particleSystem);

            foreach (Light light in root.GetComponentsInChildren<Light>(true))
                UnityEngine.Object.DestroyImmediate(light);

            foreach (Renderer renderer in root.GetComponentsInChildren<Renderer>(true))
            {
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.lightProbeUsage = LightProbeUsage.Off;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            }
        }

        private static void ConfigureLighting()
        {
            RenderSettings.fog = false;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.39f, 0.43f, 0.49f, 1f);
            RenderSettings.ambientEquatorColor = new Color(0.22f, 0.25f, 0.29f, 1f);
            RenderSettings.ambientGroundColor = new Color(0.09f, 0.10f, 0.12f, 1f);
            RenderSettings.reflectionIntensity = 0.55f;

            var lightGo = new GameObject("State Transition Key");
            lightGo.transform.rotation = Quaternion.Euler(38f, -34f, 0f);
            Light light = lightGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = new Color(0.96f, 0.98f, 1.00f, 1f);
            light.intensity = 1.05f;
            light.shadows = LightShadows.None;
        }

        private static void BuildCamera()
        {
            var cameraGo = new GameObject("State Transition Camera");
            cameraGo.tag = "MainCamera";
            cameraGo.transform.position = new Vector3(0f, 0.45f, -24f);
            cameraGo.transform.rotation = Quaternion.identity;

            Camera camera = cameraGo.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.055f, 0.061f, 0.073f, 1f);
            camera.orthographic = true;
            camera.orthographicSize = 8.05f;
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 45f;
        }

        private static Font LoadBuiltinFont()
        {
            Font font = null;
            try { font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"); }
            catch { }
            if (font != null)
                return font;

            try { font = Resources.GetBuiltinResource<Font>("Arial.ttf"); }
            catch { }
            return font;
        }

        private static void CreateLabel(Transform parent, string objectName, string text, Vector3 position, Font font, bool header)
        {
            var go = new GameObject(objectName);
            go.transform.SetParent(parent, false);
            go.transform.position = position;
            if (font == null)
                return;

            TextMesh label = go.AddComponent<TextMesh>();
            label.text = text;
            label.font = font;
            label.fontSize = 64;
            label.characterSize = header ? 0.065f : 0.043f;
            label.anchor = TextAnchor.MiddleCenter;
            label.alignment = TextAlignment.Center;
            label.color = header ? Color.white : new Color(0.80f, 0.84f, 0.90f, 1f);

            MeshRenderer renderer = go.GetComponent<MeshRenderer>();
            if (renderer != null)
            {
                renderer.sharedMaterial = font.material;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.lightProbeUsage = LightProbeUsage.Off;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            }
        }

        private static string Slug(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
                return "default";
            char[] chars = value.ToLowerInvariant().Select(c => char.IsLetterOrDigit(c) ? c : '_').ToArray();
            string result = new string(chars);
            while (result.Contains("__")) result = result.Replace("__", "_");
            return result.Trim('_');
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path))
                return;
            string parent = path.Substring(0, path.LastIndexOf('/'));
            string name = path.Substring(path.LastIndexOf('/') + 1);
            if (!AssetDatabase.IsValidFolder(parent))
                EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, name);
        }
    }
}
