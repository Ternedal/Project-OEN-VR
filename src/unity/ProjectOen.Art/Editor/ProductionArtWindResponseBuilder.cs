using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Adds lightweight wind response to selected Stormnatten dressing without
    /// introducing per-object Update() scripts. Each target receives a tiny legacy
    /// AnimationClip that only animates local X/Z rotation; the authored yaw and
    /// world placement from ProductionArtShowcaseBuilder therefore stay intact.
    ///
    /// Quest 2 contract:
    /// - nine bounded Animation components;
    /// - no shaders, particles, lights, colliders or runtime scripts;
    /// - clips are looped, renderer-culled and deterministic;
    /// - animation assets are updated in place so their Unity GUIDs stay stable.
    /// </summary>
    public static class ProductionArtWindResponseBuilder
    {
        private const string ScenePath = "Assets/ProductionArt/Scenes/StormnattenArtShowcase.unity";
        private const string AnimationRoot = "Assets/ProductionArt/Animations";
        private const string WindAnimationRoot = AnimationRoot + "/StormWind";
        private const int SamplesPerClip = 12;

        private sealed class WindSpec
        {
            public string TargetName;
            public float XDegrees;
            public float ZDegrees;
            public float Duration;
            public float Phase;

            public WindSpec(string targetName, float xDegrees, float zDegrees, float duration, float phase)
            {
                TargetName = targetName;
                XDegrees = xDegrees;
                ZDegrees = zDegrees;
                Duration = duration;
                Phase = phase;
            }
        }

        private static readonly WindSpec[] Specs =
        {
            new WindSpec("Loose Storm Cloth", 2.8f, 6.5f, 1.15f, 0.05f),
            new WindSpec("Rain Catcher Cloth", 1.5f, 3.2f, 1.40f, 0.32f),
            new WindSpec("Signal Cloth", 2.2f, 5.8f, 1.05f, 0.61f),
            new WindSpec("Signal Spare Ropes", 1.8f, 4.5f, 1.30f, 0.83f),
            new WindSpec("Palm Mature A", 0.8f, 2.6f, 2.40f, 0.14f),
            new WindSpec("Palm Mature B", 0.7f, 2.2f, 2.10f, 0.48f),
            new WindSpec("Palm Frond Clutter A", 1.4f, 4.5f, 1.70f, 0.73f),
            new WindSpec("Palm Frond Clutter B", 1.2f, 3.8f, 1.55f, 0.91f),
            new WindSpec("Vines", 2.0f, 3.6f, 1.95f, 0.26f),
        };

        [MenuItem("Project OEN/Art/Add Wind Response To Showcase")]
        public static void AddWindResponse()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
                throw new InvalidOperationException("Showcase scene missing: " + ScenePath);

            EnsureFolder(AnimationRoot);
            EnsureFolder(WindAnimationRoot);
            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var missing = new List<string>();
            int wired = 0;

            for (int i = 0; i < Specs.Length; i++)
            {
                WindSpec spec = Specs[i];
                GameObject target = GameObject.Find(spec.TargetName);
                if (target == null)
                {
                    missing.Add(spec.TargetName);
                    continue;
                }

                AnimationClip clip = BuildOrUpdateClip(spec, i);
                Animation existing = target.GetComponent<Animation>();
                if (existing != null)
                    UnityEngine.Object.DestroyImmediate(existing);

                Animation animation = target.AddComponent<Animation>();
                animation.playAutomatically = true;
                animation.cullingType = AnimationCullingType.BasedOnRenderers;
                animation.AddClip(clip, clip.name);
                animation.clip = clip;
                wired++;
            }

            if (missing.Count > 0)
                throw new InvalidOperationException("Wind-response target(s) missing: " + string.Join(", ", missing));
            if (wired != Specs.Length)
                throw new InvalidOperationException("Expected " + Specs.Length + " wind-responsive objects, wired " + wired + ".");

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[ProjectOEN.Art.Wind] Added deterministic renderer-culled wind response to " + wired +
                      " Stormnatten dressing objects using legacy AnimationClips only.");
        }

        private static AnimationClip BuildOrUpdateClip(WindSpec spec, int index)
        {
            string stem = Slug(spec.TargetName) + "_wind";
            string path = WindAnimationRoot + "/" + stem + ".anim";
            AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
            if (clip == null)
            {
                clip = new AnimationClip { name = stem };
                AssetDatabase.CreateAsset(clip, path);
            }
            else
            {
                clip.ClearCurves();
                clip.name = stem;
            }

            clip.legacy = true;
            clip.wrapMode = WrapMode.Loop;
            clip.frameRate = 30f;

            AnimationCurve x = BuildSwayCurve(spec.XDegrees, spec.Duration, spec.Phase, index * 0.17f);
            AnimationCurve z = BuildSwayCurve(spec.ZDegrees, spec.Duration, spec.Phase + 0.21f, index * 0.11f);
            clip.SetCurve(string.Empty, typeof(Transform), "localEulerAnglesRaw.x", x);
            clip.SetCurve(string.Empty, typeof(Transform), "localEulerAnglesRaw.z", z);
            EditorUtility.SetDirty(clip);
            return clip;
        }

        private static AnimationCurve BuildSwayCurve(float amplitude, float duration, float phase, float harmonicPhase)
        {
            var curve = new AnimationCurve();
            for (int i = 0; i <= SamplesPerClip; i++)
            {
                float t = duration * i / SamplesPerClip;
                float normalized = t / duration;
                float primary = Mathf.Sin((normalized + phase) * Mathf.PI * 2f);
                float harmonic = Mathf.Sin((normalized * 2f + phase + harmonicPhase) * Mathf.PI * 2f);
                float angle = amplitude * (primary * 0.78f + harmonic * 0.22f);
                curve.AddKey(new Keyframe(t, angle));
            }
            curve.preWrapMode = WrapMode.Loop;
            curve.postWrapMode = WrapMode.Loop;
            return curve;
        }

        private static string Slug(string value)
        {
            return value.ToLowerInvariant()
                .Replace(" ", "_")
                .Replace("-", "_")
                .Replace("/", "_");
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path))
                return;
            int slash = path.LastIndexOf('/');
            if (slash <= 0)
                throw new InvalidOperationException("Invalid Unity asset folder: " + path);
            string parent = path.Substring(0, slash);
            string leaf = path.Substring(slash + 1);
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, leaf);
        }
    }
}
