using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Adds a small, deterministic storm-FX layer to the generated Stormnatten
    /// showcase by reusing the already validated production VFX prefabs.
    ///
    /// Quest 2 constraints:
    /// - two extra particle systems only (wind debris + ground rain splashes);
    /// - one non-shadowing directional flash light;
    /// - no particle collision, no realtime shadowing, no custom shader;
    /// - lightning uses a legacy AnimationClip instead of an Update() script.
    /// </summary>
    public static class ProductionArtStormFxBuilder
    {
        private const string ScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/StormnattenArtShowcase.unity";
        private const string VfxPrefabRoot = "Assets/ProjectOEN/ProductionArt/VfxPrefabs";
        private const string AnimationRoot = "Assets/ProjectOEN/ProductionArt/Animations";
        private const string LightningClipPath = AnimationRoot + "/storm_lightning_loop.anim";

        private const string WindDebrisName = "Windblown Storm Debris";
        private const string RainSplashName = "Camp Rain Splashes";
        private const string LightningName = "Distant Storm Lightning";

        [MenuItem("Project OEN/Art/Add Storm Motion FX To Showcase")]
        public static void AddStormMotionFx()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
                throw new InvalidOperationException("Showcase scene missing: " + ScenePath);
            if (!AssetDatabase.IsValidFolder(VfxPrefabRoot))
                throw new InvalidOperationException("Production VFX prefabs missing: " + VfxPrefabRoot);

            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            RemoveExisting(WindDebrisName);
            RemoveExisting(RainSplashName);
            RemoveExisting(LightningName);

            BuildWindDebris();
            BuildCampRainSplashes();
            BuildDistantLightning();

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[ProjectOEN.Art.StormFX] Added wind debris, camp rain splashes and distant lightning " +
                      "to Stormnatten (2 particle systems, 1 non-shadowing flash light, no collision).");
        }

        private static void BuildWindDebris()
        {
            GameObject prefab = FindVfxPrefab("fx_003_single_ash");
            GameObject go = Instantiate(prefab, WindDebrisName);
            go.transform.position = new Vector3(0f, 2.6f, 0f);

            ParticleSystem ps = RequireParticleSystem(go, WindDebrisName);
            ParticleSystem.MainModule main = ps.main;
            main.playOnAwake = true;
            main.loop = true;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.maxParticles = 24;
            main.startLifetime = new ParticleSystem.MinMaxCurve(1.8f, 2.6f);
            main.startSpeed = 0f;
            main.startSize = new ParticleSystem.MinMaxCurve(0.035f, 0.085f);
            main.startColor = new ParticleSystem.MinMaxGradient(
                new Color(0.42f, 0.43f, 0.39f, 0.20f),
                new Color(0.68f, 0.61f, 0.48f, 0.38f));

            ParticleSystem.EmissionModule emission = ps.emission;
            emission.rateOverTime = 5.0f;

            ParticleSystem.ShapeModule shape = ps.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(15f, 3.5f, 15f);

            ParticleSystem.VelocityOverLifetimeModule velocity = ps.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = new ParticleSystem.MinMaxCurve(-3.2f, -1.8f);
            velocity.y = new ParticleSystem.MinMaxCurve(-0.35f, 0.18f);
            velocity.z = new ParticleSystem.MinMaxCurve(0.15f, 0.95f);

            ParticleSystemRenderer renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        private static void BuildCampRainSplashes()
        {
            GameObject prefab = FindVfxPrefab("fx_004_medium_rain_splash");
            GameObject go = Instantiate(prefab, RainSplashName);
            go.transform.position = new Vector3(-0.1f, 0.035f, 0.2f);

            ParticleSystem ps = RequireParticleSystem(go, RainSplashName);
            ParticleSystem.MainModule main = ps.main;
            main.playOnAwake = true;
            main.loop = true;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.maxParticles = 12;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.22f, 0.38f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(0.02f, 0.06f);
            main.startSize = new ParticleSystem.MinMaxCurve(0.18f, 0.34f);

            ParticleSystem.EmissionModule emission = ps.emission;
            emission.rateOverTime = 8.0f;

            ParticleSystem.ShapeModule shape = ps.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(6.5f, 0.04f, 6.5f);

            ParticleSystemRenderer renderer = ps.GetComponent<ParticleSystemRenderer>();
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        private static void BuildDistantLightning()
        {
            EnsureFolder(AnimationRoot);

            GameObject prefab = FindVfxPrefab("fx_006_far_lightning");
            GameObject go = Instantiate(prefab, LightningName);
            go.transform.position = new Vector3(-7.8f, 6.2f, 12.0f);

            Camera camera = UnityEngine.Object.FindObjectOfType<Camera>();
            if (camera != null)
            {
                go.transform.LookAt(camera.transform.position);
                go.transform.Rotate(0f, 180f, 0f, Space.Self);
            }

            SpriteRenderer spriteRenderer = go.GetComponentInChildren<SpriteRenderer>(true);
            if (spriteRenderer == null)
                throw new InvalidOperationException("Lightning VFX prefab has no SpriteRenderer.");
            spriteRenderer.color = new Color(0.72f, 0.82f, 1.0f, 0.10f);
            spriteRenderer.shadowCastingMode = ShadowCastingMode.Off;
            spriteRenderer.receiveShadows = false;

            Light flash = go.GetComponent<Light>();
            if (flash == null)
                flash = go.AddComponent<Light>();
            flash.type = LightType.Directional;
            flash.color = new Color(0.63f, 0.77f, 1.0f);
            flash.intensity = 0f;
            flash.shadows = LightShadows.None;
            flash.transform.rotation = Quaternion.Euler(28f, 118f, 0f);

            AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(LightningClipPath);
            if (clip == null)
            {
                clip = new AnimationClip { name = "storm_lightning_loop" };
                clip.legacy = true;
                clip.frameRate = 30f;
                AssetDatabase.CreateAsset(clip, LightningClipPath);
            }
            else
            {
                clip.legacy = true;
                clip.frameRate = 30f;
                foreach (EditorCurveBinding binding in AnimationUtility.GetCurveBindings(clip))
                    AnimationUtility.SetEditorCurve(clip, binding, null);
            }

            clip.wrapMode = WrapMode.Loop;
            AnimationCurve alphaCurve = new AnimationCurve(
                new Keyframe(0.00f, 0.10f),
                new Keyframe(4.72f, 0.10f),
                new Keyframe(4.76f, 0.95f),
                new Keyframe(4.84f, 0.24f),
                new Keyframe(4.91f, 1.00f),
                new Keyframe(5.02f, 0.10f),
                new Keyframe(8.00f, 0.10f));
            AnimationCurve lightCurve = new AnimationCurve(
                new Keyframe(0.00f, 0.00f),
                new Keyframe(4.72f, 0.00f),
                new Keyframe(4.76f, 0.55f),
                new Keyframe(4.84f, 0.12f),
                new Keyframe(4.91f, 0.72f),
                new Keyframe(5.02f, 0.00f),
                new Keyframe(8.00f, 0.00f));

            clip.SetCurve(string.Empty, typeof(SpriteRenderer), "m_Color.a", alphaCurve);
            clip.SetCurve(string.Empty, typeof(Light), "m_Intensity", lightCurve);
            EditorUtility.SetDirty(clip);

            Animation animation = go.GetComponent<Animation>();
            if (animation == null)
                animation = go.AddComponent<Animation>();
            animation.playAutomatically = true;
            animation.AddClip(clip, clip.name);
            animation.clip = clip;
        }

        private static GameObject FindVfxPrefab(string stem)
        {
            string[] guids = AssetDatabase.FindAssets("t:Prefab", new[] { VfxPrefabRoot });
            string path = guids
                .Select(AssetDatabase.GUIDToAssetPath)
                .FirstOrDefault(p => string.Equals(Path.GetFileNameWithoutExtension(p), stem, StringComparison.OrdinalIgnoreCase));
            if (string.IsNullOrEmpty(path))
                throw new InvalidOperationException("Required production VFX prefab missing: " + stem);

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null)
                throw new InvalidOperationException("Could not load production VFX prefab: " + path);
            return prefab;
        }

        private static GameObject Instantiate(GameObject prefab, string instanceName)
        {
            GameObject instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (instance == null)
                throw new InvalidOperationException("Could not instantiate VFX prefab: " + prefab.name);
            instance.name = instanceName;
            return instance;
        }

        private static ParticleSystem RequireParticleSystem(GameObject go, string label)
        {
            ParticleSystem ps = go.GetComponentInChildren<ParticleSystem>(true);
            if (ps == null)
                throw new InvalidOperationException(label + " has no ParticleSystem.");
            return ps;
        }

        private static void RemoveExisting(string name)
        {
            GameObject existing = GameObject.Find(name);
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
