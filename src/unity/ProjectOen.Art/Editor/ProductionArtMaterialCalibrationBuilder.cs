using System;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Builds an isolated material-calibration scene for the 11 shared production
    /// materials. Every material is shown on the same primitive under identical
    /// lighting in three scoped wetness columns: dry (0.00), mid (0.40) and the
    /// Stormnatten reference (0.78).
    ///
    /// This scene is visual QA only. It is not added to Android build settings and
    /// uses the existing event-driven ProductionArtWetnessDriver without material
    /// clones, custom shaders, particle systems or per-frame scripts.
    /// </summary>
    public static class ProductionArtMaterialCalibrationBuilder
    {
        public const string ScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/MaterialCalibrationShowcase.unity";

        private const string SceneRoot = "Assets/ProjectOEN/ProductionArt/Scenes";
        private const string MaterialRoot = "Assets/ProjectOEN/ProductionArt/UnityMaterials";
        private const float RowSpacing = 1.34f;
        private const float FirstRowY = 6.70f;

        private static readonly string[] MaterialNames =
        {
            "Wood", "Rope", "Tarp", "Metal", "Stone", "Leaf",
            "Cloth", "Mud", "Fire", "Char", "Water"
        };

        private static readonly string[] ColumnNames = { "Dry", "Mid", "Storm" };
        private static readonly float[] ColumnWetness = { 0.00f, 0.40f, 0.78f };
        private static readonly float[] ColumnX = { -2.55f, 0.00f, 2.55f };

        [MenuItem("Project OEN/Art/Build Material Calibration Showcase")]
        public static void BuildShowcase()
        {
            EnsureFolder(SceneRoot);
            Material[] materials = LoadProductionMaterials();

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            ConfigureLighting();
            BuildCamera();
            BuildLabels();

            for (int columnIndex = 0; columnIndex < ColumnNames.Length; columnIndex++)
                BuildWetnessColumn(columnIndex, materials);

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[ProjectOEN.Art.Calibration] Built material calibration scene: " + ScenePath +
                      " (11 materials x 3 wetness states = 33 samples; wetness 0.00 / 0.40 / 0.78).");
        }

        private static Material[] LoadProductionMaterials()
        {
            var result = new Material[MaterialNames.Length];
            for (int i = 0; i < MaterialNames.Length; i++)
            {
                string path = MaterialRoot + "/" + MaterialNames[i].ToLowerInvariant() + ".mat";
                Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (material == null)
                    throw new InvalidOperationException("Production material missing. Run ProductionArtPrefabBuilder.BuildAll first: " + path);
                result[i] = material;
            }
            return result;
        }

        private static void BuildWetnessColumn(int columnIndex, Material[] materials)
        {
            float wetness = ColumnWetness[columnIndex];
            var root = new GameObject("Wetness " + ColumnNames[columnIndex] + " " + wetness.ToString("0.00"));
            root.transform.position = new Vector3(ColumnX[columnIndex], 0f, 0f);

            // Keep OnEnable from briefly applying the default scene-wide wetness
            // before scopeRoot has been assigned.
            root.SetActive(false);

            for (int materialIndex = 0; materialIndex < MaterialNames.Length; materialIndex++)
            {
                GameObject sample = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                sample.name = "Sample_" + MaterialNames[materialIndex];
                sample.transform.SetParent(root.transform, false);
                sample.transform.localPosition = new Vector3(0f, FirstRowY - materialIndex * RowSpacing, 0f);
                sample.transform.localScale = new Vector3(0.72f, 0.72f, 0.72f);

                Collider collider = sample.GetComponent<Collider>();
                if (collider != null)
                    UnityEngine.Object.DestroyImmediate(collider);

                Renderer renderer = sample.GetComponent<Renderer>();
                renderer.sharedMaterial = materials[materialIndex];
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.lightProbeUsage = LightProbeUsage.Off;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            }

            ProductionArtWetnessDriver driver = root.AddComponent<ProductionArtWetnessDriver>();
            var serialized = new SerializedObject(driver);
            SerializedProperty scope = serialized.FindProperty("scopeRoot");
            if (scope == null)
                throw new InvalidOperationException("ProductionArtWetnessDriver.scopeRoot serialized property is unavailable.");
            scope.objectReferenceValue = root.transform;
            serialized.ApplyModifiedPropertiesWithoutUndo();

            driver.SetWetness(wetness);
            EditorUtility.SetDirty(driver);
            root.SetActive(true);
            driver.ApplyWetness();
        }

        private static void ConfigureLighting()
        {
            RenderSettings.fog = false;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.46f, 0.49f, 0.54f, 1f);
            RenderSettings.ambientEquatorColor = new Color(0.28f, 0.30f, 0.34f, 1f);
            RenderSettings.ambientGroundColor = new Color(0.12f, 0.13f, 0.15f, 1f);
            RenderSettings.reflectionIntensity = 0.65f;

            var lightGo = new GameObject("Material Calibration Key");
            lightGo.transform.rotation = Quaternion.Euler(38f, -32f, 0f);
            Light light = lightGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = new Color(0.96f, 0.98f, 1.00f, 1f);
            light.intensity = 1.10f;
            light.shadows = LightShadows.None;
        }

        private static void BuildCamera()
        {
            var cameraGo = new GameObject("Material Calibration Camera");
            cameraGo.tag = "MainCamera";
            cameraGo.transform.position = new Vector3(0f, 0.65f, -20f);
            cameraGo.transform.rotation = Quaternion.identity;

            Camera camera = cameraGo.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.065f, 0.070f, 0.082f, 1f);
            camera.orthographic = true;
            camera.orthographicSize = 9.15f;
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 45f;
        }

        private static void BuildLabels()
        {
            var labelRoot = new GameObject("Calibration Labels");
            Font font = LoadBuiltinFont();

            for (int i = 0; i < ColumnNames.Length; i++)
                CreateLabel(labelRoot.transform, "Header_" + ColumnNames[i], ColumnNames[i].ToUpperInvariant() + "  " + ColumnWetness[i].ToString("0.00"), new Vector3(ColumnX[i], 8.18f, 0f), font, true);

            for (int i = 0; i < MaterialNames.Length; i++)
                CreateLabel(labelRoot.transform, "Row_" + MaterialNames[i], MaterialNames[i], new Vector3(-4.45f, FirstRowY - i * RowSpacing, 0f), font, false);
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

            // Keep hierarchy markers even if a Unity version has no compatible
            // built-in legacy font; the material samples remain fully reviewable.
            if (font == null)
                return;

            TextMesh label = go.AddComponent<TextMesh>();
            label.text = text;
            label.font = font;
            label.fontSize = 64;
            label.characterSize = header ? 0.070f : 0.052f;
            label.anchor = TextAnchor.MiddleCenter;
            label.alignment = TextAlignment.Center;
            label.color = header ? Color.white : new Color(0.80f, 0.83f, 0.88f, 1f);

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