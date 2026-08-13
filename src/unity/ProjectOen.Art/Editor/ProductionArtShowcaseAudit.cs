using System;
using System.Linq;
using ProjectOen.Art.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Opens the generated Stormnatten art showcase after real Unity import and
    /// audits conservative scene-level proxies against the repository's Quest 2
    /// budgets. This is deliberately stricter than relying on visual judgement.
    ///
    /// Hard gates from docs/08:
    /// - triangles: warning > 500k, hard fail > 750k;
    /// - draw calls: target < 100, hard fail proxy > 130;
    /// - realtime shadow lights: max 1;
    /// - active particle systems/effects: max 10.
    ///
    /// The Stormnatten art scene must also contain exactly one event-driven
    /// ProductionArtWetnessDriver at the authored storm wetness range plus the
    /// bounded motion-FX layer: one wind-debris system, one camp-splash system
    /// and one animated non-shadowing distant-lightning object.
    ///
    /// Renderer material-slot count is used as a conservative draw-call proxy in
    /// this editor audit. Device profiling remains authoritative for final draw calls.
    /// </summary>
    public static class ProductionArtShowcaseAudit
    {
        private const string ScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/StormnattenArtShowcase.unity";
        private const int TriangleTarget = 500000;
        private const int TriangleHardLimit = 750000;
        private const int DrawCallProxyTarget = 100;
        private const int DrawCallProxyHardLimit = 130;
        private const int ShadowCasterHardLimit = 1;
        private const int ParticleSystemHardLimit = 10;
        private const float StormWetnessMin = 0.74f;
        private const float StormWetnessMax = 0.82f;

        [MenuItem("Project OEN/Art/Audit Stormnatten Showcase Budget")]
        public static void AuditShowcase()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
                throw new InvalidOperationException("Showcase scene missing: " + ScenePath);

            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

            MeshFilter[] meshFilters = UnityEngine.Object.FindObjectsOfType<MeshFilter>(true);
            SkinnedMeshRenderer[] skinned = UnityEngine.Object.FindObjectsOfType<SkinnedMeshRenderer>(true);
            Renderer[] renderers = UnityEngine.Object.FindObjectsOfType<Renderer>(true);
            Light[] lights = UnityEngine.Object.FindObjectsOfType<Light>(true);
            ParticleSystem[] particleSystems = UnityEngine.Object.FindObjectsOfType<ParticleSystem>(true);
            Collider[] colliders = UnityEngine.Object.FindObjectsOfType<Collider>(true);
            ProductionArtWetnessDriver[] wetnessDrivers = UnityEngine.Object.FindObjectsOfType<ProductionArtWetnessDriver>(true);

            GameObject windDebrisGo = GameObject.Find("Windblown Storm Debris");
            GameObject rainSplashGo = GameObject.Find("Camp Rain Splashes");
            GameObject lightningGo = GameObject.Find("Distant Storm Lightning");
            ParticleSystem windDebris = windDebrisGo == null ? null : windDebrisGo.GetComponentInChildren<ParticleSystem>(true);
            ParticleSystem rainSplashes = rainSplashGo == null ? null : rainSplashGo.GetComponentInChildren<ParticleSystem>(true);
            Animation lightningAnimation = lightningGo == null ? null : lightningGo.GetComponent<Animation>();
            Light lightningLight = lightningGo == null ? null : lightningGo.GetComponent<Light>();
            SpriteRenderer lightningSprite = lightningGo == null ? null : lightningGo.GetComponentInChildren<SpriteRenderer>(true);

            long triangles = 0;
            foreach (MeshFilter filter in meshFilters)
            {
                Mesh mesh = filter.sharedMesh;
                if (mesh != null)
                    triangles += mesh.triangles.LongLength / 3L;
            }
            foreach (SkinnedMeshRenderer skin in skinned)
            {
                Mesh mesh = skin.sharedMesh;
                if (mesh != null)
                    triangles += mesh.triangles.LongLength / 3L;
            }

            int drawCallProxy = renderers
                .Where(r => r != null && r.enabled && r.gameObject.activeInHierarchy)
                .Sum(r => Math.Max(1, r.sharedMaterials == null ? 0 : r.sharedMaterials.Length));

            int shadowCasters = lights.Count(l => l != null && l.enabled &&
                l.gameObject.activeInHierarchy && l.shadows != LightShadows.None);
            int activeParticles = particleSystems.Count(p => p != null && p.gameObject.activeInHierarchy && p.emission.enabled);

            Debug.Log("[ProjectOEN.Art.Budget] Stormnatten showcase audit");
            Debug.Log("[ProjectOEN.Art.Budget] triangles=" + triangles +
                      " target<=" + TriangleTarget + " hard<=" + TriangleHardLimit);
            Debug.Log("[ProjectOEN.Art.Budget] rendererMaterialSlots(draw-call proxy)=" + drawCallProxy +
                      " target<=" + DrawCallProxyTarget + " hard<=" + DrawCallProxyHardLimit);
            Debug.Log("[ProjectOEN.Art.Budget] lights=" + lights.Length +
                      " shadowCasters=" + shadowCasters + " hard<=" + ShadowCasterHardLimit);
            Debug.Log("[ProjectOEN.Art.Budget] particleSystems=" + activeParticles +
                      " hard<=" + ParticleSystemHardLimit + " colliders=" + colliders.Length);
            Debug.Log("[ProjectOEN.Art.Budget] wetnessDrivers=" + wetnessDrivers.Length +
                      (wetnessDrivers.Length == 1 ? " wetness=" + wetnessDrivers[0].Wetness.ToString("0.00") : string.Empty));
            Debug.Log("[ProjectOEN.Art.Budget] stormMotionFx=" +
                      "wind:" + (windDebris != null ? windDebris.main.maxParticles.ToString() : "missing") +
                      " splash:" + (rainSplashes != null ? rainSplashes.main.maxParticles.ToString() : "missing") +
                      " lightning:" + (lightningAnimation != null && lightningLight != null && lightningSprite != null ? "ready" : "missing"));

            if (triangles > TriangleTarget)
                Debug.LogWarning("[ProjectOEN.Art.Budget] Triangle target exceeded; device profile before adding more geometry.");
            if (drawCallProxy > DrawCallProxyTarget)
                Debug.LogWarning("[ProjectOEN.Art.Budget] Draw-call proxy target exceeded; inspect batching/material sharing.");

            var hardFailures = new System.Collections.Generic.List<string>();
            if (triangles > TriangleHardLimit)
                hardFailures.Add("triangles " + triangles + " > " + TriangleHardLimit);
            if (drawCallProxy > DrawCallProxyHardLimit)
                hardFailures.Add("draw-call proxy " + drawCallProxy + " > " + DrawCallProxyHardLimit);
            if (shadowCasters > ShadowCasterHardLimit)
                hardFailures.Add("shadow-casting realtime lights " + shadowCasters + " > " + ShadowCasterHardLimit);
            if (activeParticles > ParticleSystemHardLimit)
                hardFailures.Add("active particle systems " + activeParticles + " > " + ParticleSystemHardLimit);
            if (wetnessDrivers.Length != 1)
                hardFailures.Add("wetness drivers " + wetnessDrivers.Length + " != 1");
            else if (wetnessDrivers[0].Wetness < StormWetnessMin || wetnessDrivers[0].Wetness > StormWetnessMax)
                hardFailures.Add("storm wetness " + wetnessDrivers[0].Wetness.ToString("0.00") +
                                 " outside " + StormWetnessMin.ToString("0.00") + "-" + StormWetnessMax.ToString("0.00"));

            if (windDebris == null)
                hardFailures.Add("Windblown Storm Debris particle system missing");
            else if (windDebris.main.maxParticles > 24)
                hardFailures.Add("wind debris maxParticles " + windDebris.main.maxParticles + " > 24");

            if (rainSplashes == null)
                hardFailures.Add("Camp Rain Splashes particle system missing");
            else if (rainSplashes.main.maxParticles > 12)
                hardFailures.Add("camp splash maxParticles " + rainSplashes.main.maxParticles + " > 12");

            if (lightningAnimation == null || lightningAnimation.clip == null)
                hardFailures.Add("Distant Storm Lightning animation missing");
            if (lightningSprite == null)
                hardFailures.Add("Distant Storm Lightning sprite missing");
            if (lightningLight == null)
                hardFailures.Add("Distant Storm Lightning flash light missing");
            else if (lightningLight.shadows != LightShadows.None)
                hardFailures.Add("Distant Storm Lightning must not cast shadows");

            if (hardFailures.Count > 0)
                throw new InvalidOperationException("Quest 2 showcase budget hard gate failed: " + string.Join("; ", hardFailures));

            Debug.Log("[ProjectOEN.Art.Budget] PASS: showcase stays inside repository Quest 2 hard limits with centralized wet surfaces and bounded storm motion FX. Device profiling still required for authoritative frame timing/draw calls.");
        }
    }
}
