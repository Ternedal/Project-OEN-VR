using System;
using System.Collections.Generic;
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
    /// Audits both the saved 6x3 visual matrix and real editor-side calls through
    /// ProductionArtPrefabStateController.SetState. This verifies that generated
    /// state sets select the intended prefabs and that state-local appearance
    /// profiles survive actual state replacement rather than only existing on disk.
    /// </summary>
    public static class ProductionArtStateTransitionShowcaseAudit
    {
        private const string ScenePath = ProductionArtStateTransitionShowcaseBuilder.ScenePath;
        private const int ExpectedLabelCount = 27;
        private const int TriangleHardLimit = 300000;

        [MenuItem("Project OEN/Art/Audit State Transition Showcase")]
        public static void AuditShowcase()
        {
            var errors = new List<string>();
            SceneAsset sceneAsset = AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath);
            if (sceneAsset == null)
                throw new InvalidOperationException("State-transition scene missing: " + ScenePath);

            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            if (EditorBuildSettings.scenes.Any(s => string.Equals(s.path, ScenePath, StringComparison.OrdinalIgnoreCase)))
                errors.Add("state-transition review scene must stay out of Android build settings");

            GameObject[] samples = SceneComponents<Transform>(scene)
                .Select(t => t.gameObject)
                .Where(go => go.name.StartsWith("StateSample_", StringComparison.Ordinal))
                .ToArray();
            if (samples.Length != ProductionArtStateTransitionShowcaseBuilder.ExpectedSampleCount)
                errors.Add("expected " + ProductionArtStateTransitionShowcaseBuilder.ExpectedSampleCount + " state samples, found " + samples.Length);

            Collider[] colliders = SceneComponents<Collider>(scene);
            if (colliders.Length != 0)
                errors.Add("state-transition review must contain 0 colliders, found " + colliders.Length);

            ParticleSystem[] particles = SceneComponents<ParticleSystem>(scene);
            if (particles.Length != 0)
                errors.Add("state-transition review must contain 0 particle systems, found " + particles.Length);

            ProductionArtWetnessDriver[] wetnessDrivers = SceneComponents<ProductionArtWetnessDriver>(scene);
            if (wetnessDrivers.Length != 0)
                errors.Add("state-transition review isolates state-local appearance and must contain 0 wetness drivers");

            ProductionArtPrefabStateController[] savedControllers = SceneComponents<ProductionArtPrefabStateController>(scene);
            if (savedControllers.Length != 0)
                errors.Add("saved review matrix must remain static; runtime controllers are exercised transiently by the audit");

            Light[] lights = SceneComponents<Light>(scene);
            if (lights.Length != 1 || lights[0].shadows != LightShadows.None)
                errors.Add("state-transition review requires exactly 1 shadowless light");

            Camera[] cameras = SceneComponents<Camera>(scene);
            if (cameras.Length != 1 || !cameras[0].orthographic)
                errors.Add("state-transition review requires exactly 1 orthographic camera");

            GameObject labels = FindByName(scene, "State Transition Labels");
            if (labels == null || labels.transform.childCount != ExpectedLabelCount)
                errors.Add("expected " + ExpectedLabelCount + " state-transition label markers");

            long triangles = CountTriangles(scene);
            if (triangles > TriangleHardLimit)
                errors.Add("state-transition triangle proxy " + triangles + " exceeds hard limit " + TriangleHardLimit);

            foreach (Renderer renderer in SceneComponents<Renderer>(scene))
            {
                if (renderer.shadowCastingMode != ShadowCastingMode.Off || renderer.receiveShadows)
                    errors.Add("review renderer has realtime shadows enabled: " + renderer.name);
                foreach (Material material in renderer.sharedMaterials)
                {
                    if (material != null && material.name.EndsWith(" (Instance)", StringComparison.Ordinal))
                        errors.Add("material instance detected in review scene: " + material.name);
                }
            }

            VerifyStaticMatrix(scene, errors);
            VerifyRuntimeTransitions(errors);

            if (errors.Count > 0)
            {
                Debug.LogError("[ProjectOEN.Art.StateTransition] FAIL\n - " + string.Join("\n - ", errors));
                throw new InvalidOperationException("State-transition showcase audit failed with " + errors.Count + " issue(s).");
            }

            Debug.Log("[ProjectOEN.Art.StateTransition] PASS: 18 visual samples + real controller transitions preserve canonical appearance; " +
                      triangles + " triangles, 0 colliders, 0 particles, 1 shadowless light, scene excluded from build settings.");
        }

        private static void VerifyStaticMatrix(Scene scene, List<string> errors)
        {
            foreach (ProductionArtStateTransitionShowcaseBuilder.RowSpec row in ProductionArtStateTransitionShowcaseBuilder.Rows)
            {
                for (int i = 0; i < row.states.Length; i++)
                {
                    string stateKey = row.states[i];
                    string objectName = ProductionArtStateTransitionShowcaseBuilder.SampleObjectName(row.assetId, stateKey);
                    GameObject sample = FindByName(scene, objectName);
                    if (sample == null)
                    {
                        errors.Add("missing static sample: " + row.assetId + "/" + stateKey);
                        continue;
                    }
                    VerifyAppearance(sample, row.expectedProfiles[i], "static " + row.assetId + "/" + stateKey, errors);
                }
            }
        }

        private static void VerifyRuntimeTransitions(List<string> errors)
        {
            foreach (ProductionArtStateTransitionShowcaseBuilder.RowSpec row in ProductionArtStateTransitionShowcaseBuilder.Rows)
            {
                ProductionArtPrefabStateSet stateSet;
                try
                {
                    stateSet = ProductionArtStateTransitionShowcaseBuilder.LoadStateSet(row.assetId);
                }
                catch (Exception ex)
                {
                    errors.Add("could not load state set " + row.assetId + ": " + ex.Message);
                    continue;
                }

                var fixture = new GameObject("__StateTransitionAudit_" + row.assetId);
                try
                {
                    ProductionArtPrefabStateController controller = fixture.AddComponent<ProductionArtPrefabStateController>();
                    controller.Configure(stateSet, fixture.transform, row.states[0]);
                    GameObject previous = null;

                    for (int i = 0; i < row.states.Length; i++)
                    {
                        string stateKey = row.states[i];
                        if (!controller.HasState(stateKey))
                        {
                            errors.Add("controller state set missing: " + row.assetId + "/" + stateKey);
                            continue;
                        }

                        previous = controller.CurrentInstance;
                        if (!controller.SetState(stateKey))
                        {
                            errors.Add("SetState returned false: " + row.assetId + "/" + stateKey);
                            continue;
                        }

                        if (previous != null)
                            errors.Add("previous state instance survived editor-side replacement: " + row.assetId + "/" + stateKey);
                        if (!string.Equals(controller.CurrentState, stateKey, StringComparison.OrdinalIgnoreCase))
                            errors.Add("controller CurrentState mismatch: " + row.assetId + "/" + stateKey);
                        if (controller.CurrentInstance == null)
                        {
                            errors.Add("controller produced no instance: " + row.assetId + "/" + stateKey);
                            continue;
                        }
                        if (controller.CurrentInstance.transform.parent != fixture.transform)
                            errors.Add("controller instance mounted outside fixture: " + row.assetId + "/" + stateKey);

                        VerifyAppearance(controller.CurrentInstance, row.expectedProfiles[i], "runtime " + row.assetId + "/" + stateKey, errors);
                    }
                }
                finally
                {
                    UnityEngine.Object.DestroyImmediate(fixture);
                }
            }
        }

        private static void VerifyAppearance(GameObject root, string expectedProfile, string label, List<string> errors)
        {
            ProductionArtStateAppearance[] appearances = root.GetComponentsInChildren<ProductionArtStateAppearance>(true);
            if (string.IsNullOrEmpty(expectedProfile))
            {
                if (appearances.Length != 0)
                    errors.Add(label + " should have no state-local appearance profile, found " + appearances.Length);
                return;
            }

            if (appearances.Length != 1)
            {
                errors.Add(label + " expected exactly one state-local appearance profile, found " + appearances.Length);
                return;
            }

            ProductionArtStateAppearance appearance = appearances[0];
            if (!string.Equals(appearance.ProfileKey, expectedProfile, StringComparison.Ordinal))
                errors.Add(label + " expected profile " + expectedProfile + ", found " + appearance.ProfileKey);
            if (appearance.NormalScaleMultiplier < 0.1f || appearance.NormalScaleMultiplier > 1.2f)
                errors.Add(label + " normal-scale multiplier out of bounds");
            if (appearance.EmissionScale < 0f || appearance.EmissionScale > 1.2f)
                errors.Add(label + " emission multiplier out of bounds");
            if (expectedProfile == "cs010-nearly-out-wet" && appearance.EmissionScale > 0.25f)
                errors.Add(label + " wet nearly-out campfire must keep strongly reduced emission");
        }

        private static T[] SceneComponents<T>(Scene scene) where T : Component
        {
            return scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<T>(true))
                .ToArray();
        }

        private static GameObject FindByName(Scene scene, string objectName)
        {
            foreach (Transform transform in SceneComponents<Transform>(scene))
            {
                if (transform.gameObject.name == objectName)
                    return transform.gameObject;
            }
            return null;
        }

        private static long CountTriangles(Scene scene)
        {
            long triangles = 0;
            foreach (MeshFilter filter in SceneComponents<MeshFilter>(scene))
            {
                if (filter.sharedMesh != null)
                    triangles += filter.sharedMesh.triangles.Length / 3;
            }
            foreach (SkinnedMeshRenderer renderer in SceneComponents<SkinnedMeshRenderer>(scene))
            {
                if (renderer.sharedMesh != null)
                    triangles += renderer.sharedMesh.triangles.Length / 3;
            }
            return triangles;
        }
    }
}
