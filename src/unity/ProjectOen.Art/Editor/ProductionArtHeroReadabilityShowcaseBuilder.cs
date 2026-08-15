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
    /// Builds an isolated physical-scale review scene for the canonical hero props
    /// and world anchors players must read quickly in VR. Every production prefab is
    /// instantiated from its runtime state set at 1:1 root scale, grounded by renderer
    /// bounds and grouped into near-field, co-op/heavy and world-anchor lanes.
    ///
    /// Visual QA only: no build-settings changes, no runtime update loops, no particles,
    /// no wetness driver and no realtime shadows.
    /// </summary>
    public static class ProductionArtHeroReadabilityShowcaseBuilder
    {
        public const string ScenePath = "Assets/ProductionArt/Scenes/HeroReadabilityShowcase.unity";
        public const int ExpectedSampleCount = 12;

        private const string SceneRoot = "Assets/ProductionArt/Scenes";
        private const string StateSetRoot = "Assets/ProductionArt/StateSets";
        private const float GroundOffset = 0.04f;

        internal readonly struct HeroSpec
        {
            public readonly string label;
            public readonly string assetId;
            public readonly string stateKey;
            public readonly Vector3 position;
            public readonly float yaw;
            public readonly float minDimension;
            public readonly float maxDimension;

            public HeroSpec(string sampleLabel, string id, string state, Vector3 samplePosition, float rotationYaw, float minSize, float maxSize)
            {
                label = sampleLabel;
                assetId = id;
                stateKey = state;
                position = samplePosition;
                yaw = rotationYaw;
                minDimension = minSize;
                maxDimension = maxSize;
            }
        }

        internal static readonly HeroSpec[] Specs =
        {
            new HeroSpec("Rope coil", "PR-002", "loose", new Vector3(-4.80f, 0f, 0.00f), 18f, 0.08f, 1.60f),
            new HeroSpec("Portable radio", "PR-005", "repaired", new Vector3(-3.20f, 0f, 0.00f), -12f, 0.08f, 1.50f),
            new HeroSpec("Canteen", "PR-007", "full", new Vector3(-1.60f, 0f, 0.00f), 20f, 0.05f, 0.90f),
            new HeroSpec("Oil lantern", "PR-008", "off", new Vector3(0.00f, 0f, 0.00f), -18f, 0.08f, 1.20f),
            new HeroSpec("Mallet", "PR-017", "clean", new Vector3(1.60f, 0f, 0.00f), 24f, 0.08f, 1.20f),
            new HeroSpec("Knife", "PR-018", "clean", new Vector3(3.20f, 0f, 0.00f), -28f, 0.05f, 0.80f),
            new HeroSpec("Anchor peg", "PR-019", "inactive", new Vector3(4.80f, 0f, 0.00f), 16f, 0.05f, 1.20f),

            new HeroSpec("Supply crate", "PR-004", "closed", new Vector3(-3.15f, 0f, 3.15f), 18f, 0.25f, 2.50f),
            new HeroSpec("Shared-carry box", "PR-020", "idle", new Vector3(0.00f, 0f, 3.15f), -15f, 0.35f, 3.20f),
            new HeroSpec("Placed tarp", "PR-001", "placed", new Vector3(3.15f, 0f, 3.15f), 10f, 0.40f, 4.50f),

            new HeroSpec("Usable shelter", "WORLD-SHELTER", "covered_usable", new Vector3(-3.45f, 0f, 7.65f), 18f, 0.70f, 9.00f),
            new HeroSpec("Signal beacon", "WORLD-SIGNAL-BEACON", "complete", new Vector3(3.45f, 0f, 7.65f), -18f, 0.70f, 9.00f),
        };

        [MenuItem("Project OEN/Art/Build Hero Readability Showcase")]
        public static void BuildShowcase()
        {
            EnsureFolder(SceneRoot);
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            ConfigureLighting();
            BuildCamera();
            Font font = LoadBuiltinFont();
            var labels = new GameObject("Hero Readability Labels");
            var samples = new GameObject("Hero Readability Samples");

            CreateLabel(labels.transform, "Title", "HERO PROP READABILITY - 1:1 ROOT SCALE", new Vector3(0f, 4.95f, -0.65f), font, 0.055f);
            CreateLabel(labels.transform, "Lane_Near", "HAND / NEAR-FIELD", new Vector3(0f, 2.00f, -0.80f), font, 0.050f);
            CreateLabel(labels.transform, "Lane_Heavy", "HEAVY / CO-OP", new Vector3(0f, 2.45f, 2.15f), font, 0.050f);
            CreateLabel(labels.transform, "Lane_World", "WORLD ANCHORS", new Vector3(0f, 4.20f, 6.25f), font, 0.050f);

            int built = 0;
            foreach (HeroSpec spec in Specs)
            {
                ProductionArtPrefabStateSet stateSet = LoadStateSet(spec.assetId);
                GameObject prefab;
                if (!stateSet.TryGetPrefab(spec.stateKey, out prefab) || prefab == null)
                    throw new InvalidOperationException("Hero-readability state missing: " + spec.assetId + "/" + spec.stateKey);

                GameObject instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
                if (instance == null)
                    throw new InvalidOperationException("Could not instantiate hero-readability sample: " + spec.assetId + "/" + spec.stateKey);

                instance.name = SampleObjectName(spec.assetId, spec.stateKey);
                instance.transform.SetParent(samples.transform, false);
                instance.transform.localPosition = spec.position;
                instance.transform.localRotation = Quaternion.Euler(0f, spec.yaw, 0f);
                instance.transform.localScale = Vector3.one;

                StripReviewOnlyCost(instance);
                ProductionArtStateAppearance appearance = instance.GetComponentInChildren<ProductionArtStateAppearance>(true);
                if (appearance != null)
                    appearance.ApplyAppearance();
                AlignToGround(instance);

                Bounds bounds = CombinedRendererBounds(instance);
                float labelY = Mathf.Clamp(bounds.max.y + 0.32f, 0.82f, 4.35f);
                CreateLabel(labels.transform,
                    "Label_" + Slug(spec.assetId) + "_" + Slug(spec.stateKey),
                    spec.label.ToUpperInvariant() + "\n" + spec.assetId + " / " + spec.stateKey.Replace('_', ' ').ToUpperInvariant(),
                    new Vector3(spec.position.x, labelY, spec.position.z - 0.30f),
                    font,
                    0.033f);
                built++;
            }

            if (built != ExpectedSampleCount)
                throw new InvalidOperationException("Hero-readability showcase expected " + ExpectedSampleCount + " samples, built " + built + ".");

            CreateScaleReference(labels.transform, font);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.HeroReadability] Built " + ExpectedSampleCount +
                      " canonical 1:1 hero/world samples in: " + ScenePath);
        }

        [MenuItem("Project OEN/Art/Open Hero Readability Showcase")]
        public static void OpenShowcase()
        {
            SceneAsset scene = AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath);
            if (scene == null)
                throw new InvalidOperationException("Hero-readability scene missing. Build it first: " + ScenePath);
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Selection.activeObject = scene;
        }

        internal static string SampleObjectName(string assetId, string stateKey)
        {
            return "HeroSample_" + Slug(assetId) + "_" + Slug(stateKey);
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
            throw new InvalidOperationException("Production state set missing for hero-readability review: " + assetId);
        }

        private static void AlignToGround(GameObject root)
        {
            Bounds bounds = CombinedRendererBounds(root);
            float delta = GroundOffset - bounds.min.y;
            root.transform.position += Vector3.up * delta;
        }

        internal static Bounds CombinedRendererBounds(GameObject root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true)
                .Where(r => !(r is ParticleSystemRenderer))
                .ToArray();
            if (renderers.Length == 0)
                throw new InvalidOperationException("Hero-readability sample has no renderer: " + root.name);

            Bounds bounds = renderers[0].bounds;
            for (int i = 1; i < renderers.Length; i++)
                bounds.Encapsulate(renderers[i].bounds);
            return bounds;
        }

        private static void StripReviewOnlyCost(GameObject root)
        {
            foreach (Collider collider in root.GetComponentsInChildren<Collider>(true))
                UnityEngine.Object.DestroyImmediate(collider);

            foreach (Renderer renderer in root.GetComponentsInChildren<Renderer>(true))
            {
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.lightProbeUsage = LightProbeUsage.Off;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            }
        }

        private static void CreateScaleReference(Transform labelRoot, Font font)
        {
            GameObject marker = GameObject.CreatePrimitive(PrimitiveType.Cube);
            marker.name = "Hero Readability Scale Reference";
            marker.transform.position = new Vector3(6.10f, 0.50f, -0.65f);
            marker.transform.localScale = new Vector3(0.035f, 1.00f, 0.035f);
            Collider collider = marker.GetComponent<Collider>();
            if (collider != null)
                UnityEngine.Object.DestroyImmediate(collider);
            Renderer renderer = marker.GetComponent<Renderer>();
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            renderer.lightProbeUsage = LightProbeUsage.Off;
            renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;

            CreateLabel(labelRoot, "ScaleReferenceLabel", "1 m", new Vector3(6.10f, 1.22f, -0.65f), font, 0.038f);
        }

        private static void ConfigureLighting()
        {
            RenderSettings.fog = false;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.40f, 0.44f, 0.50f, 1f);
            RenderSettings.ambientEquatorColor = new Color(0.23f, 0.26f, 0.30f, 1f);
            RenderSettings.ambientGroundColor = new Color(0.08f, 0.09f, 0.11f, 1f);
            RenderSettings.reflectionIntensity = 0.55f;

            var lightGo = new GameObject("Hero Readability Key");
            lightGo.transform.rotation = Quaternion.Euler(42f, -32f, 0f);
            Light light = lightGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = new Color(0.97f, 0.98f, 1.00f, 1f);
            light.intensity = 1.08f;
            light.shadows = LightShadows.None;
        }

        private static void BuildCamera()
        {
            var cameraGo = new GameObject("Hero Readability Camera");
            cameraGo.tag = "MainCamera";
            cameraGo.transform.position = new Vector3(0f, 5.15f, -15.40f);
            cameraGo.transform.LookAt(new Vector3(0f, 1.65f, 3.70f));

            Camera camera = cameraGo.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.052f, 0.058f, 0.070f, 1f);
            camera.orthographic = false;
            camera.fieldOfView = 48f;
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

        private static void CreateLabel(Transform parent, string objectName, string text, Vector3 position, Font font, float characterSize)
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
            label.characterSize = characterSize;
            label.anchor = TextAnchor.MiddleCenter;
            label.alignment = TextAlignment.Center;
            label.color = new Color(0.86f, 0.89f, 0.94f, 1f);
            label.GetComponent<MeshRenderer>().shadowCastingMode = ShadowCastingMode.Off;
            label.GetComponent<MeshRenderer>().receiveShadows = false;
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
