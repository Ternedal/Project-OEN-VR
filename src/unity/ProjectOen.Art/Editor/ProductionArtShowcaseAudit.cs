using System;
using System.Collections.Generic;
using System.IO;
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
    /// bounded motion-FX layer, a two-billboard near/far lightning rig, nine
    /// renderer-culled wind-responsive dressing objects, both deterministic
    /// Stormnatten micro-story layers and the canonical damaged/wet storm-pressure
    /// prefab states for camp and signal landmarks. Story renderers must be
    /// shadowless and opt out of light/reflection probes so consequence dressing
    /// cannot silently add realtime renderer cost on Quest 2.
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

        private const string CampStoryRootName = "Storm Camp Micro Story";
        private const int CampStoryExpectedCount = 9;
        private const int CampStoryTriangleHardLimit = 60000;
        private const int CampStoryMaterialSlotHardLimit = 36;
        private const float CampStoryMaxRadius = 3.10f;
        private static readonly Vector2 CampStoryCenter = new Vector2(-1.00f, 0.75f);

        private const string SignalStoryRootName = "Signal Finale Micro Story";
        private const int SignalStoryExpectedCount = 8;
        private const int SignalStoryTriangleHardLimit = 50000;
        private const int SignalStoryMaterialSlotHardLimit = 32;
        private const float SignalStoryMaxRadius = 2.45f;
        private static readonly Vector2 SignalStoryCenter = new Vector2(5.40f, 5.80f);

        private readonly struct StoryAuditSpec
        {
            public readonly string Name;
            public readonly string Prefix;
            public readonly string Token;

            public StoryAuditSpec(string name, string prefix, string token)
            {
                Name = name;
                Prefix = prefix;
                Token = token;
            }
        }

        private static readonly StoryAuditSpec[] CampStoryExpectations =
        {
            new StoryAuditSpec("Collapsed Shelter Crossbrace", "en-023_", "broken_shelter_parts"),
            new StoryAuditSpec("Storm-Torn Shelter Debris", "en-023_", "broken_shelter_parts"),
            new StoryAuditSpec("Shelter Guy Rope Under Load", "en-024_", "taut"),
            new StoryAuditSpec("Shelter Rope Failure", "en-024_", "slack"),
            new StoryAuditSpec("Snapped Wood Bundle", "pr-003_", "damaged"),
            new StoryAuditSpec("Overturned Storage Crate", "en-018_", "crate"),
            new StoryAuditSpec("Scattered Cooking Utensils", "en-017_", "utensils"),
            new StoryAuditSpec("Camp Rope Washout", "en-004_", "small"),
            new StoryAuditSpec("Shelter Foot Puddle", "en-011_", "small"),
        };

        private static readonly StoryAuditSpec[] SignalStoryExpectations =
        {
            new StoryAuditSpec("Collapsed Beacon Crossbrace", "pr-003_", "damaged"),
            new StoryAuditSpec("Loaded Beacon Guy Rope", "en-024_", "taut"),
            new StoryAuditSpec("Failed Beacon Guy Rope", "en-024_", "slack"),
            new StoryAuditSpec("Scattered Signal Fuel", "en-019_", "logs"),
            new StoryAuditSpec("Washed-Out Signal Rope", "en-004_", "small"),
            new StoryAuditSpec("Loose Beacon Anchor Stones", "pr-010_", "small"),
            new StoryAuditSpec("Storm-Torn Signal Cloth Debris", "en-023_", "loose_cloth"),
            new StoryAuditSpec("Signal Hill Puddle", "en-011_", "small"),
        };

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

        // Scene object name, prefab filename prefix, required variant token.
        // Construction-state rows encode their state in the asset ID/name and use
        // the default variant, so they intentionally have no third-token requirement.
        private static readonly string[][] StormStateExpectations =
        {
            new[] { "Storm-Damaged Shelter", "cs-004_", "" },
            new[] { "Campfire Nearly Out Wet", "cs-010_", "" },
            new[] { "Wet Tarp", "pr-001_", "wet" },
            new[] { "Wet Camp Groundsheet", "en-016_", "wet" },
            new[] { "Signal Beacon Storm Damaged", "cs-015_", "" },
            new[] { "Signal Cloth", "pr-014_", "storm_damaged" },
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
            int matchingStormStates = StormStateExpectations.Count(MatchesStormState);

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
            Debug.Log("[ProjectOEN.Art.Budget] stormStates=" + matchingStormStates + "/" + StormStateExpectations.Length);
            Debug.Log("[ProjectOEN.Art.Budget] stormMotionFx=" +
                      "wind:" + (windDebris != null ? windDebris.main.maxParticles.ToString() : "missing") +
                      " splash:" + (rainSplashes != null ? rainSplashes.main.maxParticles.ToString() : "missing") +
                      " lightning:" + (farPulse && nearPulse && lightPulse ? "near+far layered" : "incomplete"));

            if (triangles > TriangleTarget)
                Debug.LogWarning("[ProjectOEN.Art.Budget] Triangle target exceeded; device profile before adding more geometry.");
            if (drawCallProxy > DrawCallProxyTarget)
                Debug.LogWarning("[ProjectOEN.Art.Budget] Draw-call proxy target exceeded; inspect batching/material sharing.");

            var hardFailures = new List<string>();
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

            AuditStoryLayer(
                "camp micro-story",
                CampStoryRootName,
                CampStoryExpectedCount,
                CampStoryExpectations,
                CampStoryCenter,
                CampStoryMaxRadius,
                CampStoryTriangleHardLimit,
                CampStoryMaterialSlotHardLimit,
                hardFailures);

            AuditStoryLayer(
                "signal finale micro-story",
                SignalStoryRootName,
                SignalStoryExpectedCount,
                SignalStoryExpectations,
                SignalStoryCenter,
                SignalStoryMaxRadius,
                SignalStoryTriangleHardLimit,
                SignalStoryMaterialSlotHardLimit,
                hardFailures);

            foreach (string[] expectation in StormStateExpectations)
            {
                if (MatchesStormState(expectation))
                    continue;

                GameObject target = GameObject.Find(expectation[0]);
                if (target == null)
                {
                    hardFailures.Add("canonical storm-state object missing: " + expectation[0]);
                    continue;
                }

                string prefabPath = PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(target);
                string stem = string.IsNullOrEmpty(prefabPath)
                    ? "<not a prefab instance>"
                    : Path.GetFileNameWithoutExtension(prefabPath).ToLowerInvariant();
                hardFailures.Add("wrong canonical storm state on " + expectation[0] + ": " + stem);
            }

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

            Debug.Log("[ProjectOEN.Art.Budget] PASS: showcase stays inside repository Quest 2 hard limits with canonical storm-damaged/wet camp and signal states, imported camp/signal story layers, shadowless/probe-free story renderers, centralized wet surfaces, bounded storm motion FX, layered near/far lightning and nine renderer-culled wind-responsive dressing objects. Device profiling still required for authoritative frame timing/draw calls.");
        }

        private static void AuditStoryLayer(
            string label,
            string rootName,
            int expectedCount,
            StoryAuditSpec[] expectations,
            Vector2 center,
            float maxRadius,
            int triangleHardLimit,
            int materialSlotHardLimit,
            List<string> hardFailures)
        {
            Scene activeScene = SceneManager.GetActiveScene();
            GameObject[] roots = activeScene.GetRootGameObjects()
                .Where(root => root != null && root.name == rootName)
                .ToArray();

            if (roots.Length != 1)
            {
                hardFailures.Add(label + " root count " + roots.Length + " != 1");
                return;
            }

            GameObject root = roots[0];
            if (expectations.Length != expectedCount)
                hardFailures.Add(label + " audit expectation count " + expectations.Length + " != " + expectedCount);
            if (root.transform.childCount != expectedCount)
                hardFailures.Add(label + " direct child count " + root.transform.childCount + " != " + expectedCount);

            int storyColliders = root.GetComponentsInChildren<Collider>(true).Length;
            int storyRigidbodies = root.GetComponentsInChildren<Rigidbody>(true).Length;
            int storyParticles = root.GetComponentsInChildren<ParticleSystem>(true).Length;
            int storyLights = root.GetComponentsInChildren<Light>(true).Length;
            int storyAnimations = root.GetComponentsInChildren<Animation>(true).Length;
            int storyAnimators = root.GetComponentsInChildren<Animator>(true).Length;

            if (storyColliders != 0)
                hardFailures.Add(label + " colliders " + storyColliders + " != 0");
            if (storyRigidbodies != 0)
                hardFailures.Add(label + " rigidbodies " + storyRigidbodies + " != 0");
            if (storyParticles != 0)
                hardFailures.Add(label + " particle systems " + storyParticles + " != 0");
            if (storyLights != 0)
                hardFailures.Add(label + " lights " + storyLights + " != 0");
            if (storyAnimations != 0 || storyAnimators != 0)
                hardFailures.Add(label + " animation components " + (storyAnimations + storyAnimators) + " != 0");

            long storyTriangles = 0;
            foreach (MeshFilter filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh != null)
                    storyTriangles += filter.sharedMesh.triangles.LongLength / 3L;
            }
            foreach (SkinnedMeshRenderer skin in root.GetComponentsInChildren<SkinnedMeshRenderer>(true))
            {
                if (skin.sharedMesh != null)
                    storyTriangles += skin.sharedMesh.triangles.LongLength / 3L;
            }

            Renderer[] storyRenderers = root.GetComponentsInChildren<Renderer>(true);
            int storyMaterialSlots = storyRenderers.Sum(renderer =>
                renderer.sharedMaterials == null ? 0 : renderer.sharedMaterials.Length);
            int storyShadowRenderers = storyRenderers.Count(renderer =>
                renderer.shadowCastingMode != ShadowCastingMode.Off || renderer.receiveShadows);
            int storyLightProbeRenderers = storyRenderers.Count(renderer => renderer.lightProbeUsage != LightProbeUsage.Off);
            int storyReflectionProbeRenderers = storyRenderers.Count(renderer => renderer.reflectionProbeUsage != ReflectionProbeUsage.Off);

            if (storyTriangles > triangleHardLimit)
                hardFailures.Add(label + " triangles " + storyTriangles + " > " + triangleHardLimit);
            if (storyMaterialSlots > materialSlotHardLimit)
                hardFailures.Add(label + " material slots " + storyMaterialSlots + " > " + materialSlotHardLimit);
            if (storyShadowRenderers != 0)
                hardFailures.Add(label + " shadow-enabled renderers " + storyShadowRenderers + " != 0");
            if (storyLightProbeRenderers != 0)
                hardFailures.Add(label + " light-probed renderers " + storyLightProbeRenderers + " != 0");
            if (storyReflectionProbeRenderers != 0)
                hardFailures.Add(label + " reflection-probed renderers " + storyReflectionProbeRenderers + " != 0");

            foreach (StoryAuditSpec expectation in expectations)
            {
                Transform child = root.transform.Find(expectation.Name);
                if (child == null)
                {
                    hardFailures.Add(label + " object missing: " + expectation.Name);
                    continue;
                }

                float radius = Vector2.Distance(
                    new Vector2(child.position.x, child.position.z),
                    center);
                if (radius > maxRadius)
                    hardFailures.Add(label + " object outside " + maxRadius.ToString("0.00") +
                                     "m radius: " + expectation.Name + " at " + radius.ToString("0.00") + "m");

                string prefabPath = PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(child.gameObject);
                string stem = string.IsNullOrEmpty(prefabPath)
                    ? string.Empty
                    : Path.GetFileNameWithoutExtension(prefabPath).ToLowerInvariant().Replace('-', '_');
                string expectedPrefix = expectation.Prefix.ToLowerInvariant().Replace('-', '_');
                string expectedToken = expectation.Token.ToLowerInvariant().Replace('-', '_');
                if (!stem.StartsWith(expectedPrefix, StringComparison.Ordinal) || !stem.Contains(expectedToken))
                    hardFailures.Add(label + " wrong canonical prefab on " + expectation.Name + ": " +
                                     (string.IsNullOrEmpty(stem) ? "<not a prefab instance>" : stem));
            }

            Debug.Log("[ProjectOEN.Art.Budget] " + label +
                      " roots=1 children=" + root.transform.childCount + "/" + expectedCount +
                      " triangles=" + storyTriangles + "/" + triangleHardLimit +
                      " materialSlots=" + storyMaterialSlots + "/" + materialSlotHardLimit +
                      " radius<=" + maxRadius.ToString("0.00") + "m" +
                      " runtimeCost=" + (storyColliders + storyRigidbodies + storyParticles + storyLights + storyAnimations + storyAnimators) +
                      " rendererCost=shadows:" + storyShadowRenderers +
                      " lightProbes:" + storyLightProbeRenderers +
                      " reflectionProbes:" + storyReflectionProbeRenderers);
        }

        private static bool MatchesStormState(string[] expectation)
        {
            GameObject target = GameObject.Find(expectation[0]);
            if (target == null)
                return false;

            string prefabPath = PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(target);
            if (string.IsNullOrEmpty(prefabPath))
                return false;

            string stem = Path.GetFileNameWithoutExtension(prefabPath).ToLowerInvariant();
            if (!stem.StartsWith(expectation[1].ToLowerInvariant(), StringComparison.Ordinal))
                return false;

            string requiredToken = expectation[2].ToLowerInvariant();
            return string.IsNullOrEmpty(requiredToken) || stem.Contains(requiredToken);
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
