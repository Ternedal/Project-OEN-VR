using System;
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
        private const string AudioRoot = "Assets/ProjectOen/Audio";
        private const string RuntimePrefabPath =
            "Assets/ProjectOen/Audio/GeneratedFirstPlayable/Runtime/AudioRuntime_FirstPlayable.prefab";
        private const string RuntimeName = "AudioRuntime_FirstPlayable";
        private const string WorldFaunaName = "WorldFauna";
        private const string WorldWeatherName = "WorldWeather";
        private const string CicadaEmitterName = "JungleDay_Cicadas";
        private const string ThunderEmitterName = "RainFire_ThunderFar";
        private const int ExpectedFirstPlayableClipCount = 160;
        private const int ExpectedFirstPlayableEventCount = 45;

        [MenuItem("Project Oen/Audio/Build + Install First Playable (One Click)", priority = -10)]
        public static void BuildAndInstall()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                Debug.LogError(
                    "Project Oen audio build/install stopped: exit Play Mode before mutating generated audio assets or scene composition.");
                return;
            }

            ProjectOenAudioOneClickFirstPlayableBuilder.BuildOneClick();
            InstallIntoActiveScene();
        }

        [MenuItem("Project Oen/Audio/Install First-Playable Runtime Into Active Scene")]
        public static void InstallIntoActiveScene()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                Debug.LogError(
                    "Project Oen audio scene install stopped: exit Play Mode before changing scene composition.");
                return;
            }

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

            var coverage = MeasureCanonicalClipCoverage();
            if (coverage.clipCount < ExpectedFirstPlayableClipCount ||
                coverage.eventCount < ExpectedFirstPlayableEventCount)
            {
                Debug.LogError(
                    "Project Oen audio scene install stopped: incomplete first-playable audio import. " +
                    $"Found {coverage.clipCount}/{ExpectedFirstPlayableClipCount} canonical clips across " +
                    $"{coverage.eventCount}/{ExpectedFirstPlayableEventCount} events below '{AudioRoot}'.");
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

            var listeners = FindActiveListeners(scene);
            ConfigureWorldFauna(runtimeRoot, service, worldState, listeners);
            ConfigureWorldWeather(runtimeRoot, service, worldState, listeners);

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
            var coverage = MeasureCanonicalClipCoverage();

            var coverageOk = coverage.clipCount >= ExpectedFirstPlayableClipCount &&
                             coverage.eventCount >= ExpectedFirstPlayableEventCount;
            var ok = coverageOk &&
                     services.Count == 1 &&
                     routers.Count == 1 &&
                     followers.Count >= 2 &&
                     emitterRouters.Count >= 2 &&
                     randomEmitters.Count >= 2;

            if (!coverageOk)
            {
                Debug.LogError(
                    $"Project Oen active-scene audio audit: incomplete audio import: {coverage.clipCount}/" +
                    $"{ExpectedFirstPlayableClipCount} clips across {coverage.eventCount}/" +
                    $"{ExpectedFirstPlayableEventCount} events.");
            }

            if (!ok)
            {
                Debug.LogError(
                    "Project Oen active-scene audio audit failed: expected complete first-playable coverage, one AudioService/router, " +
                    "and listener-relative WorldFauna + WorldWeather follower/router/emitter sets.");
            }

            if (listeners.Count != 1)
            {
                Debug.LogWarning(
                    $"Project Oen active-scene audio audit: expected exactly one active AudioListener, found {listeners.Count}. " +
                    "Listener-relative world emitters must stay disabled until listener ownership is unambiguous.");
            }

            var followerTargetCount = 0;
            if (listeners.Count == 1)
            {
                for (var i = 0; i < followers.Count; i++)
                {
                    var follower = followers[i];
                    if (follower != null && follower.Target == listeners[0].transform)
                        followerTargetCount++;
                }

                if (followerTargetCount < 2)
                {
                    Debug.LogError(
                        "Project Oen active-scene audio audit: both WorldFauna and WorldWeather anchors must be bound to the active AudioListener.");
                }
            }

            Debug.Log(
                $"Project Oen active-scene audio audit: coverage={coverage.clipCount}/{coverage.eventCount}, " +
                $"services={services.Count}, routers={routers.Count}, worldAnchors={followers.Count}, " +
                $"emitterRouters={emitterRouters.Count}, randomEmitters={randomEmitters.Count}, " +
                $"listenerBoundAnchors={followerTargetCount}, activeListeners={listeners.Count}, " +
                $"status={(ok && (listeners.Count != 1 || followerTargetCount >= 2) ? "OK" : "CHECK")}.");
        }

        private static (int clipCount, int eventCount) MeasureCanonicalClipCoverage()
        {
            if (!AssetDatabase.IsValidFolder(AudioRoot))
                return (0, 0);

            var clipCount = 0;
            var events = new HashSet<AudioEventId>();
            foreach (var guid in AssetDatabase.FindAssets("t:AudioClip", new[] { AudioRoot }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
                if (clip == null || !TryResolveCanonicalClipEvent(clip.name, out var id))
                    continue;

                clipCount++;
                events.Add(id);
            }

            return (clipCount, events.Count);
        }

        private static bool TryResolveCanonicalClipEvent(string clipName, out AudioEventId id)
        {
            id = AudioEventId.None;
            if (string.IsNullOrWhiteSpace(clipName))
                return false;

            var separator = clipName.LastIndexOf('_');
            if (separator <= 0 || separator >= clipName.Length - 1)
                return false;

            var eventName = clipName.Substring(0, separator);
            var variationText = clipName.Substring(separator + 1);
            if (!int.TryParse(variationText, out var variation) || variation <= 0)
                return false;

            if (eventName == "SFX_STS_Hunger_Warn" || eventName == "SFX_STS_Thirst_Warn")
                return false;

            return Enum.TryParse(eventName, out id) && id != AudioEventId.None;
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
            IReadOnlyList<AudioListener> listeners)
        {
            var root = GetOrCreateDirectChild(runtimeRoot.transform, WorldFaunaName, "Create Project Oen WorldFauna");
            var follower = GetOrAddComponent<AudioWorldAnchorFollower>(root.gameObject);

            var cicadaTransform = GetOrCreateDirectChild(root, CicadaEmitterName, "Create Project Oen Cicada Emitter");
            var cicadaEmitter = GetOrAddComponent<AudioRandomEmitter>(cicadaTransform.gameObject);
            ConfigureRandomEmitter(
                cicadaEmitter,
                service,
                AudioEventId.SFX_NAT_Insect_CicadaCluster,
                new Vector2(14f, 34f),
                18f,
                2.5f);

            var emitterRouter = GetOrAddComponent<AudioWorldStateEmitterRouter>(root.gameObject);
            var serialized = new SerializedObject(emitterRouter);
            serialized.FindProperty("_worldState").objectReferenceValue = worldState;
            var bindings = serialized.FindProperty("_bindings");
            bindings.arraySize = 1;
            ConfigureEmitterBinding(
                bindings.GetArrayElementAtIndex(0),
                cicadaEmitter,
                AudioBiome.Jungle,
                true,
                AudioDayPhase.Day,
                true,
                AudioStormPhase.Calm,
                true);
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(emitterRouter);

            BindListenerRelativeRoot(root.gameObject, follower, listeners, "WorldFauna");
        }

        private static void ConfigureWorldWeather(
            GameObject runtimeRoot,
            AudioService service,
            AudioWorldStateRouter worldState,
            IReadOnlyList<AudioListener> listeners)
        {
            var root = GetOrCreateDirectChild(runtimeRoot.transform, WorldWeatherName, "Create Project Oen WorldWeather");
            var follower = GetOrAddComponent<AudioWorldAnchorFollower>(root.gameObject);

            var thunderTransform = GetOrCreateDirectChild(root, ThunderEmitterName, "Create Project Oen Thunder Emitter");
            var thunderEmitter = GetOrAddComponent<AudioRandomEmitter>(thunderTransform.gameObject);
            ConfigureRandomEmitter(
                thunderEmitter,
                service,
                AudioEventId.SFX_WTH_Thunder_Far,
                new Vector2(18f, 42f),
                32f,
                10f);

            var emitterRouter = GetOrAddComponent<AudioWorldStateEmitterRouter>(root.gameObject);
            var serialized = new SerializedObject(emitterRouter);
            serialized.FindProperty("_worldState").objectReferenceValue = worldState;
            var bindings = serialized.FindProperty("_bindings");
            bindings.arraySize = 1;
            ConfigureEmitterBinding(
                bindings.GetArrayElementAtIndex(0),
                thunderEmitter,
                AudioBiome.Beach,
                false,
                AudioDayPhase.Day,
                false,
                AudioStormPhase.RainFire,
                true);
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(emitterRouter);

            BindListenerRelativeRoot(root.gameObject, follower, listeners, "WorldWeather");
        }

        private static void ConfigureRandomEmitter(
            AudioRandomEmitter emitter,
            AudioService service,
            AudioEventId eventId,
            Vector2 delaySeconds,
            float horizontalRadius,
            float verticalJitter)
        {
            var serialized = new SerializedObject(emitter);
            serialized.FindProperty("_audioService").objectReferenceValue = service;

            var eventsProperty = serialized.FindProperty("_events");
            eventsProperty.arraySize = 1;
            eventsProperty.GetArrayElementAtIndex(0).intValue = (int)eventId;

            serialized.FindProperty("_delaySeconds").vector2Value = delaySeconds;
            serialized.FindProperty("_horizontalRadius").floatValue = horizontalRadius;
            serialized.FindProperty("_verticalJitter").floatValue = verticalJitter;
            serialized.FindProperty("_playOnEnable").boolValue = false;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(emitter);
        }

        private static void ConfigureEmitterBinding(
            SerializedProperty binding,
            AudioRandomEmitter emitter,
            AudioBiome biome,
            bool matchBiome,
            AudioDayPhase dayPhase,
            bool matchDayPhase,
            AudioStormPhase stormPhase,
            bool exteriorOnly)
        {
            binding.FindPropertyRelative("_emitter").objectReferenceValue = emitter;
            binding.FindPropertyRelative("_biome").intValue = (int)biome;
            binding.FindPropertyRelative("_matchBiome").boolValue = matchBiome;
            binding.FindPropertyRelative("_dayPhase").intValue = (int)dayPhase;
            binding.FindPropertyRelative("_matchDayPhase").boolValue = matchDayPhase;
            binding.FindPropertyRelative("_stormPhase").intValue = (int)stormPhase;
            binding.FindPropertyRelative("_exteriorOnly").boolValue = exteriorOnly;
        }

        private static void BindListenerRelativeRoot(
            GameObject root,
            AudioWorldAnchorFollower follower,
            IReadOnlyList<AudioListener> listeners,
            string label)
        {
            Undo.RecordObject(root, $"Configure Project Oen {label}");
            Undo.RecordObject(follower, $"Configure Project Oen {label} Anchor");

            if (listeners.Count == 1)
            {
                follower.Configure(listeners[0].transform, false);
                root.SetActive(true);
                EditorUtility.SetDirty(follower);
                return;
            }

            follower.Configure(null, false);
            root.SetActive(false);
            EditorUtility.SetDirty(follower);
            Debug.LogWarning(
                $"Project Oen audio: {label} disabled because active scene has {listeners.Count} active AudioListeners. " +
                "Resolve listener ownership and rerun the scene installer.");
        }

        private static T GetOrAddComponent<T>(GameObject gameObject) where T : Component
        {
            var existing = gameObject.GetComponent<T>();
            return existing != null ? existing : Undo.AddComponent<T>(gameObject);
        }

        private static Transform GetOrCreateDirectChild(Transform parent, string name, string undoName)
        {
            var existing = FindDirectChild(parent, name);
            if (existing != null)
                return existing;

            var created = new GameObject(name);
            Undo.RegisterCreatedObjectUndo(created, undoName);
            created.transform.SetParent(parent, false);
            return created.transform;
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
