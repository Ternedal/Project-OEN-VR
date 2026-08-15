using System;
using System.Collections.Generic;
using System.Linq;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Unity-machine hard gate for the isolated dry/mid/storm material review.
    /// It proves that all 11 shared production materials are present in all three
    /// columns and that scoped wetness affects exactly the nine intended surface
    /// families while Fire and Water remain untouched.
    /// </summary>
    public static class ProductionArtMaterialCalibrationAudit
    {
        private const string ScenePath = "Assets/ProductionArt/Scenes/MaterialCalibrationShowcase.unity";
        private const string MaterialRoot = "Assets/ProductionArt/UnityMaterials";
        private const int ExpectedSampleCount = 33;
        private const int ExpectedWettableCountPerColumn = 9;

        private static readonly string[] MaterialNames =
        {
            "Wood", "Rope", "Tarp", "Metal", "Stone", "Leaf",
            "Cloth", "Mud", "Fire", "Char", "Water"
        };

        private static readonly float[] ExpectedWetness = { 0.00f, 0.40f, 0.78f };

        [MenuItem("Project OEN/Art/Audit Material Calibration Showcase")]
        public static void AuditShowcase()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
                throw new InvalidOperationException("Material calibration scene missing: " + ScenePath);

            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

            var failures = new List<string>();
            ProductionArtWetnessDriver[] drivers = UnityEngine.Object.FindObjectsOfType<ProductionArtWetnessDriver>(true);
            Array.Sort(drivers, (a, b) => a.Wetness.CompareTo(b.Wetness));

            Renderer[] renderers = UnityEngine.Object.FindObjectsOfType<Renderer>(true);
            Renderer[] sampleRenderers = renderers
                .Where(r => r != null && r.gameObject.name.StartsWith("Sample_", StringComparison.Ordinal))
                .ToArray();
            Collider[] colliders = UnityEngine.Object.FindObjectsOfType<Collider>(true);
            ParticleSystem[] particles = UnityEngine.Object.FindObjectsOfType<ParticleSystem>(true);
            Light[] lights = UnityEngine.Object.FindObjectsOfType<Light>(true);
            Camera[] cameras = UnityEngine.Object.FindObjectsOfType<Camera>(true);

            if (drivers.Length != ExpectedWetness.Length)
                failures.Add("wetness drivers " + drivers.Length + " != " + ExpectedWetness.Length);
            if (sampleRenderers.Length != ExpectedSampleCount)
                failures.Add("sample renderers " + sampleRenderers.Length + " != " + ExpectedSampleCount);
            if (colliders.Length != 0)
                failures.Add("calibration scene must contain zero colliders, found " + colliders.Length);
            if (particles.Length != 0)
                failures.Add("calibration scene must contain zero particle systems, found " + particles.Length);
            if (lights.Length != 1)
                failures.Add("calibration scene must contain exactly one light, found " + lights.Length);
            else if (lights[0].shadows != LightShadows.None)
                failures.Add("calibration key light must not cast realtime shadows");
            if (cameras.Length != 1)
                failures.Add("calibration scene must contain exactly one camera, found " + cameras.Length);
            else if (!cameras[0].orthographic)
                failures.Add("calibration camera must remain orthographic for like-for-like comparison");

            GameObject labelRoot = GameObject.Find("Calibration Labels");
            if (labelRoot == null)
                failures.Add("Calibration Labels hierarchy missing");
            else if (labelRoot.transform.childCount != 14)
                failures.Add("calibration labels " + labelRoot.transform.childCount + " != 14 hierarchy markers");

            if (EditorBuildSettings.scenes.Any(s => string.Equals(s.path, ScenePath, StringComparison.OrdinalIgnoreCase)))
                failures.Add("material calibration review scene must stay out of Android build settings");

            for (int i = 0; i < drivers.Length && i < ExpectedWetness.Length; i++)
                AuditColumn(drivers[i], ExpectedWetness[i], failures);

            foreach (Renderer renderer in sampleRenderers)
            {
                if (renderer.shadowCastingMode != ShadowCastingMode.Off)
                    failures.Add(renderer.gameObject.name + " must not cast shadows");
                if (renderer.receiveShadows)
                    failures.Add(renderer.gameObject.name + " must not receive shadows");
            }

            Debug.Log("[ProjectOEN.Art.Calibration] Material calibration audit");
            Debug.Log("[ProjectOEN.Art.Calibration] samples=" + sampleRenderers.Length + "/" + ExpectedSampleCount +
                      " drivers=" + drivers.Length + "/" + ExpectedWetness.Length +
                      " wettablePerColumn=" + ExpectedWettableCountPerColumn);
            Debug.Log("[ProjectOEN.Art.Calibration] colliders=" + colliders.Length +
                      " particles=" + particles.Length +
                      " lights=" + lights.Length +
                      " camera=" + cameras.Length);

            if (failures.Count > 0)
                throw new InvalidOperationException("Material calibration showcase hard gate failed:\n - " + string.Join("\n - ", failures));

            Debug.Log("[ProjectOEN.Art.Calibration] PASS: 11 shared materials compare dry/mid/storm under identical lighting; nine wettable families receive scoped MaterialPropertyBlocks while Fire and Water remain untouched.");
        }

        private static void AuditColumn(ProductionArtWetnessDriver driver, float expectedWetness, List<string> failures)
        {
            if (driver == null)
            {
                failures.Add("null wetness driver in calibration column");
                return;
            }

            if (Mathf.Abs(driver.Wetness - expectedWetness) > 0.001f)
                failures.Add(driver.gameObject.name + " wetness " + driver.Wetness.ToString("0.00") +
                             " != " + expectedWetness.ToString("0.00"));

            var serialized = new SerializedObject(driver);
            SerializedProperty scopeProperty = serialized.FindProperty("scopeRoot");
            Transform scopeRoot = scopeProperty == null ? null : scopeProperty.objectReferenceValue as Transform;
            if (scopeRoot != driver.transform)
                failures.Add(driver.gameObject.name + " must scope wetness to its own column root");

            driver.ApplyWetness();
            if (driver.LastAffectedRendererCount != ExpectedWettableCountPerColumn)
                failures.Add(driver.gameObject.name + " affected renderers " + driver.LastAffectedRendererCount +
                             " != " + ExpectedWettableCountPerColumn);

            int samplesInColumn = 0;
            var propertyBlock = new MaterialPropertyBlock();
            foreach (string materialName in MaterialNames)
            {
                Transform sample = driver.transform.Find("Sample_" + materialName);
                if (sample == null)
                {
                    failures.Add(driver.gameObject.name + " missing Sample_" + materialName);
                    continue;
                }

                Renderer renderer = sample.GetComponent<Renderer>();
                if (renderer == null)
                {
                    failures.Add(sample.name + " renderer missing in " + driver.gameObject.name);
                    continue;
                }
                samplesInColumn++;

                string materialPath = MaterialRoot + "/" + materialName.ToLowerInvariant() + ".mat";
                Material expectedMaterial = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
                if (expectedMaterial == null)
                    failures.Add("shared material missing: " + materialPath);
                else if (renderer.sharedMaterial != expectedMaterial)
                    failures.Add(driver.gameObject.name + "/" + sample.name + " is not using shared " + materialName + " material");

                propertyBlock.Clear();
                renderer.GetPropertyBlock(propertyBlock, 0);
                bool shouldBeWettable = materialName != "Fire" && materialName != "Water";
                if (shouldBeWettable && propertyBlock.isEmpty)
                    failures.Add(driver.gameObject.name + "/" + sample.name + " missing scoped wetness MaterialPropertyBlock");
                if (!shouldBeWettable && !propertyBlock.isEmpty)
                    failures.Add(driver.gameObject.name + "/" + sample.name + " must stay outside wetness MaterialPropertyBlock response");
            }

            if (samplesInColumn != MaterialNames.Length)
                failures.Add(driver.gameObject.name + " sample count " + samplesInColumn + " != " + MaterialNames.Length);
        }
    }
}