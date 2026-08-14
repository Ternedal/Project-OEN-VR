using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Builds an isolated review scene for the generated VFX prefabs/materials.
    /// The scene is intentionally not part of Android build settings and keeps
    /// all VFX review cost away from Stormnatten/M0b performance gates.
    /// </summary>
    public static class ProductionArtVfxShowcaseBuilder
    {
        private const string PrefabRoot = "Assets/ProjectOEN/ProductionArt/VfxPrefabs";
        private const string MaterialRoot = "Assets/ProjectOEN/ProductionArt/VfxMaterials";
        private const string SceneRoot = "Assets/ProjectOEN/ProductionArt/Scenes";
        private const string ScenePath = SceneRoot + "/ProductionVfxShowcase.unity";

        [MenuItem("Project OEN/Art/Build Production VFX Showcase")]
        public static void BuildShowcase()
        {
            if (!AssetDatabase.IsValidFolder(PrefabRoot))
                throw new InvalidOperationException("VFX prefabs are missing. Run Build Production VFX first.");

            EnsureFolder(SceneRoot);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            RenderSettings.skybox = null;
            RenderSettings.fog = false;
            RenderSettings.ambientIntensity = 1f;

            GameObject root = new GameObject("Production VFX Review Grid");

            // Particle rows: smoke, ember, ash, rain splash. Prefabs stay
            // playOnAwake=false; the scene is for controlled editor/play review.
            Place(root.transform, "fx_001_small_smoke.prefab",  new Vector3(-1.50f, 1.30f, 0.5f));
            Place(root.transform, "fx_001_medium_smoke.prefab", new Vector3(-0.70f, 1.30f, 0.5f));
            Place(root.transform, "fx_002_small_ember.prefab",  new Vector3( 0.20f, 1.30f, 0.5f));
            Place(root.transform, "fx_002_medium_ember.prefab", new Vector3( 0.90f, 1.30f, 0.5f));
            Place(root.transform, "fx_003_single_ash.prefab",   new Vector3( 1.55f, 1.30f, 0.5f));
            Place(root.transform, "fx_004_small_rain_splash.prefab",  new Vector3(-0.55f, 0.62f, 0.5f));
            Place(root.transform, "fx_004_medium_rain_splash.prefab", new Vector3( 0.45f, 0.62f, 0.5f));

            // Billboard rows: lightning, glow, objective pulse.
            Place(root.transform, "fx_006_near_lightning.prefab", new Vector3(-1.45f, 2.20f, 0.8f));
            Place(root.transform, "fx_006_far_lightning.prefab",  new Vector3(-0.55f, 2.20f, 0.8f));
            Place(root.transform, "fx_007_fire_glow.prefab",      new Vector3( 0.25f, 2.05f, 0.8f));
            Place(root.transform, "fx_007_lantern_glow.prefab",   new Vector3( 0.85f, 2.05f, 0.8f));
            Place(root.transform, "fx_008_small_objective_pulse.prefab",  new Vector3(1.35f, 1.95f, 0.8f));
            Place(root.transform, "fx_008_medium_objective_pulse.prefab", new Vector3(1.85f, 1.95f, 0.8f));

            BuildWetSheenReview(root.transform);
            BuildCamera();

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.VFX] Built isolated VFX showcase: " + ScenePath);
        }

        private static void BuildWetSheenReview(Transform parent)
        {
            Material wet = AssetDatabase.LoadAssetAtPath<Material>(MaterialRoot + "/fx_005_single_wet_sheen.mat");
            if (wet == null)
                throw new InvalidOperationException("Wet sheen helper material is missing.");

            GameObject basePlane = GameObject.CreatePrimitive(PrimitiveType.Quad);
            basePlane.name = "Wet Sheen Dark Reference";
            basePlane.transform.SetParent(parent, false);
            basePlane.transform.position = new Vector3(1.15f, 0.52f, 0.72f);
            basePlane.transform.localScale = new Vector3(0.75f, 0.45f, 1f);
            DestroyCollider(basePlane);
            Renderer baseRenderer = basePlane.GetComponent<Renderer>();
            baseRenderer.shadowCastingMode = ShadowCastingMode.Off;
            baseRenderer.receiveShadows = false;
            Material baseMaterial = BuildReviewBaseMaterial();
            baseRenderer.sharedMaterial = baseMaterial;

            GameObject sheen = GameObject.CreatePrimitive(PrimitiveType.Quad);
            sheen.name = "Wet Sheen Helper";
            sheen.transform.SetParent(parent, false);
            sheen.transform.position = new Vector3(1.15f, 0.52f, 0.70f);
            sheen.transform.localScale = new Vector3(0.72f, 0.42f, 1f);
            DestroyCollider(sheen);
            Renderer sheenRenderer = sheen.GetComponent<Renderer>();
            sheenRenderer.shadowCastingMode = ShadowCastingMode.Off;
            sheenRenderer.receiveShadows = false;
            sheenRenderer.sharedMaterial = wet;
        }

        private static Material BuildReviewBaseMaterial()
        {
            const string path = MaterialRoot + "/vfx_review_dark_base.mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null) shader = Shader.Find("Unlit/Color");
            if (shader == null) throw new InvalidOperationException("No unlit shader for VFX review reference material.");
            if (material == null)
            {
                material = new Material(shader) { name = "VFX Review Dark Base" };
                AssetDatabase.CreateAsset(material, path);
            }
            else material.shader = shader;
            Color c = new Color(0.06f, 0.085f, 0.09f, 1f);
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", c);
            if (material.HasProperty("_Color")) material.SetColor("_Color", c);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static void BuildCamera()
        {
            GameObject cameraGo = new GameObject("VFX Review Camera");
            cameraGo.tag = "MainCamera";
            cameraGo.transform.position = new Vector3(0.15f, 1.38f, -4.0f);
            cameraGo.transform.rotation = Quaternion.Euler(0f, 0f, 0f);
            Camera camera = cameraGo.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.025f, 0.035f, 0.04f, 1f);
            camera.fieldOfView = 52f;
            camera.nearClipPlane = 0.03f;
            camera.farClipPlane = 12f;
        }

        private static GameObject Place(Transform parent, string prefabName, Vector3 position)
        {
            string path = PrefabRoot + "/" + prefabName;
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null)
                throw new InvalidOperationException("Required VFX prefab missing: " + path);
            GameObject instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (instance == null)
                throw new InvalidOperationException("Could not instantiate VFX prefab: " + path);
            instance.name = Path.GetFileNameWithoutExtension(prefabName) + " - review";
            instance.transform.SetParent(parent, false);
            instance.transform.position = position;
            return instance;
        }

        private static void DestroyCollider(GameObject go)
        {
            Collider c = go.GetComponent<Collider>();
            if (c != null) UnityEngine.Object.DestroyImmediate(c);
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
