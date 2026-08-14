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
    /// Unity-side hard gate for the hero-readability scene. It verifies that the
    /// canonical runtime prefabs remain at 1:1 root scale, grounded in metre space,
    /// readable within intentionally broad physical-size bands, and isolated from
    /// expensive runtime-only systems.
    /// </summary>
    public static class ProductionArtHeroReadabilityShowcaseAudit
    {
        private const string ScenePath = ProductionArtHeroReadabilityShowcaseBuilder.ScenePath;
        private const int TriangleHardLimit = 250000;
        private const int RendererHardLimit = 90;
        private const float ScaleTolerance = 0.001f;
        private const float GroundTolerance = 0.16f;

        [MenuItem("Project OEN/Art/Audit Hero Readability Showcase")]
        public static void AuditShowcase()
        {
            var errors = new List<string>();
            SceneAsset sceneAsset = AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath);
            if (sceneAsset == null)
                throw new InvalidOperationException("Hero-readability scene missing: " + ScenePath);

            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            if (EditorBuildSettings.scenes.Any(s => string.Equals(s.path, ScenePath, StringComparison.OrdinalIgnoreCase)))
                errors.Add("hero-readability review scene must stay out of Android build settings");

            GameObject[] samples = SceneComponents<Transform>(scene)
                .Select(t => t.gameObject)
                .Where(go => go.name.StartsWith("HeroSample_", StringComparison.Ordinal))
                .ToArray();
            if (samples.Length != ProductionArtHeroReadabilityShowcaseBuilder.ExpectedSampleCount)
                errors.Add("expected " + ProductionArtHeroReadabilityShowcaseBuilder.ExpectedSampleCount + " hero samples, found " + samples.Length);

            if (SceneComponents<Collider>(scene).Length != 0)
                errors.Add("hero-readability review must contain 0 colliders");
            if (SceneComponents<ParticleSystem>(scene).Length != 0)
                errors.Add("hero-readability review must contain 0 particle systems");
            if (SceneComponents<Animation>(scene).Length != 0 || SceneComponents<Animator>(scene).Length != 0)
                errors.Add("hero-readability review must contain 0 animation components");
            if (SceneComponents<ProductionArtWetnessDriver>(scene).Length != 0)
                errors.Add("hero-readability review must contain 0 wetness drivers");
            if (SceneComponents<ProductionArtPrefabStateController>(scene).Length != 0)
                errors.Add("hero-readability review must remain a static visual matrix with 0 runtime state controllers");

            Light[] lights = SceneComponents<Light>(scene);
            if (lights.Length != 1 || lights[0].type != LightType.Directional || lights[0].shadows != LightShadows.None)
                errors.Add("hero-readability review requires exactly 1 shadowless directional light");

            Camera[] cameras = SceneComponents<Camera>(scene);
            if (cameras.Length != 1 || cameras[0].orthographic)
                errors.Add("hero-readability review requires exactly 1 perspective camera");

            Renderer[] renderers = SceneComponents<Renderer>(scene);
            if (renderers.Length > RendererHardLimit)
                errors.Add("hero-readability renderer proxy " + renderers.Length + " exceeds hard limit " + RendererHardLimit);
            foreach (Renderer renderer in renderers)
            {
                if (renderer.shadowCastingMode != ShadowCastingMode.Off || renderer.receiveShadows)
                    errors.Add("hero-readability renderer has realtime shadows enabled: " + renderer.name);
                foreach (Material material in renderer.sharedMaterials)
                {
                    if (material != null && material.name.EndsWith(" (Instance)", StringComparison.Ordinal))
                        errors.Add("material instance detected in hero-readability scene: " + material.name);
                }
            }

            long triangles = CountTriangles(scene);
            if (triangles > TriangleHardLimit)
                errors.Add("hero-readability triangle proxy " + triangles + " exceeds hard limit " + TriangleHardLimit);

            VerifyScaleReference(scene, errors);
            foreach (ProductionArtHeroReadabilityShowcaseBuilder.HeroSpec spec in ProductionArtHeroReadabilityShowcaseBuilder.Specs)
                VerifySample(scene, spec, errors);

            if (errors.Count > 0)
            {
                Debug.LogError("[ProjectOEN.Art.HeroReadability] FAIL\n - " + string.Join("\n - ", errors));
                throw new InvalidOperationException("Hero-readability showcase audit failed with " + errors.Count + " issue(s).");
            }

            Debug.Log("[ProjectOEN.Art.HeroReadability] PASS: 12 canonical hero/world samples retain 1:1 root scale and physical metre-space readability; " +
                      triangles + " triangles, " + renderers.Length + " renderers, 0 colliders, 0 particles, 1 shadowless light, scene excluded from build settings.");
        }

        private static void VerifyScaleReference(Scene scene, List<string> errors)
        {
            GameObject marker = FindByName(scene, "Hero Readability Scale Reference");
            if (marker == null)
            {
                errors.Add("1 metre scale reference is missing");
                return;
            }

            Renderer renderer = marker.GetComponent<Renderer>();
            if (renderer == null)
            {
                errors.Add("1 metre scale reference has no renderer");
                return;
            }
            if (Mathf.Abs(renderer.bounds.size.y - 1f) > 0.06f)
                errors.Add("1 metre scale reference height drifted to " + renderer.bounds.size.y.ToString("0.000") + " m");
        }

        private static void VerifySample(Scene scene, ProductionArtHeroReadabilityShowcaseBuilder.HeroSpec spec, List<string> errors)
        {
            string objectName = ProductionArtHeroReadabilityShowcaseBuilder.SampleObjectName(spec.assetId, spec.stateKey);
            GameObject sample = FindByName(scene, objectName);
            if (sample == null)
            {
                errors.Add("missing hero-readability sample: " + spec.assetId + "/" + spec.stateKey);
                return;
            }

            Vector3 scale = sample.transform.localScale;
            if (Mathf.Abs(scale.x - 1f) > ScaleTolerance || Mathf.Abs(scale.y - 1f) > ScaleTolerance || Mathf.Abs(scale.z - 1f) > ScaleTolerance)
                errors.Add("hero sample root scale must remain 1:1: " + spec.assetId + "/" + spec.stateKey + " = " + scale);

            Bounds bounds;
            try
            {
                bounds = ProductionArtHeroReadabilityShowcaseBuilder.CombinedRendererBounds(sample);
            }
            catch (Exception ex)
            {
                errors.Add("could not measure hero sample " + spec.assetId + "/" + spec.stateKey + ": " + ex.Message);
                return;
            }

            float maxDimension = Mathf.Max(bounds.size.x, Mathf.Max(bounds.size.y, bounds.size.z));
            if (maxDimension < spec.minDimension || maxDimension > spec.maxDimension)
                errors.Add(spec.assetId + "/" + spec.stateKey + " physical max dimension " + maxDimension.ToString("0.000") +
                           " m is outside readability band " + spec.minDimension.ToString("0.00") + ".." + spec.maxDimension.ToString("0.00") + " m");

            if (bounds.min.y < -0.02f || bounds.min.y > GroundTolerance)
                errors.Add(spec.assetId + "/" + spec.stateKey + " is not grounded in metre space; bounds.min.y=" + bounds.min.y.ToString("0.000"));
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
                Mesh mesh = filter.sharedMesh;
                if (mesh != null)
                    triangles += mesh.triangles.LongLength / 3L;
            }
            foreach (SkinnedMeshRenderer renderer in SceneComponents<SkinnedMeshRenderer>(scene))
            {
                Mesh mesh = renderer.sharedMesh;
                if (mesh != null)
                    triangles += mesh.triangles.LongLength / 3L;
            }
            return triangles;
        }
    }
}
