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
    /// - active particle systems/effects: max 10;
    /// - legacy Animation components: max 12 (9 wind + 1 layered-lightning rig + headroom).
    ///
    /// The Stormnatten art scene must also contain exactly one event-driven
    /// ProductionArtWetnessDriver at the authored storm wetness range plus the
    /// bounded motion-FX layer, a two-billboard near/far lightning rig and nine
    /// renderer-culled wind-responsive dressing objects. This keeps the scene
    /// alive without per-object Update() scripts.
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
        private const int AnimationComponentHardLimit = 12;
        private const float StormWetnessMin = 0.74f;
        private const float StormWetnessMax = 0.82f;
        private const string FarLightningName = "Far Lightning";
        private const string NearLightningName = "Near Lightning";

        private static readonly string[] WindResponseTargets =
        {
            "Loose Storm Cloth",
            "Rain Catcher Cloth",
            "Signal Cloth",
            "Signal Spare Ropes",
            "Palm Mature A",
            "Palm Mature B",
            "Palm Frond Clutter A",
            "Palm Frond Clutter B",
            "Vines",
        };

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
            Animation[] animations = UnityEngine.Object.FindObjectsOfType<Animation>(true);
            Collider[] colliders = UnityEngine.Object.FindObjectsOfType<Collider>(true);
            ProductionArtWetnessDriver[] wetnessDrivers = UnityEngine.Object.FindObjectsOfType<ProductionArtWetnessDriver>(true);

            GameObject windDebrisGo = GameObject.Find("Windblown Storm Debris");
            GameObject rainSplashGo = GameObject.Find("Camp Rain Splashes");
            GameObject lightningGo = GameObject.Find("Distant Storm Lightning");
            ParticleSystem windDebris = windDebrisGo == null ? null : windDebrisGo.GetComponentInChildren<ParticleSystem>(true);
            ParticleSystem rainSplashes = rainSplashGo == null ? null : rainSplashGo.GetComponentInChildren<ParticleSystem>(true);
            Animation lightningAnimation = lightningGo == null ? null : lightningGo.GetComponent<Animation>();
            Light lightningLight = lightningGo == null ? null : lightningGo.GetComponent<Light>();
            Transform farLightning = lightningGo == null ? null : lightningGo.transform.Find(FarLightningName);
            Transform nearLightning = lightningGo == null ? null : lightningGo.transform.Find(NearLightningName);
            SpriteRenderer farLightningSprite = farLightning == null ? null : farLightning.GetComponentInChildren<SpriteRenderer>(true);
            SpriteRenderer nearLightningSprite = nearLightning == null ? null : nearLightning.GetComponentInChildren<SpriteRenderer>(true);
            SpriteRenderer[] lightningSprites = lightningGo == null
                ? new SpriteRenderer[0]
                : lightningGo.GetComponentsInChildren<SpriteRenderer>(true);
            Collider[] lightningColliders = lightningGo == null
                ? new Collider[0]
                : lightningGo.GetComponentsInChildren<Collider>(true);

            var windResponse = WindResponseTargets
                .Select(name => new
                {
                    Name = name,
                    Target = GameObject.Find(name),
                })
                .Select(x => new
                {
                    x.Name,
                    Animation = x.Target == null ? null : x.Target.GetComponent<Animation>(),
                })
                .ToArray();
            int readyWindAnimations = windResponse.Count(x => x.Animation != null && x.Animation.clip != null);

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

            bool farPulse = HasPulseCurve(lightningAnimation == null ? null : lightningAnimation.clip,
                                          FarLightningName, typeof(SpriteRenderer), "m_Color.a", 0.55f);
            bool nearPulse = HasPulseCurve(lightningAnimation == null ? null : lightningAnimation.clip,
                                           NearLightningName, typeof(SpriteRenderer), "m_Color.a", 0.90f);
            bool lightPulse = HasPulseCurve(lightningAnimation == null ? null : lightningAnimation.clip,
                                            string.Empty, typeof(Light), "m_Intensity", 0.60f);

            Debug.Log("[ProjectOEN.Art.Budget] Stormnatten showcase audit");
            Debug.Log("[ProjectOEN.Art.Budget] triangles=" + triangles +
                      " target<=" + TriangleTarget + " hard<=" + TriangleHardLimit);
            Debug.Log("[ProjectOEN.Art.Budget] rendererMaterialSlots(draw-call proxy)=" + drawCallProxy +
                      " target<=" + DrawCallProxyTarget + " hard<=" + DrawCallProxyHardLimit);
            Debug.Log("[ProjectOEN.Art.Budget] lights=" + lights.Length +
                      " shadowCasters=" + shadowCasters + " hard<=" + ShadowCasterHardLimit);
            Debug.Log("[ProjectOEN.Art.Budget] particleSystems=" + activeParticles +
                      " hard<=" + ParticleSystemHardLimit + " colliders=" + colliders.Length);
            Debug.Log("[ProjectOEN.Art.Budget] animations=" + animations.Length +
                      " hard<=" + AnimationComponentHardLimit + " windReady=" + readyWindAnimations + "/" + WindResponseTargets.Length);
            Debug.Log("[ProjectOEN.Art.Budget] wetnessDrivers=" + wetnessDrivers.Length +
                      (wetnessDrivers.Length == 1 ? " wetness=" + wetnessDrivers[0].Wetness.ToString("0.00") : string.Empty));
            Debug.Log("[ProjectOEN.Art.Budget] stormMotionFx=" +
                      "wind:" + (windDebris != null ? windDebris.main.maxParticles.ToString() : "missing") +
                      " splash:" + (rainSplashes != null ? rainSplashes.main.maxParticles.ToString() : "missing") +
                      " lightning:" + (farPulse && nearPulse && lightPulse ? "near+far layered" : "incomplete"));

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
            if (animations.Length > AnimationComponentHardLimit)
                hardFailures.Add("legacy Animation components " + animations.Length + " > " + AnimationComponentHardLimit);
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
            else
            {
                if (!lightningAnimation.clip.legacy)
                    hardFailures.Add("Distant Storm Lightning clip must stay legacy");
                if (lightningAnimation.clip.wrapMode != WrapMode.Loop)
                    hardFailures.Add("Distant Storm Lightning clip must loop");
                if (lightningAnimation.cullingType != AnimationCullingType.AlwaysAnimate)
                    hardFailures.Add("Distant Storm Lightning rig must always animate so off-alpha billboards can flash back on");
            }
            if (lightningSprites.Length != 2)
                hardFailures.Add("layered lightning SpriteRenderer count " + lightningSprites.Length + " != 2");
            if (farLightningSprite == null)
                hardFailures.Add("Far Lightning sprite missing");
            if (nearLightningSprite == null)
                hardFailures.Add("Near Lightning sprite missing");
            if (!farPulse)
                hardFailures.Add("Far Lightning alpha pulse curve missing/too weak");
            if (!nearPulse)
                hardFailures.Add("Near Lightning alpha pulse curve missing/too weak");
            if (lightningLight == null)
                hardFailures.Add("Distant Storm Lightning shared flash light missing");
            else if (lightningLight.shadows != LightShadows.None)
                hardFailures.Add("Distant Storm Lightning shared flash light must not cast shadows");
            if (!lightPulse)
                hardFailures.Add("Distant Storm Lightning shared light pulse curve missing/too weak");
            if (lightningColliders.Length != 0)
                hardFailures.Add("layered lightning must remain collider-free");

            foreach (var response in windResponse)
            {
                if (response.Animation == null || response.Animation.clip == null)
                {
                    hardFailures.Add("wind response missing on " + response.Name);
                    continue;
                }
                if (!response.Animation.clip.legacy)
                    hardFailures.Add("wind clip must stay legacy on " + response.Name);
                if (response.Animation.clip.wrapMode != WrapMode.Loop)
                    hardFailures.Add("wind clip must loop on " + response.Name);
                if (response.Animation.cullingType != AnimationCullingType.BasedOnRenderers)
                    hardFailures.Add("wind animation must use renderer culling on " + response.Name);
            }

            if (hardFailures.Count > 0)
                throw new InvalidOperationException("Quest 2 showcase budget hard gate failed: " + string.Join("; ", hardFailures));

            Debug.Log("[ProjectOEN.Art.Budget] PASS: showcase stays inside repository Quest 2 hard limits with centralized wet surfaces, bounded storm motion FX, layered near/far lightning and nine renderer-culled wind-responsive dressing objects. Device profiling still required for authoritative frame timing/draw calls.");
        }

        private static bool HasPulseCurve(AnimationClip clip, string path, Type type, string propertyName, float minimumPeak)
        {
            if (clip == null)
                return false;

            EditorCurveBinding binding = AnimationUtility.GetCurveBindings(clip)
                .FirstOrDefault(b => b.path == path && b.type == type && b.propertyName == propertyName);
            if (binding.type == null)
                return false;

            AnimationCurve curve = AnimationUtility.GetEditorCurve(clip, binding);
            if (curve == null || curve.keys.Length < 3)
                return false;

            return curve.keys.Max(key => key.value) >= minimumPeak;
        }
    }
}
