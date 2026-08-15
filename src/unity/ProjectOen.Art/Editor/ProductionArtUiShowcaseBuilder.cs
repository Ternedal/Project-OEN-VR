using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Builds a standalone physical-scale review scene for the generated diegetic
    /// UI prefabs. This is intentionally separate from StormnattenArtShowcase and
    /// from the M0b CoopGame build gate.
    /// </summary>
    public static class ProductionArtUiShowcaseBuilder
    {
        private const string UiPrefabRoot = "Assets/ProductionArt/UiPrefabs";
        private const string SceneRoot = "Assets/ProductionArt/Scenes";
        private const string ScenePath = SceneRoot + "/DiegeticUiArtShowcase.unity";

        [MenuItem("Project OEN/Art/Build Diegetic UI Showcase")]
        public static void BuildShowcase()
        {
            if (!AssetDatabase.IsValidFolder(UiPrefabRoot))
                throw new InvalidOperationException("Diegetic UI prefabs are missing. Run Build Diegetic UI Prefabs first.");

            EnsureFolder(SceneRoot);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            RenderSettings.skybox = null;
            RenderSettings.fog = false;
            RenderSettings.ambientIntensity = 1f;

            BuildReviewRig();
            BuildCamera();

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.UI] Built physical-scale diegetic UI showcase: " + ScenePath);
        }

        private static void BuildReviewRig()
        {
            var root = new GameObject("Diegetic UI Physical Scale Review");

            Place(root.transform, "WristStatus_Diegetic.prefab",
                new Vector3(-0.56f, 1.34f, 0.40f), new Vector3(0f, 0f, 0f), 1f,
                "Wrist Status - physical scale");

            Place(root.transform, "PlanningBoard_Diegetic.prefab",
                new Vector3(0.05f, 1.04f, 0.70f), new Vector3(0f, 0f, 0f), 1f,
                "Planning Board - physical scale");

            Place(root.transform, "InteractionMarkers_Diegetic.prefab",
                new Vector3(0.02f, 0.55f, 0.48f), new Vector3(0f, 0f, 0f), 1f,
                "Interaction Markers - physical scale");

            Place(root.transform, "MetaStatus_Diegetic.prefab",
                new Vector3(0.72f, 1.28f, 0.52f), new Vector3(0f, 0f, 0f), 0.78f,
                "Meta Status - physical scale");

            // One metre reference stick makes scale errors obvious in the editor,
            // but it is visual-only and deliberately has no collider.
            var reference = GameObject.CreatePrimitive(PrimitiveType.Cube);
            reference.name = "1m Scale Reference";
            reference.transform.SetParent(root.transform, false);
            reference.transform.position = new Vector3(-0.92f, 0.50f, 0.62f);
            reference.transform.localScale = new Vector3(0.025f, 1.0f, 0.025f);
            var collider = reference.GetComponent<Collider>();
            if (collider != null)
                UnityEngine.Object.DestroyImmediate(collider);
            var renderer = reference.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                renderer.receiveShadows = false;
            }
        }

        private static void BuildCamera()
        {
            var cameraGo = new GameObject("Diegetic UI Review Camera");
            cameraGo.tag = "MainCamera";
            cameraGo.transform.position = new Vector3(0f, 1.08f, -2.15f);
            cameraGo.transform.rotation = Quaternion.identity;

            var camera = cameraGo.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.035f, 0.050f, 0.055f, 1f);
            camera.fieldOfView = 54f;
            camera.nearClipPlane = 0.03f;
            camera.farClipPlane = 8f;
        }

        private static GameObject Place(
            Transform parent,
            string prefabName,
            Vector3 position,
            Vector3 euler,
            float scale,
            string instanceName)
        {
            string path = UiPrefabRoot + "/" + prefabName;
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null)
                throw new InvalidOperationException("Required diegetic UI prefab missing: " + path);

            GameObject instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (instance == null)
                throw new InvalidOperationException("Could not instantiate diegetic UI prefab: " + path);

            instance.name = instanceName;
            instance.transform.SetParent(parent, false);
            instance.transform.position = position;
            instance.transform.rotation = Quaternion.Euler(euler);
            instance.transform.localScale = Vector3.one * scale;
            return instance;
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
