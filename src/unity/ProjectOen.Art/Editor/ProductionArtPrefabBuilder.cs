using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Converts generated Project ØEN production-art OBJ models into reusable Unity prefabs.
    /// Source meshes remain untouched under Assets/ProjectOEN/ProductionArt/Meshes.
    ///
    /// Design goals:
    /// - deterministic output paths;
    /// - simple static colliders suitable for Quest 2 baseline prototyping;
    /// - no dependency on Meta Avatars, Shader Graph or third-party packages;
    /// - lightweight fire/signal dressing only where the asset name explicitly represents an active flame.
    /// </summary>
    public static class ProductionArtPrefabBuilder
    {
        private const string MeshRoot = "Assets/ProjectOEN/ProductionArt/Meshes";
        private const string PrefabRoot = "Assets/ProjectOEN/ProductionArt/Prefabs";

        [MenuItem("Project OEN/Art/Build Production Art Prefabs")]
        public static void BuildAll()
        {
            if (!AssetDatabase.IsValidFolder(MeshRoot))
            {
                Debug.LogError("[ProjectOEN.Art] Missing generated mesh root: " + MeshRoot);
                return;
            }

            EnsureFolder(PrefabRoot);

            string[] guids = AssetDatabase.FindAssets("t:GameObject", new[] { MeshRoot });
            int built = 0;
            var failures = new List<string>();

            foreach (string guid in guids)
            {
                string sourcePath = AssetDatabase.GUIDToAssetPath(guid);
                if (!sourcePath.EndsWith(".obj", StringComparison.OrdinalIgnoreCase))
                    continue;

                try
                {
                    BuildOne(sourcePath);
                    built++;
                }
                catch (Exception ex)
                {
                    failures.Add(sourcePath + ": " + ex.Message);
                }
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            if (failures.Count == 0)
            {
                Debug.Log("[ProjectOEN.Art] Built " + built + " production-art prefabs.");
            }
            else
            {
                Debug.LogError("[ProjectOEN.Art] Built " + built + " prefabs with " + failures.Count +
                               " failure(s):\n" + string.Join("\n", failures));
            }
        }

        private static void BuildOne(string sourcePath)
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(sourcePath);
            if (model == null)
                throw new InvalidOperationException("Unity did not import the OBJ as a GameObject.");

            string relative = sourcePath.Substring(MeshRoot.Length).TrimStart('/');
            string category = Path.GetDirectoryName(relative);
            category = string.IsNullOrEmpty(category) ? string.Empty : category.Replace('\\', '/');
            string prefabDirectory = string.IsNullOrEmpty(category)
                ? PrefabRoot
                : PrefabRoot + "/" + category;
            EnsureFolder(prefabDirectory);

            string fileName = Path.GetFileNameWithoutExtension(sourcePath);
            string prefabPath = prefabDirectory + "/" + fileName + ".prefab";

            var root = new GameObject(fileName);
            try
            {
                GameObject instance = PrefabUtility.InstantiatePrefab(model) as GameObject;
                if (instance == null)
                    throw new InvalidOperationException("PrefabUtility could not instantiate imported OBJ.");

                instance.name = "Visual";
                instance.transform.SetParent(root.transform, false);

                AddSimpleBoundsCollider(root);
                AddQuestFriendlyActiveFireIfNeeded(root, fileName);

                GameObject saved = PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
                if (saved == null)
                    throw new InvalidOperationException("PrefabUtility.SaveAsPrefabAsset returned null.");
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static void AddSimpleBoundsCollider(GameObject root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
                return;

            bool hasBounds = false;
            Bounds localBounds = default(Bounds);

            foreach (Renderer renderer in renderers)
            {
                Bounds world = renderer.bounds;
                Vector3[] corners =
                {
                    new Vector3(world.min.x, world.min.y, world.min.z),
                    new Vector3(world.min.x, world.min.y, world.max.z),
                    new Vector3(world.min.x, world.max.y, world.min.z),
                    new Vector3(world.min.x, world.max.y, world.max.z),
                    new Vector3(world.max.x, world.min.y, world.min.z),
                    new Vector3(world.max.x, world.min.y, world.max.z),
                    new Vector3(world.max.x, world.max.y, world.min.z),
                    new Vector3(world.max.x, world.max.y, world.max.z),
                };

                foreach (Vector3 corner in corners)
                {
                    Vector3 local = root.transform.InverseTransformPoint(corner);
                    if (!hasBounds)
                    {
                        localBounds = new Bounds(local, Vector3.zero);
                        hasBounds = true;
                    }
                    else
                    {
                        localBounds.Encapsulate(local);
                    }
                }
            }

            if (!hasBounds)
                return;

            BoxCollider collider = root.AddComponent<BoxCollider>();
            collider.center = localBounds.center;
            collider.size = localBounds.size;
        }

        private static void AddQuestFriendlyActiveFireIfNeeded(GameObject root, string fileName)
        {
            string n = fileName.ToLowerInvariant();
            bool activeCampfire = n.Contains("campfire_strong_flame") || n.Contains("campfire_small_flame");
            bool activeBeacon = n.Contains("signal_beacon_lit_active");
            bool litTorch = n.Contains("torch__lit") || n.Contains("torch_stand__lit");

            if (!activeCampfire && !activeBeacon && !litTorch)
                return;

            var fireRoot = new GameObject("RuntimeFireAccent");
            fireRoot.transform.SetParent(root.transform, false);

            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length > 0)
            {
                float top = renderers.Max(r => r.bounds.max.y);
                Vector3 worldTop = new Vector3(root.transform.position.x, top, root.transform.position.z);
                fireRoot.transform.position = worldTop;
            }

            // One non-shadowing point light is intentionally the ceiling for a generated fire prefab.
            var light = fireRoot.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = new Color(1.0f, 0.46f, 0.16f);
            light.intensity = activeBeacon ? 2.0f : 1.25f;
            light.range = activeBeacon ? 4.5f : 2.5f;
            light.shadows = LightShadows.None;

            var ps = fireRoot.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true;
            main.startLifetime = activeBeacon ? 0.75f : 0.55f;
            main.startSpeed = activeBeacon ? 0.65f : 0.42f;
            main.startSize = activeBeacon ? 0.12f : 0.075f;
            main.maxParticles = activeBeacon ? 14 : 8;
            main.startColor = new ParticleSystem.MinMaxGradient(
                new Color(1.0f, 0.28f, 0.04f, 0.85f),
                new Color(1.0f, 0.72f, 0.16f, 0.55f));

            var emission = ps.emission;
            emission.rateOverTime = activeBeacon ? 12f : 7f;

            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Cone;
            shape.angle = 9f;
            shape.radius = activeBeacon ? 0.14f : 0.08f;

            var particleRenderer = ps.GetComponent<ParticleSystemRenderer>();
            particleRenderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            particleRenderer.receiveShadows = false;
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
