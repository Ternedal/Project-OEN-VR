using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Builds lightweight Unity materials/prefabs for the dedicated Project ØEN
    /// VFX production textures. This layer intentionally adds no realtime lights,
    /// colliders, particle collision or shadowing.
    /// </summary>
    public static class ProductionArtVfxBuilder
    {
        private const string SpriteRoot = "Assets/ProductionArt/Sprites/vfx_support_graphics";
        private const string MaterialRoot = "Assets/ProductionArt/VfxMaterials";
        private const string PrefabRoot = "Assets/ProductionArt/VfxPrefabs";

        private sealed class VfxSpec
        {
            public string AssetId;
            public string Variant;
            public string Kind;
            public bool Additive;

            public VfxSpec(string assetId, string variant, string kind, bool additive = false)
            {
                AssetId = assetId;
                Variant = variant;
                Kind = kind;
                Additive = additive;
            }
        }

        private static readonly VfxSpec[] Specs =
        {
            new VfxSpec("fx-001_", "small", "smoke"),
            new VfxSpec("fx-001_", "medium", "smoke"),
            new VfxSpec("fx-002_", "small", "ember", true),
            new VfxSpec("fx-002_", "medium", "ember", true),
            new VfxSpec("fx-003_", "single", "ash"),
            new VfxSpec("fx-004_", "small", "rain_splash"),
            new VfxSpec("fx-004_", "medium", "rain_splash"),
            new VfxSpec("fx-005_", "single", "wet_sheen"),
            new VfxSpec("fx-006_", "near", "lightning", true),
            new VfxSpec("fx-006_", "far", "lightning", true),
            new VfxSpec("fx-007_", "fire", "glow", true),
            new VfxSpec("fx-007_", "lantern", "glow", true),
            new VfxSpec("fx-008_", "small", "objective_pulse", true),
            new VfxSpec("fx-008_", "medium", "objective_pulse", true),
        };

        [MenuItem("Project OEN/Art/Build Production VFX")]
        public static void BuildAll()
        {
            if (!AssetDatabase.IsValidFolder(SpriteRoot))
                throw new InvalidOperationException("Production VFX sprite root is missing: " + SpriteRoot);

            EnsureFolder(MaterialRoot);
            EnsureFolder(PrefabRoot);

            int materials = 0;
            int prefabs = 0;
            foreach (VfxSpec spec in Specs)
            {
                string texturePath = FindTexturePath(spec.AssetId, spec.Variant);
                Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
                if (texture == null)
                    throw new InvalidOperationException("Unity did not import VFX texture: " + texturePath);

                Material material = BuildMaterial(spec, texture);
                materials++;

                // Wet sheen is a material helper/mask, not a standalone particle or billboard.
                if (spec.Kind == "wet_sheen")
                    continue;

                if (spec.Kind == "smoke" || spec.Kind == "ember" || spec.Kind == "ash" || spec.Kind == "rain_splash")
                    BuildParticlePrefab(spec, material);
                else
                    BuildBillboardPrefab(spec, texturePath, material);
                prefabs++;
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[ProjectOEN.Art.VFX] Built " + materials + " VFX materials and " + prefabs +
                      " lightweight effect prefabs; wet sheen remains a material-helper asset.");
        }

        private static Material BuildMaterial(VfxSpec spec, Texture2D texture)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Particles/Unlit");
            if (shader == null) shader = Shader.Find("Particles/Standard Unlit");
            if (shader == null) shader = Shader.Find("Unlit/Transparent");
            if (shader == null) throw new InvalidOperationException("No supported unlit transparent VFX shader found.");

            string name = spec.AssetId.TrimEnd('_').Replace('-', '_') + "_" + spec.Variant + "_" + spec.Kind;
            string path = MaterialRoot + "/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.shader = shader;
                material.name = name;
            }

            if (material.HasProperty("_BaseMap")) material.SetTexture("_BaseMap", texture);
            if (material.HasProperty("_MainTex")) material.SetTexture("_MainTex", texture);
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", Color.white);
            if (material.HasProperty("_Color")) material.SetColor("_Color", Color.white);
            if (material.HasProperty("_Surface")) material.SetFloat("_Surface", 1f);
            if (material.HasProperty("_ZWrite")) material.SetFloat("_ZWrite", 0f);
            if (material.HasProperty("_Cull")) material.SetFloat("_Cull", 0f);
            if (material.HasProperty("_SrcBlend")) material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            if (material.HasProperty("_DstBlend")) material.SetFloat("_DstBlend", (float)(spec.Additive ? BlendMode.One : BlendMode.OneMinusSrcAlpha));
            material.renderQueue = (int)RenderQueue.Transparent;
            material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.DisableKeyword("_ALPHATEST_ON");
            EditorUtility.SetDirty(material);
            return material;
        }

        private static void BuildParticlePrefab(VfxSpec spec, Material material)
        {
            string stem = spec.AssetId.TrimEnd('_').Replace('-', '_') + "_" + spec.Variant + "_" + spec.Kind;
            GameObject root = new GameObject(stem);
            try
            {
                ParticleSystem ps = root.AddComponent<ParticleSystem>();
                ParticleSystem.MainModule main = ps.main;
                main.playOnAwake = false;
                main.loop = spec.Kind != "rain_splash";
                main.simulationSpace = ParticleSystemSimulationSpace.Local;
                main.maxParticles = MaxParticles(spec.Kind, spec.Variant);
                main.startLifetime = StartLifetime(spec.Kind, spec.Variant);
                main.startSpeed = StartSpeed(spec.Kind, spec.Variant);
                main.startSize = StartSize(spec.Kind, spec.Variant);

                ParticleSystem.EmissionModule emission = ps.emission;
                emission.rateOverTime = EmissionRate(spec.Kind, spec.Variant);

                ParticleSystem.ShapeModule shape = ps.shape;
                shape.enabled = true;
                shape.shapeType = spec.Kind == "rain_splash" ? ParticleSystemShapeType.Circle : ParticleSystemShapeType.Cone;
                shape.radius = spec.Kind == "rain_splash" ? 0.18f : 0.08f;
                if (spec.Kind != "rain_splash") shape.angle = 8f;

                if (spec.Kind == "smoke")
                {
                    ParticleSystem.TextureSheetAnimationModule sheet = ps.textureSheetAnimation;
                    sheet.enabled = true;
                    sheet.mode = ParticleSystemAnimationMode.Grid;
                    sheet.animation = ParticleSystemAnimationType.WholeSheet;
                    sheet.numTilesX = 4;
                    sheet.numTilesY = 4;
                    sheet.cycleCount = 1;
                }

                ParticleSystemRenderer renderer = ps.GetComponent<ParticleSystemRenderer>();
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.renderMode = spec.Kind == "ember" ? ParticleSystemRenderMode.Stretch : ParticleSystemRenderMode.Billboard;
                if (spec.Kind == "ember")
                {
                    renderer.lengthScale = 1.8f;
                    renderer.velocityScale = 0.55f;
                }

                string path = PrefabRoot + "/" + stem + ".prefab";
                if (PrefabUtility.SaveAsPrefabAsset(root, path) == null)
                    throw new InvalidOperationException("Could not save VFX prefab: " + path);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static void BuildBillboardPrefab(VfxSpec spec, string texturePath, Material material)
        {
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(texturePath);
            if (sprite == null)
                throw new InvalidOperationException("VFX billboard texture did not import as Sprite: " + texturePath);

            string stem = spec.AssetId.TrimEnd('_').Replace('-', '_') + "_" + spec.Variant + "_" + spec.Kind;
            GameObject root = new GameObject(stem);
            try
            {
                SpriteRenderer renderer = root.AddComponent<SpriteRenderer>();
                renderer.sprite = sprite;
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.sortingOrder = 20;

                float width = sprite.bounds.size.x;
                float targetWidth = spec.Kind == "lightning" ? (spec.Variant == "near" ? 2.4f : 1.5f) :
                                    spec.Kind == "glow" ? (spec.Variant == "fire" ? 0.75f : 0.42f) :
                                    spec.Variant == "small" ? 0.32f : 0.52f;
                if (width > 0.0001f) root.transform.localScale = Vector3.one * (targetWidth / width);

                string path = PrefabRoot + "/" + stem + ".prefab";
                if (PrefabUtility.SaveAsPrefabAsset(root, path) == null)
                    throw new InvalidOperationException("Could not save VFX billboard prefab: " + path);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static int MaxParticles(string kind, string variant)
        {
            if (kind == "smoke") return variant == "small" ? 10 : 16;
            if (kind == "ember") return variant == "small" ? 18 : 28;
            if (kind == "ash") return 24;
            if (kind == "rain_splash") return variant == "small" ? 8 : 12;
            return 8;
        }

        private static float StartLifetime(string kind, string variant)
        {
            if (kind == "smoke") return variant == "small" ? 1.5f : 2.2f;
            if (kind == "ember") return 0.7f;
            if (kind == "ash") return 2.4f;
            if (kind == "rain_splash") return 0.35f;
            return 1f;
        }

        private static float StartSpeed(string kind, string variant)
        {
            if (kind == "smoke") return variant == "small" ? 0.14f : 0.22f;
            if (kind == "ember") return variant == "small" ? 0.55f : 0.8f;
            if (kind == "ash") return 0.08f;
            if (kind == "rain_splash") return 0.03f;
            return 0f;
        }

        private static float StartSize(string kind, string variant)
        {
            if (kind == "smoke") return variant == "small" ? 0.28f : 0.45f;
            if (kind == "ember") return variant == "small" ? 0.045f : 0.065f;
            if (kind == "ash") return 0.055f;
            if (kind == "rain_splash") return variant == "small" ? 0.22f : 0.36f;
            return 0.2f;
        }

        private static float EmissionRate(string kind, string variant)
        {
            if (kind == "smoke") return variant == "small" ? 3.2f : 4.5f;
            if (kind == "ember") return variant == "small" ? 5f : 8f;
            if (kind == "ash") return 3f;
            if (kind == "rain_splash") return variant == "small" ? 4f : 6f;
            return 0f;
        }

        private static string FindTexturePath(string prefix, string variant)
        {
            string p = prefix.ToLowerInvariant();
            string v = variant.ToLowerInvariant();
            string[] guids = AssetDatabase.FindAssets("t:Texture2D", new[] { SpriteRoot });
            List<string> candidates = guids
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(path => Path.GetFileNameWithoutExtension(path).ToLowerInvariant().StartsWith(p))
                .OrderBy(path => path, StringComparer.Ordinal)
                .ToList();
            if (candidates.Count == 0)
                throw new InvalidOperationException("No production VFX texture with prefix: " + prefix);
            string chosen = candidates.FirstOrDefault(path => Path.GetFileNameWithoutExtension(path).ToLowerInvariant().Contains("__" + v));
            if (chosen == null && variant == "single") chosen = candidates[0];
            if (chosen == null) throw new InvalidOperationException("No VFX state found for " + prefix + " / " + variant);
            return chosen;
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
