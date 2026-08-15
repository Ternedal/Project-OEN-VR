using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Audits the actually imported isolated VFX review scene. This protects
    /// structural Quest-conscious constraints but does not replace headset visual
    /// quality/performance review.
    /// </summary>
    public static class ProductionArtVfxShowcaseAudit
    {
        private const string ScenePath = "Assets/ProductionArt/Scenes/ProductionVfxShowcase.unity";
        private const int ExpectedParticleSystems = 7;
        private const int ExpectedBillboardSprites = 6;
        private const int MaxParticlesPerSystem = 28;

        [MenuItem("Project OEN/Art/Audit Production VFX Showcase")]
        public static void AuditShowcase()
        {
            if (!System.IO.File.Exists(ScenePath))
                throw new InvalidOperationException("Production VFX showcase scene is missing: " + ScenePath);

            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject[] all = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Transform>(true))
                .Select(t => t.gameObject)
                .Distinct()
                .ToArray();

            RequireNamed(all, "Production VFX Review Grid");
            RequireNamed(all, "VFX Review Camera");
            RequireNamed(all, "Wet Sheen Dark Reference");
            RequireNamed(all, "Wet Sheen Helper");

            ParticleSystem[] systems = all.SelectMany(go => go.GetComponents<ParticleSystem>()).ToArray();
            if (systems.Length != ExpectedParticleSystems)
                throw new InvalidOperationException("Expected " + ExpectedParticleSystems + " VFX particle systems, found " + systems.Length);

            foreach (ParticleSystem ps in systems)
            {
                ParticleSystem.MainModule main = ps.main;
                if (main.maxParticles > MaxParticlesPerSystem)
                    throw new InvalidOperationException(ps.gameObject.name + " maxParticles=" + main.maxParticles + " exceeds " + MaxParticlesPerSystem);
                if (main.playOnAwake)
                    throw new InvalidOperationException(ps.gameObject.name + " must remain playOnAwake=false in isolated review prefabs.");
                if (ps.collision.enabled)
                    throw new InvalidOperationException(ps.gameObject.name + " must not enable particle collision on Quest 2 baseline.");

                ParticleSystemRenderer renderer = ps.GetComponent<ParticleSystemRenderer>();
                if (renderer == null || renderer.sharedMaterial == null)
                    throw new InvalidOperationException(ps.gameObject.name + " has no production particle material.");
                if (renderer.shadowCastingMode != ShadowCastingMode.Off || renderer.receiveShadows)
                    throw new InvalidOperationException(ps.gameObject.name + " must not cast/receive shadows.");

                if (ps.gameObject.name.Contains("fx_001_"))
                {
                    ParticleSystem.TextureSheetAnimationModule sheet = ps.textureSheetAnimation;
                    if (!sheet.enabled || sheet.numTilesX != 4 || sheet.numTilesY != 4)
                        throw new InvalidOperationException(ps.gameObject.name + " smoke must use the 4x4 flipbook atlas.");
                }
            }

            SpriteRenderer[] billboards = all.SelectMany(go => go.GetComponents<SpriteRenderer>()).ToArray();
            if (billboards.Length != ExpectedBillboardSprites)
                throw new InvalidOperationException("Expected " + ExpectedBillboardSprites + " VFX SpriteRenderers, found " + billboards.Length);
            foreach (SpriteRenderer renderer in billboards)
            {
                if (renderer.sprite == null || renderer.sharedMaterial == null)
                    throw new InvalidOperationException(renderer.gameObject.name + " has missing sprite/material.");
                if (renderer.shadowCastingMode != ShadowCastingMode.Off || renderer.receiveShadows)
                    throw new InvalidOperationException(renderer.gameObject.name + " must not cast/receive shadows.");
            }

            Renderer[] allRenderers = all.SelectMany(go => go.GetComponents<Renderer>()).ToArray();
            foreach (Renderer renderer in allRenderers)
            {
                if (renderer.shadowCastingMode != ShadowCastingMode.Off || renderer.receiveShadows)
                    throw new InvalidOperationException("VFX review renderer must not use shadows: " + renderer.gameObject.name);
            }

            int colliders = all.SelectMany(go => go.GetComponents<Collider>()).Count();
            if (colliders != 0)
                throw new InvalidOperationException("Isolated VFX review scene must have zero colliders, found " + colliders);
            if (all.SelectMany(go => go.GetComponents<Light>()).Any())
                throw new InvalidOperationException("Isolated VFX review scene must have zero realtime lights.");

            bool leakedIntoBuild = EditorBuildSettings.scenes.Any(s => s.enabled &&
                string.Equals(s.path, ScenePath, StringComparison.OrdinalIgnoreCase));
            if (leakedIntoBuild)
                throw new InvalidOperationException("Production VFX showcase must not be enabled in Android build settings.");

            Debug.Log("[ProjectOEN.Art.VFX.Audit] PASS: 7 particle systems, 6 billboards, 4x4 smoke flipbooks, maxParticles<=28, zero colliders/lights/shadows, scene excluded from build settings.");
        }

        private static GameObject RequireNamed(GameObject[] all, string name)
        {
            GameObject found = all.FirstOrDefault(go => go.name == name);
            if (found == null) throw new InvalidOperationException("Required VFX review object missing: " + name);
            return found;
        }
    }
}
