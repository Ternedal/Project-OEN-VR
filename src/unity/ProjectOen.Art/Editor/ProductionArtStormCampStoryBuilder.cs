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
    /// Adds a deterministic physical storm-consequence story around the camp in
    /// StormnattenArtShowcase. The story uses existing canonical production prefabs
    /// only: broken shelter pieces, strained/failed rope, damaged poles, overturned
    /// storage, scattered utensils, rope washout and a small shelter-foot puddle.
    ///
    /// This layer is intentionally cheap and static. It adds no particles, lights,
    /// colliders, physics, Animator/Animation components or runtime update loops.
    /// </summary>
    public static class ProductionArtStormCampStoryBuilder
    {
        public const string ScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/StormnattenArtShowcase.unity";
        public const string StoryRootName = "Storm Camp Micro Story";
        public const int ExpectedStoryObjectCount = 9;

        private const string PrefabRoot = "Assets/ProjectOEN/ProductionArt/Prefabs";
        private const int TriangleHardLimit = 60000;
        private const int MaterialSlotHardLimit = 36;

        private readonly struct StorySpec
        {
            public readonly string name;
            public readonly string prefix;
            public readonly string token;
            public readonly Vector3 position;
            public readonly Vector3 euler;
            public readonly float scale;
            public readonly bool batchingStatic;

            public StorySpec(string objectName, string prefabPrefix, string variantToken,
                Vector3 worldPosition, Vector3 worldEuler, float uniformScale, bool isBatchingStatic)
            {
                name = objectName;
                prefix = prefabPrefix;
                token = variantToken;
                position = worldPosition;
                euler = worldEuler;
                scale = uniformScale;
                batchingStatic = isBatchingStatic;
            }
        }

        private static readonly StorySpec[] Specs =
        {
            // Shelter pressure: two separated broken-part clusters make the damaged
            // shelter read as an event rather than merely another construction state.
            new StorySpec("Collapsed Shelter Crossbrace", "en-023_", "broken_shelter_parts",
                new Vector3(-2.42f, 0.055f, 1.62f), new Vector3(7f, 28f, 18f), 0.78f, true),
            new StorySpec("Storm-Torn Shelter Debris", "en-023_", "broken_shelter_parts",
                new Vector3(-0.48f, 0.035f, 2.22f), new Vector3(-5f, -42f, -12f), 0.62f, true),

            // Rope tells two different mechanical stories: one guy-line is still
            // carrying load, while another has failed and dropped into the mud.
            new StorySpec("Shelter Guy Rope Under Load", "en-024_", "taut",
                new Vector3(-1.58f, 0.030f, 0.96f), new Vector3(0f, 18f, 0f), 1.12f, true),
            new StorySpec("Shelter Rope Failure", "en-024_", "slack",
                new Vector3(-2.72f, 0.022f, 0.48f), new Vector3(0f, 56f, 0f), 0.78f, true),

            // Damaged build stock and displaced camp gear communicate that the
            // storm has affected both shelter integrity and day-to-day camp use.
            new StorySpec("Snapped Wood Bundle", "pr-003_", "damaged",
                new Vector3(-0.08f, 0.090f, 2.02f), new Vector3(10f, 74f, 12f), 0.70f, true),
            new StorySpec("Overturned Storage Crate", "en-018_", "crate",
                new Vector3(1.78f, 0.145f, 1.62f), new Vector3(9f, -34f, 18f), 0.72f, true),
            new StorySpec("Scattered Cooking Utensils", "en-017_", "utensils",
                new Vector3(0.93f, 0.025f, -0.42f), new Vector3(0f, 34f, 0f), 0.68f, true),
            new StorySpec("Camp Rope Washout", "en-004_", "small",
                new Vector3(-0.92f, 0.025f, -1.18f), new Vector3(0f, -12f, 0f), 0.66f, true),

            // A close puddle anchors the wetness around the damaged shelter instead
            // of leaving all visible water accents at the edge of the composition.
            new StorySpec("Shelter Foot Puddle", "en-011_", "small",
                new Vector3(-1.88f, 0.003f, -0.02f), new Vector3(0f, 14f, 0f), 0.90f, false),
        };

        [MenuItem("Project OEN/Art/Add Storm Camp Micro Story")]
        public static void BuildIntoShowcase()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
                throw new InvalidOperationException("Showcase scene missing: " + ScenePath);
            if (!AssetDatabase.IsValidFolder(PrefabRoot))
                throw new InvalidOperationException("Production prefab root missing: " + PrefabRoot);

            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            RemoveExistingStory();

            var root = new GameObject(StoryRootName);
            foreach (StorySpec spec in Specs)
                PlaceStoryPrefab(root.transform, spec);

            ValidateCurrentStory(root);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[ProjectOEN.Art.StormStory] Built " + ExpectedStoryObjectCount +
                      " deterministic camp-consequence props in " + ScenePath +
                      " with no particles/lights/colliders/physics/animation.");
        }

        private static void PlaceStoryPrefab(Transform parent, StorySpec spec)
        {
            GameObject prefab = FindPrefabStrict(spec.prefix, spec.token);
            var instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (instance == null)
                throw new InvalidOperationException("Could not instantiate story prefab: " + spec.prefix + " / " + spec.token);

            instance.name = spec.name;
            instance.transform.SetParent(parent, true);
            instance.transform.position = spec.position;
            instance.transform.rotation = Quaternion.Euler(spec.euler);
            instance.transform.localScale = Vector3.one * spec.scale;

            StripRuntimeOnlyCost(instance);
            ProductionArtStateAppearance appearance = instance.GetComponentInChildren<ProductionArtStateAppearance>(true);
            if (appearance != null)
                appearance.ApplyAppearance();

            if (spec.batchingStatic)
            {
                foreach (Transform t in instance.GetComponentsInChildren<Transform>(true))
                    GameObjectUtility.SetStaticEditorFlags(t.gameObject, StaticEditorFlags.BatchingStatic);
            }
        }

        private static GameObject FindPrefabStrict(string prefix, string token)
        {
            string p = prefix.ToLowerInvariant();
            string normalizedToken = (token ?? string.Empty).ToLowerInvariant().Replace('-', '_');
            string[] guids = AssetDatabase.FindAssets("t:Prefab", new[] { PrefabRoot });

            List<string> candidates = guids
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(path => Path.GetFileNameWithoutExtension(path).ToLowerInvariant().StartsWith(p))
                .OrderBy(path => path, StringComparer.Ordinal)
                .ToList();

            string chosen = candidates.FirstOrDefault(path =>
                Path.GetFileNameWithoutExtension(path).ToLowerInvariant().Replace('-', '_').Contains(normalizedToken));
            if (string.IsNullOrEmpty(chosen))
                throw new InvalidOperationException("Canonical story prefab missing: " + prefix + " / " + token);

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(chosen);
            if (prefab == null)
                throw new InvalidOperationException("Canonical story prefab could not be loaded: " + chosen);
            return prefab;
        }

        private static void StripRuntimeOnlyCost(GameObject root)
        {
            foreach (Collider component in root.GetComponentsInChildren<Collider>(true))
                UnityEngine.Object.DestroyImmediate(component);
            foreach (Rigidbody component in root.GetComponentsInChildren<Rigidbody>(true))
                UnityEngine.Object.DestroyImmediate(component);
            foreach (ParticleSystem component in root.GetComponentsInChildren<ParticleSystem>(true))
                UnityEngine.Object.DestroyImmediate(component.gameObject);
            foreach (Light component in root.GetComponentsInChildren<Light>(true))
                UnityEngine.Object.DestroyImmediate(component);
            foreach (Animation component in root.GetComponentsInChildren<Animation>(true))
                UnityEngine.Object.DestroyImmediate(component);
            foreach (Animator component in root.GetComponentsInChildren<Animator>(true))
                UnityEngine.Object.DestroyImmediate(component);
        }

        private static void ValidateCurrentStory(GameObject root)
        {
            if (root.transform.childCount != ExpectedStoryObjectCount)
                throw new InvalidOperationException("Storm camp story expected " + ExpectedStoryObjectCount +
                                                    " direct props, found " + root.transform.childCount + ".");

            if (root.GetComponentsInChildren<Collider>(true).Length != 0)
                throw new InvalidOperationException("Storm camp story must remain collider-free.");
            if (root.GetComponentsInChildren<Rigidbody>(true).Length != 0)
                throw new InvalidOperationException("Storm camp story must remain physics-free.");
            if (root.GetComponentsInChildren<ParticleSystem>(true).Length != 0)
                throw new InvalidOperationException("Storm camp story must add no particle systems.");
            if (root.GetComponentsInChildren<Light>(true).Length != 0)
                throw new InvalidOperationException("Storm camp story must add no lights.");
            if (root.GetComponentsInChildren<Animation>(true).Length != 0 ||
                root.GetComponentsInChildren<Animator>(true).Length != 0)
                throw new InvalidOperationException("Storm camp story must add no animation components.");

            long triangles = 0;
            foreach (MeshFilter filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh != null)
                    triangles += filter.sharedMesh.triangles.LongLength / 3L;
            }

            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            int materialSlots = renderers.Sum(renderer =>
                renderer.sharedMaterials == null ? 0 : renderer.sharedMaterials.Length);
            if (triangles > TriangleHardLimit)
                throw new InvalidOperationException("Storm camp story triangle proxy " + triangles +
                                                    " exceeds " + TriangleHardLimit + ".");
            if (materialSlots > MaterialSlotHardLimit)
                throw new InvalidOperationException("Storm camp story material-slot proxy " + materialSlots +
                                                    " exceeds " + MaterialSlotHardLimit + ".");

            foreach (StorySpec spec in Specs)
            {
                Transform child = root.transform.Find(spec.name);
                if (child == null)
                    throw new InvalidOperationException("Storm camp story object missing: " + spec.name);

                string prefabPath = PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(child.gameObject);
                string stem = string.IsNullOrEmpty(prefabPath)
                    ? string.Empty
                    : Path.GetFileNameWithoutExtension(prefabPath).ToLowerInvariant().Replace('-', '_');
                string expectedPrefix = spec.prefix.ToLowerInvariant();
                string expectedToken = spec.token.ToLowerInvariant().Replace('-', '_');
                if (!stem.StartsWith(expectedPrefix, StringComparison.Ordinal) || !stem.Contains(expectedToken))
                    throw new InvalidOperationException("Wrong canonical story state on " + spec.name + ": " + stem);
            }
        }

        private static void RemoveExistingStory()
        {
            GameObject existing = GameObject.Find(StoryRootName);
            if (existing != null)
                UnityEngine.Object.DestroyImmediate(existing);
        }
    }
}
