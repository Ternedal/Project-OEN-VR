using System;
using System.Linq;
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

            if (hardFailures.Count > 0)
                throw new InvalidOperationException("Quest 2 showcase budget hard gate failed: " + string.Join("; ", hardFailures));

            Debug.Log("[ProjectOEN.Art.Budget] PASS: showcase stays inside repository Quest 2 hard limits. Device profiling still required for authoritative frame timing/draw calls.");
        }
    }
}
