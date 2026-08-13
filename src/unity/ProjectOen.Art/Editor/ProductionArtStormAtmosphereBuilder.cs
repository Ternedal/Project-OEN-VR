using System;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Adds the deterministic camp-consequence micro-story, a cheap local rain volume
    /// and one event-driven wet-surface driver to the generated Stormnatten art showcase.
    /// Rain has no collision or shadows; wetness uses MaterialPropertyBlocks and no
    /// per-frame Update loop.
    /// </summary>
    public static class ProductionArtStormAtmosphereBuilder
    {
        private const string ScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/StormnattenArtShowcase.unity";
        private const string MaterialRoot = "Assets/ProjectOEN/ProductionArt/UnityMaterials";
        private const string RainMaterialPath = MaterialRoot + "/storm_rain.mat";
        private const string RainObjectName = "Storm Rain Volume";
        private const string WetnessObjectName = "Storm Surface Wetness";
        private const float ShowcaseWetness = 0.78f;

        [MenuItem("Project OEN/Art/Add Storm Atmosphere To Showcase")]
        public static void AddStormAtmosphere()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
                throw new InvalidOperationException("Showcase scene missing: " + ScenePath);

            // The camp consequence layer is part of the canonical Stormnatten visual
            // pass. It rebuilds itself idempotently before rain/wetness are authored,
            // so every existing bootstrap/review entrypoint receives the story layer.
            ProductionArtStormCampStoryBuilder.BuildIntoShowcase();

            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            RemoveExistingAtmosphere();

            Material rainMaterial = BuildOrUpdateRainMaterial();
            var rainGo = new GameObject(RainObjectName);
            rainGo.transform.position = new Vector3(0f, 7.2f, 0f);

            var ps = rainGo.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true;
            main.playOnAwake = true;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.70f, 1.05f);
            main.startSpeed = 0f;
            main.startSize = new ParticleSystem.MinMaxCurve(0.018f, 0.032f);
            main.startColor = new ParticleSystem.MinMaxGradient(
                new Color(0.62f, 0.74f, 0.82f, 0.13f),
                new Color(0.80f, 0.88f, 0.92f, 0.23f));
            main.maxParticles = 180;

            var emission = ps.emission;
            emission.rateOverTime = 135f;

            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(17f, 0.25f, 17f);

            var velocity = ps.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = new ParticleSystem.MinMaxCurve(-2.15f, -1.35f);
            velocity.y = new ParticleSystem.MinMaxCurve(-13.5f, -11.5f);
            velocity.z = new ParticleSystem.MinMaxCurve(0.15f, 0.65f);

            var renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.renderMode = ParticleSystemRenderMode.Stretch;
            renderer.lengthScale = 2.8f;
            renderer.velocityScale = 0.08f;
            renderer.cameraVelocityScale = 0f;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            renderer.sharedMaterial = rainMaterial;

            var wetnessGo = new GameObject(WetnessObjectName);
            var wetnessDriver = wetnessGo.AddComponent<ProductionArtWetnessDriver>();
            wetnessDriver.SetWetness(ShowcaseWetness);

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[ProjectOEN.Art] Added Quest-friendly storm atmosphere to " + ScenePath +
                      " (camp micro-story + 1 rain particle system, max 180 particles, no collision/shadows; " +
                      "event-driven surface wetness=" + ShowcaseWetness.ToString("0.00") + ").");
        }

        private static Material BuildOrUpdateRainMaterial()
        {
            EnsureFolder(MaterialRoot);

            Shader shader = Shader.Find("Universal Render Pipeline/Particles/Unlit");
            if (shader == null)
                shader = Shader.Find("Particles/Standard Unlit");
            if (shader == null)
                shader = Shader.Find("Unlit/Color");
            if (shader == null)
                throw new InvalidOperationException("No particle/unlit shader available for storm rain material.");

            Material material = AssetDatabase.LoadAssetAtPath<Material>(RainMaterialPath);
            if (material == null)
            {
                material = new Material(shader);
                material.name = "Storm Rain";
                AssetDatabase.CreateAsset(material, RainMaterialPath);
            }
            else
            {
                material.shader = shader;
            }

            Color rainColor = new Color(0.72f, 0.82f, 0.88f, 0.22f);
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", rainColor);
            if (material.HasProperty("_Color")) material.SetColor("_Color", rainColor);
            if (material.HasProperty("_Surface")) material.SetFloat("_Surface", 1f);
            if (material.HasProperty("_Blend")) material.SetFloat("_Blend", 0f);
            if (material.HasProperty("_SrcBlend")) material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            if (material.HasProperty("_DstBlend")) material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            if (material.HasProperty("_ZWrite")) material.SetFloat("_ZWrite", 0f);
            material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.renderQueue = 3000;

            EditorUtility.SetDirty(material);
            return material;
        }

        private static void RemoveExistingAtmosphere()
        {
            RemoveIfPresent(RainObjectName);
            RemoveIfPresent(WetnessObjectName);
        }

        private static void RemoveIfPresent(string objectName)
        {
            var existing = GameObject.Find(objectName);
            if (existing != null)
                UnityEngine.Object.DestroyImmediate(existing);
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
