using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ProjectOen.Audio.Editor
{
    /// <summary>
    /// Installs the generated first-playable audio runtime into the active saved scene without
    /// creating duplicate AudioService instances. Scene-specific listener references are wired
    /// here because prefab assets cannot reference scene objects.
    /// </summary>
    public static class ProjectOenAudioSceneInstaller
    {
        private const string RuntimePrefabPath =
            "Assets/ProjectOen/Audio/GeneratedFirstPlayable/Runtime/AudioRuntime_FirstPlayable.prefab";
        private const string RuntimeName = "AudioRuntime_FirstPlayable";
        private const string WorldFaunaName = "WorldFauna";
        private const string CicadaEmitterName = "JungleDay_Cicadas";

        [MenuItem("Project Oen/Audio/Build + Install First Playable (One Click)", priority = -10)]
        public static void BuildAndInstall()
        {
            ProjectOenAudioOneClickFirstPlayableBuilder.BuildOneClick();
            InstallIntoActiveScene();
        }

        [MenuItem("Project Oen/Audio/Install First-Playable Runtime Into Active Scene")]
        public static void InstallIntoActiveScene()
        {
            if (PrefabStageUtility.GetCurrentPrefabStage() != null)
            {
                Debug.LogError(
                    "Project Oen audio scene install stopped: close Prefab Mode and return to a normal scene first.");
                return;
            }

            var scene = SceneManager.GetActiveScene();
            if (!scene.IsValid() || !scene.isLoaded)
            {
                Debug.LogError("Project Oen audio scene install stopped: there is no valid loaded active scene.");
                return;
            }

            if (string.IsNullOrWhiteSpace(scene.path))
            {
                Debug.LogError(
                    "Project Oen audio scene install stopped: save the active scene before installing the runtime.");
                return;
            }

            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(RuntimePrefabPath);
            if (prefab == null)
            {
                Debug.LogError(
                    $"Project Oen audio scene install stopped: missing generated runtime prefab '{RuntimePrefabPath}'. " +
                    "Run Build First Playable (One Click) first.");
                return;
            }

            var services = FindInScene<AudioService>(scene);
            if (services.Count > 1)
            {
                Debug.LogError(
                    $"Project Oen audio scene install stopped: active scene already contains {services.Count} AudioService components. " +
                    "Resolve the duplicate runtime ownership before installing.");
                return;
            }

            GameObject runtimeRoot;
            if (services.Count == 1)
            {
                runtimeRoot = ResolveExistingGeneratedRuntimeRoot(services[0]);
                if (runtimeRoot == null)
                {
                    Debug.LogError(
                        "Project Oen audio scene install stopped: an existing AudioService is not an instance of the generated " +
                        "first-playable runtime. It will not be overwritten or duplicated.",
                        services[0]);
                    return;
                }
            }
            else
            {
                runtimeRoot = PrefabUtility.InstantiatePrefab(prefab, scene) as GameObject;
                if (runtimeRoot == null)
                {
                    Debug.LogError("Project Oen audio scene install failed to instantiate the generated runtime prefab.");
                    return;
                }

                Undo.RegisterCreatedObjectUndo(runtimeRoot, "Install Project Oen Audio Runtime");
                runtimeRoot.name = RuntimeName;
            }

            var service = runtimeRoot.GetComponent<AudioService>();
            var worldState = runtimeRoot.GetComponent<AudioWorldStateRouter>();
            if (service == null || worldState == null)
            {
                Debug.LogError(
                    "Project Oen audio scene install stopped: generated runtime instance lacks AudioService or AudioWorldStateRouter.",
                    runtimeRoot);
                return;
            }

            ConfigureWorldFauna(runtimeRoot, service, worldState, scene);
            EditorSceneManager.MarkSceneDirty(scene);
            Selection.activeGameObject = runtimeRoot;

            AuditActiveScene();
            Debug.Log(
                $"Project Oen audio scene install complete in '{scene.name}'. " +
                "The scene was marked dirty but not auto-saved.",
                runtimeRoot);
        }

        [MenuItem("Project Oen/Audio/Audit Active Scene Audio Runtime")]
        public static void AuditActiveScene()
        {
            var scene = SceneManager.GetActiveScene();
            if (!scene.IsValid() || !scene.isLoaded)
            {
                Debug.LogError("Project Oen active-scene audio audit: no valid loaded active scene.");
                return;
            }

            var services = FindInScene<AudioService>(scene);
            var routers = FindInScene<AudioWorldStateRouter>(scene);
            var followers = FindInScene<AudioWorldAnchorFollower>(scene);
            var emitterRouters = FindInScene<AudioWorldStateEmitterRouter>(scene);
            var randomEmitters = FindInScene<AudioRandomEmitter>(scene);
            var listeners = FindActiveListeners(scene);

            var ok = services.Count == 1 &&
                     routers.Count == 1 &&
                     followers.Count >= 1 &&
                     emitterRouters.Count >= 1 &&
                     randomEmitters.Count >= 1;

            if (!ok)
            {
                Debug.LogError(
                    "Project Oen active-scene audio audit failed: expected one AudioService/router and at least one " +
                    "WorldFauna follower/state-router/random-emitter set.");
            }

            if (listeners.Count != 1)
            {
                Debug.LogWarning(
                    $"Project Oen active-scene audio audit: expected exactly one active AudioListener, found {listeners.Count}. " +
                    "WorldFauna must stay disabled until listener ownership is unambiguous.");
            }

            var followerTargetOk = followers.Count > 0 &&
                                   listeners.Count == 1 &&
                                   followers.Exists(follower => follower != null && follower.Target == listeners[0].transform);
            if (listeners.Count == 1 && !followerTargetOk)
            {
                Debug.LogError(
                    "Project Oen active-scene audio audit: WorldFauna anchor is not bound to the active AudioListener.");
            }

            Debug.Log(
                $"Project Oen active-scene audio audit: services={services.Count}, routers={routers.Count}, " +
                $"worldAnchors={followers.Count}, emitterRouters={emitterRouters.Count}, randomEmitters={randomEmitters.Count}, " +
                $"activeListeners={listeners.Count}, status={(ok && (listeners.Count != 1 || followerTargetOk) ? "OK" : "CHECK")}.");
        }

        private static GameObject ResolveExistingGeneratedRuntimeRoot(AudioService service)
        {
            if (service == null)
                return null;

            var instanceRoot = PrefabUtility.GetOutermostPrefabInstanceRoot(service.gameObject);
            if (instanceRoot == null)
                return null;

            var source = PrefabUtility.GetCorrespondingObjectFromSource(instanceRoot);
            if (source == null)
                return null;

            var sourcePath = AssetDatabase.GetAssetPath(source);
            return sourcePath == RuntimePrefabPath ? instanceRoot : null;
        }

        private static void ConfigureWorldFauna(
            GameObject runtimeRoot,
            AudioService service,
            AudioWorldStateRouter worldState,
            Scene scene)
        {
            var worldFauna = FindDirectChild(runtimeRoot.transform, WorldFaunaName);
            if (worldFauna == null)
            {
                var created = new GameObject(WorldFaunaName);
                Undo.RegisterCreatedObjectUndo(created, "Create Project Oen WorldFauna");
                created.transform.SetParent(runtimeRoot.transform, false);
                worldFauna = created.transform;
            }

            var follower = worldFauna.GetComponent<AudioWorldAnchorFollower>();
            if (follower == null)
                follower = Undo.AddComponent<AudioWorldAnchorFollower>(worldFauna.gameObject);

            var cicadaTransform = FindDirectChild(worldFauna, CicadaEmitterName);
            if (cicadaTransform == null)
            {
                var created = new GameObject(CicadaEmitterName);
                Undo.RegisterCreatedObjectUndo(created, "Create Project Oen Cicada Emitter");
                created.transform.SetParent(worldFauna, false);
                cicadaTransform = created.transform;
            }

            var cicadaEmitter = cicadaTransform.GetComponent<AudioRandomEmitter>();
            if (cicadaEmitter == null)
                cicadaEmitter = Undo.AddComponent<AudioRandomEmitter>(cicadaTransform.gameObject);
            ConfigureCicadaEmitter(cicadaEmitter, service);

            var emitterRouter = worldFauna.GetComponent<AudioWorldStateEmitterRouter>();
            if (emitterRouter == null)
                emitterRouter = Undo.AddComponent<AudioWorldStateEmitterRouter>(worldFauna.gameObject);
            ConfigureEmitterRouter(emitterRouter, worldState, cicadaEmitter);

            var listeners = FindActiveListeners(scene);
            Undo.RecordObject(worldFauna.gameObject, "Configure Project Oen WorldFauna");
            Undo.RecordObject(follower, "Configure Project Oen WorldFauna Anchor");

            if (listeners.Count == 1)
            {
                follower.Configure(listeners[0].transform, false);
                worldFauna.gameObject.SetActive(true);
                EditorUtility.SetDirty(follower);
            }
            else
            {
                follower.Configure(null, false);
                worldFauna.gameObject.SetActive(false);
                EditorUtility.SetDirty(follower);
                Debug.LogWarning(
                    $"Project Oen audio: WorldFauna disabled because active scene has {listeners.Count} active AudioListeners. " +
                    "Resolve listener ownership and rerun the scene installer.",
                    runtimeRoot);
            }
        }

        private static void ConfigureCicadaEmitter(AudioRandomEmitter emitter, AudioService service)
        {
            var serialized = new SerializedObject(emitter);
            serialized.FindProperty("_audioService").objectReferenceValue = service;

            var eventsProperty = serialized.FindProperty("_events");
            eventsProperty.arraySize = 1;
            eventsProperty.GetArrayElementAtIndex(0).intValue = (int)AudioEventId.SFX_NAT_Insect_CicadaCluster;

            serialized.FindProperty("_delaySeconds").vector2Value = new Vector2(14f, 34f);
            serialized.FindProperty("_horizontalRadius").floatValue = 18f;
            serialized.FindProperty("_verticalJitter").floatValue = 2.5f;
            serialized.FindProperty("_playOnEnable").boolValue = false;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(emitter);
        }

        private static void ConfigureEmitterRouter(
            AudioWorldStateEmitterRouter emitterRouter,
            AudioWorldStateRouter worldState,
            AudioRandomEmitter cicadaEmitter)
        {
            var serialized = new SerializedObject(emitterRouter);
            serialized.FindProperty("_worldState").objectReferenceValue = worldState;

            var bindings = serialized.FindProperty("_bindings");
            bindings.arraySize = 1;
            var binding = bindings.GetArrayElementAtIndex(0);
            binding.FindPropertyRelative("_emitter").objectReferenceValue = cicadaEmitter;
            binding.FindPropertyRelative("_biome").intValue = (int)AudioBiome.Jungle;
            binding.FindPropertyRelative("_dayPhase").intValue = (int)AudioDayPhase.Day;
            binding.FindPropertyRelative("_matchDayPhase").boolValue = true;
            binding.FindPropertyRelative("_exteriorOnly").boolValue = true;

            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(emitterRouter);
        }

        private static List<T> FindInScene<T>(Scene scene) where T : Component
        {
            var result = new List<T>();
            foreach (var root in scene.GetRootGameObjects())
                result.AddRange(root.GetComponentsInChildren<T>(true));
            return result;
        }

        private static List<AudioListener> FindActiveListeners(Scene scene)
        {
            var result = FindInScene<AudioListener>(scene);
            result.RemoveAll(listener => listener == null || !listener.enabled || !listener.gameObject.activeInHierarchy);
            return result;
        }

        private static Transform FindDirectChild(Transform parent, string name)
        {
            if (parent == null)
                return null;

            for (var index = 0; index < parent.childCount; index++)
            {
                var child = parent.GetChild(index);
                if (child.name == name)
                    return child;
            }

            return null;
        }
    }
}
