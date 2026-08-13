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
    /// here because prefab assets cannot reference scene objects. The staged first-playable
    /// manifest is verified before any scene mutation so direct install cannot bypass one-click integrity gates.
    /// </summary>
    public static class ProjectOenAudioSceneInstaller
    {
        private const string AudioRoot = "Assets/ProjectOen/Audio";
        private const string CatalogPath = AudioRoot + "/Definitions/AudioCatalog.asset";
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

            var manifest = ProjectOenAudioFirstPlayableManifestAudit.Audit();
            if (!manifest.Ok)
            {
                Debug.LogError(
                    "Project Oen audio scene install stopped: first-playable manifest/import audit failed. " +
                    manifest.Error);
                return;
            }

            var coverage = (clipCount: manifest.ClipCount, eventCount: manifest.EventCount);
            if (coverage.clipCount < ExpectedFirstPlayableClipCount ||
                coverage.eventCount < ExpectedFirstPlayableEventCount)
            {
                Debug.LogError(
                    "Project Oen audio scene install stopped: incomplete first-playable audio import. " +
                    $"Found {coverage.clipCount}/{ExpectedFirstPlayableClipCount} manifest-verified canonical clips across " +
                    $"{coverage.eventCount}/{ExpectedFirstPlayableEventCount} events below '{AudioRoot}'.");
                return;
            }

            var catalog = AssetDatabase.LoadAssetAtPath<AudioCatalog>(CatalogPath);
            if (catalog == null || catalog.Events.Count != manifest.EventCount)
            {
                Debug.LogError(
                    "Project Oen audio scene install stopped: generated catalog is missing or does not match the current staged manifest. " +
                    $"Catalog events={(catalog == null ? 0 : catalog.Events.Count)}, manifest events={manifest.EventCount}. " +
                    "Run Build First Playable (One Click) before installing the scene runtime.");
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

            var manifest = ProjectOenAudioFirstPlayableManifestAudit.Audit();
            var services = FindInScene<AudioService>(scene);
            var routers = FindInScene<AudioWorldStateRouter>(scene);
            var followers = FindInScene<AudioWorldAnchorFollower>(scene);
            var emitterRouters = FindInScene<AudioWorldStateEmitterRouter>(scene);
            var randomEmitters = FindInScene<AudioRandomEmitter>(scene);
            var listeners = FindActiveListeners(scene);
            var coverage = manifest.Ok
                ? (clipCount: manifest.ClipCount, eventCount: manifest.EventCount)
                : (clipCount: 0, eventCount: 0);
            var catalog = AssetDatabase.LoadAssetAtPath<AudioCatalog>(CatalogPath);

            var coverageOk = manifest.Ok &&
                             coverage.clipCount >= ExpectedFirstPlayableClipCount &&
                             coverage.eventCount >= ExpectedFirstPlayableEventCount;
            var catalogOk = manifest.Ok && catalog != null && catalog.Events.Count == manifest.EventCount;
            var generatedRuntimeOk = services.Count == 1 &&
                                     ResolveExistingGeneratedRuntimeRoot(services[0]) != null;

            var followerTargetCount = 0;
            if (listeners.Count == 1)
            {
                for (var i = 0; i < followers.Count; i++)
                {
                    var follower = followers[i];
                    if (follower != null &&
                        follower.Target == listeners[0].transform &&
                        follower.gameObject.activeInHierarchy)
                    {
                        followerTargetCount++;
                    }
                }
            }

            var ok = coverageOk &&
                     catalogOk &&
                     generatedRuntimeOk &&
                     routers.Count == 1 &&
                     followers.Count >= 2 &&
                     emitterRouters.Count >= 2 &&
                     randomEmitters.Count >= 2 &&
                     listeners.Count == 1 &&
                     followerTargetCount >= 2;

            if (!manifest.Ok)
                Debug.LogError("Project Oen active-scene audio audit: manifest/import integrity failed: " + manifest.Error);

            if (!coverageOk)
            {
                Debug.LogError(
                    $"Project Oen active-scene audio audit: incomplete audio import: {coverage.clipCount}/" +
                    $"{ExpectedFirstPlayableClipCount} clips across {coverage.eventCount}/" +
                    $"{ExpectedFirstPlayableEventCount} events.");
            }

            if (!catalogOk)
            {
                Debug.LogError(
                    $"Project Oen active-scene audio audit: catalog/manifest mismatch: " +
                    $"catalog={(catalog == null ? 0 : catalog.Events.Count)}, manifest={(manifest.Ok ? manifest.EventCount : 0)}.");
            }

            if (!generatedRuntimeOk)
            {
                Debug.LogError(
                    "Project Oen active-scene audio audit: expected exactly one AudioService owned by the generated first-playable prefab instance.");
            }

            if (listeners.Count != 1)
            {
                Debug.LogError(
                    $"Project Oen active-scene audio audit: expected exactly one active AudioListener, found {listeners.Count}. " +
                    "Listener-relative world emitters are intentionally disabled until ownership is unambiguous.");
            }
            else if (followerTargetCount < 2)
            {
                Debug.LogError(
                    "Project Oen active-scene audio audit: both active WorldFauna and WorldWeather anchors must be bound to the active AudioListener.");
            }

            if (!ok)
            {
                Debug.LogError(
                    "Project Oen active-scene audio audit failed: expected verified first-playable payload/catalog, one generated AudioService/router, " +
                    "and active listener-bound WorldFauna + WorldWeather follower/router/emitter sets.");
            }

            Debug.Log(
                $"Project Oen active-scene audio audit: manifest={(manifest.Ok ? "OK" : "FAILED")}, " +
                $"coverage={coverage.clipCount}/{coverage.eventCount}, catalog={(catalogOk ? "OK" : "MISMATCH")}, " +
                $"generatedRuntime={(generatedRuntimeOk ? "OK" : "INVALID")}, services={services.Count}, routers={routers.Count}, " +
                $"worldAnchors={followers.Count}, emitterRouters={emitterRouters.Count}, randomEmitters={randomEmitters.Count}, " +
                $"listenerBoundAnchors={followerTargetCount}, activeListeners={listeners.Count}, status={(ok ? "OK" : "FAILED")}.");
        }

        private static (int clipCount, int eventCount) MeasureCanonicalClipCoverage()
        {
            var manifest = ProjectOenAudioFirstPlayableManifestAudit.Audit();
            return manifest.Ok
                ? (manifest.ClipCount, manifest.EventCount)
                : (0, 0);
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
