using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Audio;

namespace ProjectOen.Audio.Editor
{
    /// <summary>
    /// Safe one-click bootstrap for the first playable.
    ///
    /// It builds clip definitions/catalog first, creates only missing generated profiles,
    /// and creates the runtime prefab only when it does not already exist. Existing profile
    /// tuning and prefab composition are therefore never overwritten by a rerun.
    /// </summary>
    public static class ProjectOenAudioOneClickFirstPlayableBuilder
    {
        private const string AudioRoot = "Assets/ProjectOen/Audio";
        private const string DefinitionsRoot = AudioRoot + "/Definitions";
        private const string CatalogPath = DefinitionsRoot + "/AudioCatalog.asset";
        private const string GeneratedRoot = AudioRoot + "/GeneratedFirstPlayable";
        private const string ProfilesRoot = GeneratedRoot + "/Profiles";
        private const string RuntimeRoot = GeneratedRoot + "/Runtime";
        private const string RuntimePrefabPath = RuntimeRoot + "/AudioRuntime_FirstPlayable.prefab";
        private const int ExpectedFirstPlayableClipCount = 160;
        private const int ExpectedFirstPlayableEventCount = 45;

        private readonly struct LayerSpec
        {
            public LayerSpec(AudioEventId id, float gain)
            {
                Id = id;
                Gain = gain;
            }

            public AudioEventId Id { get; }
            public float Gain { get; }
        }

        [MenuItem("Project Oen/Audio/Build First Playable (One Click)", priority = 0)]
        public static void BuildOneClick()
        {
            var coverage = MeasureCanonicalClipCoverage();
            if (coverage.clipCount < ExpectedFirstPlayableClipCount ||
                coverage.eventCount < ExpectedFirstPlayableEventCount)
            {
                Debug.LogError(
                    "Project Oen audio one-click build stopped: incomplete first-playable audio import. " +
                    $"Found {coverage.clipCount}/{ExpectedFirstPlayableClipCount} canonical clips across " +
                    $"{coverage.eventCount}/{ExpectedFirstPlayableEventCount} events below '{AudioRoot}'. " +
                    "Extract the current oen-unity-first-playable-audio-v1 artifact at the Unity project root first.");
                return;
            }

            ProjectOenAudioFirstPlayableBuilder.BuildFirstPlayable();

            var catalog = AssetDatabase.LoadAssetAtPath<AudioCatalog>(CatalogPath);
            if (catalog == null)
            {
                Debug.LogError(
                    $"Project Oen audio one-click build stopped: '{CatalogPath}' was not created. " +
                    "Import/extract the Unity first-playable audio artifact before running this command.");
                return;
            }

            EnsureFolder(ProfilesRoot);
            EnsureFolder(RuntimeRoot);

            var definitions = FindDefinitions();

            var beachDay = CreateProfileIfMissing(
                "FP_Biome_Beach_Day",
                definitions,
                new LayerSpec(AudioEventId.SFX_AMB_Beach_OceanNear, 1.00f));

            var jungleDay = CreateProfileIfMissing(
                "FP_Biome_Jungle_Day",
                definitions,
                new LayerSpec(AudioEventId.SFX_AMB_Jungle_DayBed, 0.90f));

            var weatherCalm = CreateProfileIfMissing(
                "FP_Weather_Calm",
                definitions);

            var weatherWind = CreateProfileIfMissing(
                "FP_Weather_Wind",
                definitions,
                new LayerSpec(AudioEventId.SFX_WTH_Storm_Wind, 0.65f));

            var weatherRainFire = CreateProfileIfMissing(
                "FP_Weather_RainFire",
                definitions,
                new LayerSpec(AudioEventId.SFX_WTH_Storm_Wind, 0.65f),
                new LayerSpec(AudioEventId.SFX_WTH_Rain_Heavy, 0.80f));

            var weatherSignal = CreateProfileIfMissing(
                "FP_Weather_Signal",
                definitions,
                new LayerSpec(AudioEventId.SFX_WTH_Storm_Wind, 0.80f),
                new LayerSpec(AudioEventId.SFX_WTH_Rain_Heavy, 1.00f));

            var musicCalm = CreateProfileIfMissing(
                "FP_Music_Calm",
                definitions);

            var musicWind = CreateProfileIfMissing(
                "FP_Music_Wind",
                definitions,
                new LayerSpec(AudioEventId.MUS_Storm_Phase1, 0.45f));

            var musicRainFire = CreateProfileIfMissing(
                "FP_Music_RainFire",
                definitions,
                new LayerSpec(AudioEventId.MUS_Storm_Phase2, 0.50f));

            var musicSignal = CreateProfileIfMissing(
                "FP_Music_Signal",
                definitions,
                new LayerSpec(AudioEventId.MUS_Storm_Phase3, 0.55f));

            var runtimePrefab = AssetDatabase.LoadAssetAtPath<GameObject>(RuntimePrefabPath);
            if (runtimePrefab == null)
            {
                runtimePrefab = CreateRuntimePrefab(
                    catalog,
                    beachDay,
                    jungleDay,
                    weatherCalm,
                    weatherWind,
                    weatherRainFire,
                    weatherSignal,
                    musicCalm,
                    musicWind,
                    musicRainFire,
                    musicSignal);
            }
            else
            {
                Debug.Log(
                    $"Project Oen audio: preserving existing runtime prefab '{RuntimePrefabPath}'. " +
                    "Delete it explicitly if you want the generated baseline recreated.",
                    runtimePrefab);
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            if (runtimePrefab != null)
                Selection.activeObject = runtimePrefab;

            AuditOneClick();
            Debug.Log(
                "Project Oen audio one-click build complete. " +
                "Definitions/catalog, generated first-playable profiles and runtime prefab are ready. " +
                "Physical Unity/Quest listening and performance QA is still required.");
        }

        [MenuItem("Project Oen/Audio/Audit First Playable (One Click)")]
        public static void AuditOneClick()
        {
            var catalog = AssetDatabase.LoadAssetAtPath<AudioCatalog>(CatalogPath);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(RuntimePrefabPath);
            var profileGuids = AssetDatabase.IsValidFolder(ProfilesRoot)
                ? AssetDatabase.FindAssets("t:AudioAmbienceProfile", new[] { ProfilesRoot })
                : Array.Empty<string>();
            var coverage = MeasureCanonicalClipCoverage();

            var definitionCount = catalog?.Events.Count ?? 0;
            var profileCount = profileGuids.Length;
            var prefabOk = prefab != null &&
                           prefab.GetComponent<AudioService>() != null &&
                           prefab.GetComponent<AudioWorldStateRouter>() != null &&
                           prefab.GetComponentsInChildren<AudioAmbienceController>(true).Length >= 3;
            var coverageOk = coverage.clipCount >= ExpectedFirstPlayableClipCount &&
                             coverage.eventCount >= ExpectedFirstPlayableEventCount;

            if (!coverageOk)
            {
                Debug.LogError(
                    $"First-playable audit: incomplete canonical clip coverage: " +
                    $"{coverage.clipCount}/{ExpectedFirstPlayableClipCount} clips across " +
                    $"{coverage.eventCount}/{ExpectedFirstPlayableEventCount} events.");
            }
            if (catalog == null)
                Debug.LogError($"First-playable audit: missing catalog '{CatalogPath}'.");
            if (profileCount < 10)
                Debug.LogWarning($"First-playable audit: expected at least 10 generated profiles, found {profileCount}.");
            if (!prefabOk)
                Debug.LogError(
                    "First-playable audit: runtime prefab is missing or lacks AudioService, " +
                    "AudioWorldStateRouter, or the three ambience controllers.");

            Debug.Log(
                $"Project Oen first-playable audit: clipCoverage={(coverageOk ? "OK" : "INCOMPLETE")}, " +
                $"catalog={(catalog != null ? "OK" : "MISSING")}, definitions={definitionCount}, " +
                $"generatedProfiles={profileCount}, runtimePrefab={(prefabOk ? "OK" : "MISSING/INVALID")}.");
        }

        private static (int clipCount, int eventCount) MeasureCanonicalClipCoverage()
        {
            if (!AssetDatabase.IsValidFolder(AudioRoot))
                return (0, 0);

            var clips = 0;
            var events = new HashSet<AudioEventId>();
            foreach (var guid in AssetDatabase.FindAssets("t:AudioClip", new[] { AudioRoot }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
                if (clip == null || !TryResolveCanonicalClipEvent(clip.name, out var id))
                    continue;

                clips++;
                events.Add(id);
            }

            return (clips, events.Count);
        }

        private static bool TryResolveCanonicalClipEvent(string clipName, out AudioEventId id)
        {
            id = AudioEventId.None;

            var names = Enum.GetNames(typeof(AudioEventId))
                .Where(name =>
                    name != nameof(AudioEventId.None) &&
                    name != "SFX_STS_Hunger_Warn" &&
                    name != "SFX_STS_Thirst_Warn")
                .OrderByDescending(name => name.Length);

            foreach (var name in names)
            {
                var prefix = name + "_";
                if (!clipName.StartsWith(prefix, StringComparison.Ordinal))
                    continue;

                var suffix = clipName.Substring(prefix.Length);
                if (!int.TryParse(suffix, out var variation) || variation <= 0)
                    return false;

                if (!Enum.TryParse(name, out id) || id == AudioEventId.None)
                    return false;

                return true;
            }

            return false;
        }

        private static Dictionary<AudioEventId, AudioEventDefinition> FindDefinitions()
        {
            var result = new Dictionary<AudioEventId, AudioEventDefinition>();
            if (!AssetDatabase.IsValidFolder(DefinitionsRoot))
                return result;

            foreach (var guid in AssetDatabase.FindAssets("t:AudioEventDefinition", new[] { DefinitionsRoot }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var definition = AssetDatabase.LoadAssetAtPath<AudioEventDefinition>(path);
                if (definition == null || definition.Id == AudioEventId.None)
                    continue;
                if (!result.ContainsKey(definition.Id))
                    result.Add(definition.Id, definition);
            }

            return result;
        }

        private static AudioAmbienceProfile CreateProfileIfMissing(
            string assetName,
            IReadOnlyDictionary<AudioEventId, AudioEventDefinition> definitions,
            params LayerSpec[] requestedLayers)
        {
            var path = $"{ProfilesRoot}/{assetName}.asset";
            var existing = AssetDatabase.LoadAssetAtPath<AudioAmbienceProfile>(path);
            if (existing != null)
                return existing;

            var profile = ScriptableObject.CreateInstance<AudioAmbienceProfile>();
            AssetDatabase.CreateAsset(profile, path);

            var validLayers = new List<(AudioEventDefinition definition, float gain)>();
            foreach (var layer in requestedLayers)
            {
                if (!definitions.TryGetValue(layer.Id, out var definition) || definition == null)
                {
                    Debug.LogWarning(
                        $"Project Oen audio: generated profile '{assetName}' omits unavailable event '{layer.Id}'.");
                    continue;
                }

                if (!definition.Loop)
                {
                    Debug.LogWarning(
                        $"Project Oen audio: generated profile '{assetName}' omits non-loop event '{layer.Id}'.",
                        definition);
                    continue;
                }

                validLayers.Add((definition, Mathf.Clamp01(layer.Gain)));
            }

            var serialized = new SerializedObject(profile);
            var layers = serialized.FindProperty("_layers");
            layers.arraySize = validLayers.Count;

            for (var index = 0; index < validLayers.Count; index++)
            {
                var element = layers.GetArrayElementAtIndex(index);
                element.FindPropertyRelative("_definition").objectReferenceValue = validLayers[index].definition;
                element.FindPropertyRelative("_gain").floatValue = validLayers[index].gain;
            }

            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static GameObject CreateRuntimePrefab(
            AudioCatalog catalog,
            AudioAmbienceProfile beachDay,
            AudioAmbienceProfile jungleDay,
            AudioAmbienceProfile weatherCalm,
            AudioAmbienceProfile weatherWind,
            AudioAmbienceProfile weatherRainFire,
            AudioAmbienceProfile weatherSignal,
            AudioAmbienceProfile musicCalm,
            AudioAmbienceProfile musicWind,
            AudioAmbienceProfile musicRainFire,
            AudioAmbienceProfile musicSignal)
        {
            var root = new GameObject("AudioRuntime_FirstPlayable");
            try
            {
                var service = root.AddComponent<AudioService>();
                var serviceObject = new SerializedObject(service);
                serviceObject.FindProperty("_catalog").objectReferenceValue = catalog;
                serviceObject.FindProperty("_oneShotPoolSize").intValue = 24;
                serviceObject.ApplyModifiedPropertiesWithoutUndo();

                var biomeObject = CreateChild(root.transform, "BiomeAmbience");
                var weatherObject = CreateChild(root.transform, "WeatherAmbience");
                var musicObject = CreateChild(root.transform, "MusicAmbience");
                CreateChild(root.transform, "WorldFauna");

                var biomeController = biomeObject.AddComponent<AudioAmbienceController>();
                var weatherController = weatherObject.AddComponent<AudioAmbienceController>();
                var musicController = musicObject.AddComponent<AudioAmbienceController>();

                SetInitialProfile(biomeController, beachDay);
                SetInitialProfile(weatherController, weatherCalm);
                SetInitialProfile(musicController, musicCalm);

                var router = root.AddComponent<AudioWorldStateRouter>();
                var routerObject = new SerializedObject(router);
                routerObject.FindProperty("_biomeAmbience").objectReferenceValue = biomeController;
                routerObject.FindProperty("_weatherAmbience").objectReferenceValue = weatherController;
                routerObject.FindProperty("_musicAmbience").objectReferenceValue = musicController;

                ConfigureBiomeBindings(routerObject, beachDay, jungleDay);
                ConfigureStormBindings(
                    routerObject,
                    weatherCalm,
                    weatherWind,
                    weatherRainFire,
                    weatherSignal,
                    musicCalm,
                    musicWind,
                    musicRainFire,
                    musicSignal);

                routerObject.FindProperty("_biome").intValue = (int)AudioBiome.Beach;
                routerObject.FindProperty("_dayPhase").intValue = (int)AudioDayPhase.Day;
                routerObject.FindProperty("_stormPhase").intValue = (int)AudioStormPhase.Calm;
                routerObject.FindProperty("_sheltered").boolValue = false;
                routerObject.ApplyModifiedPropertiesWithoutUndo();

                var prefab = PrefabUtility.SaveAsPrefabAsset(root, RuntimePrefabPath, out var success);
                if (!success || prefab == null)
                {
                    Debug.LogError($"Project Oen audio: failed to save runtime prefab '{RuntimePrefabPath}'.");
                    return null;
                }

                return prefab;
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static void ConfigureBiomeBindings(
            SerializedObject routerObject,
            AudioAmbienceProfile beachDay,
            AudioAmbienceProfile jungleDay)
        {
            var biomes = routerObject.FindProperty("_biomes");
            biomes.arraySize = 2;

            ConfigureBiomeBinding(
                biomes.GetArrayElementAtIndex(0),
                AudioBiome.Beach,
                beachDay,
                null);
            ConfigureBiomeBinding(
                biomes.GetArrayElementAtIndex(1),
                AudioBiome.Jungle,
                jungleDay,
                null);
        }

        private static void ConfigureBiomeBinding(
            SerializedProperty element,
            AudioBiome biome,
            AudioAmbienceProfile day,
            AudioAmbienceProfile night)
        {
            element.FindPropertyRelative("_biome").intValue = (int)biome;
            element.FindPropertyRelative("_day").objectReferenceValue = day;
            element.FindPropertyRelative("_night").objectReferenceValue = night;
        }

        private static void ConfigureStormBindings(
            SerializedObject routerObject,
            AudioAmbienceProfile weatherCalm,
            AudioAmbienceProfile weatherWind,
            AudioAmbienceProfile weatherRainFire,
            AudioAmbienceProfile weatherSignal,
            AudioAmbienceProfile musicCalm,
            AudioAmbienceProfile musicWind,
            AudioAmbienceProfile musicRainFire,
            AudioAmbienceProfile musicSignal)
        {
            var storms = routerObject.FindProperty("_storms");
            storms.arraySize = 4;

            ConfigureStormBinding(
                storms.GetArrayElementAtIndex(0), AudioStormPhase.Calm,
                weatherCalm, musicCalm,
                FindSnapshot("MX_CalmExterior"), FindSnapshot("MX_CalmShelter"));
            ConfigureStormBinding(
                storms.GetArrayElementAtIndex(1), AudioStormPhase.Wind,
                weatherWind, musicWind,
                FindSnapshot("MX_StormWindExterior"), FindSnapshot("MX_StormWindShelter"));
            ConfigureStormBinding(
                storms.GetArrayElementAtIndex(2), AudioStormPhase.RainFire,
                weatherRainFire, musicRainFire,
                FindSnapshot("MX_StormRainExterior"), FindSnapshot("MX_StormRainShelter"));
            ConfigureStormBinding(
                storms.GetArrayElementAtIndex(3), AudioStormPhase.Signal,
                weatherSignal, musicSignal,
                FindSnapshot("MX_StormSignalExterior"), FindSnapshot("MX_StormSignalShelter"));
        }

        private static void ConfigureStormBinding(
            SerializedProperty element,
            AudioStormPhase phase,
            AudioAmbienceProfile weather,
            AudioAmbienceProfile music,
            AudioMixerSnapshot exterior,
            AudioMixerSnapshot sheltered)
        {
            element.FindPropertyRelative("_phase").intValue = (int)phase;
            element.FindPropertyRelative("_weatherProfile").objectReferenceValue = weather;
            element.FindPropertyRelative("_musicProfile").objectReferenceValue = music;
            element.FindPropertyRelative("_exteriorSnapshot").objectReferenceValue = exterior;
            element.FindPropertyRelative("_shelteredSnapshot").objectReferenceValue = sheltered;
        }

        private static AudioMixerSnapshot FindSnapshot(string snapshotName)
        {
            foreach (var guid in AssetDatabase.FindAssets("t:AudioMixer"))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var mixer = AssetDatabase.LoadAssetAtPath<AudioMixer>(path);
                if (mixer == null)
                    continue;

                var snapshot = mixer.FindSnapshot(snapshotName);
                if (snapshot != null)
                    return snapshot;
            }

            return null;
        }

        private static void SetInitialProfile(
            AudioAmbienceController controller,
            AudioAmbienceProfile profile)
        {
            var serialized = new SerializedObject(controller);
            serialized.FindProperty("_initialProfile").objectReferenceValue = profile;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static GameObject CreateChild(Transform parent, string name)
        {
            var child = new GameObject(name);
            child.transform.SetParent(parent, false);
            return child;
        }

        private static void EnsureFolder(string path)
        {
            var parts = path.Split('/');
            var current = parts[0];
            for (var index = 1; index < parts.Length; index++)
            {
                var next = current + "/" + parts[index];
                if (!AssetDatabase.IsValidFolder(next))
                    AssetDatabase.CreateFolder(current, parts[index]);
                current = next;
            }
        }
    }
}
