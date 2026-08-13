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
    /// It verifies the staged manifest before mutation, rebuilds clip definitions/catalog from
    /// that verified payload, synchronizes generated profile membership while preserving gain
    /// tuning for still-valid layers, and creates the runtime prefab only when it does not exist.
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
        private const int ExpectedGeneratedProfileCount = 11;

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

        private readonly struct ProfileSpec
        {
            public ProfileSpec(string name, params LayerSpec[] layers)
            {
                Name = name;
                Layers = layers ?? Array.Empty<LayerSpec>();
            }

            public string Name { get; }
            public LayerSpec[] Layers { get; }
        }

        [MenuItem("Project Oen/Audio/Build First Playable (One Click)", priority = 0)]
        public static void BuildOneClick()
        {
            var manifest = ProjectOenAudioFirstPlayableManifestAudit.Audit();
            if (!manifest.Ok)
            {
                Debug.LogError(
                    "Project Oen audio one-click build stopped: first-playable manifest/import audit failed. " +
                    manifest.Error);
                return;
            }

            var coverage = (clipCount: manifest.ClipCount, eventCount: manifest.EventCount);
            if (coverage.clipCount < ExpectedFirstPlayableClipCount ||
                coverage.eventCount < ExpectedFirstPlayableEventCount)
            {
                Debug.LogError(
                    "Project Oen audio one-click build stopped: incomplete first-playable audio import. " +
                    $"Found {coverage.clipCount}/{ExpectedFirstPlayableClipCount} manifest-verified canonical clips across " +
                    $"{coverage.eventCount}/{ExpectedFirstPlayableEventCount} events below '{AudioRoot}'. " +
                    "Extract the current oen-unity-first-playable-audio-v1 artifact at the Unity project root first.");
                return;
            }

            if (!ProjectOenAudioFirstPlayableBuilder.TryBuildFirstPlayable())
                return;

            var catalog = AssetDatabase.LoadAssetAtPath<AudioCatalog>(CatalogPath);
            if (catalog == null)
            {
                Debug.LogError(
                    $"Project Oen audio one-click build stopped: '{CatalogPath}' was not created. " +
                    "Import/extract the Unity first-playable audio artifact before running this command.");
                return;
            }

            if (catalog.Events.Count != manifest.EventCount)
            {
                Debug.LogError(
                    "Project Oen audio one-click build stopped: catalog/manifest event-count mismatch after rebuild. " +
                    $"Catalog={catalog.Events.Count}, manifest={manifest.EventCount}.");
                return;
            }

            EnsureFolder(ProfilesRoot);
            EnsureFolder(RuntimeRoot);

            var definitions = FindDefinitions();
            var profiles = SyncGeneratedProfiles(definitions);

            var biomeSilence = profiles["FP_Biome_Silence"];
            var beachDay = profiles["FP_Biome_Beach_Day"];
            var jungleDay = profiles["FP_Biome_Jungle_Day"];
            var weatherCalm = profiles["FP_Weather_Calm"];
            var weatherWind = profiles["FP_Weather_Wind"];
            var weatherRainFire = profiles["FP_Weather_RainFire"];
            var weatherSignal = profiles["FP_Weather_Signal"];
            var musicCalm = profiles["FP_Music_Calm"];
            var musicWind = profiles["FP_Music_Wind"];
            var musicRainFire = profiles["FP_Music_RainFire"];
            var musicSignal = profiles["FP_Music_Signal"];

            var runtimePrefab = AssetDatabase.LoadAssetAtPath<GameObject>(RuntimePrefabPath);
            if (runtimePrefab == null)
            {
                runtimePrefab = CreateRuntimePrefab(
                    catalog,
                    biomeSilence,
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
                    "Generated profile membership has been synchronized; delete the prefab explicitly only if you want its baseline composition recreated.",
                    runtimePrefab);
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            if (runtimePrefab != null)
                Selection.activeObject = runtimePrefab;

            AuditOneClick();
            Debug.Log(
                "Project Oen audio one-click build complete. " +
                "Manifest/import integrity, definitions/catalog, synchronized generated profiles and runtime prefab are ready. " +
                "Physical Unity/Quest listening and performance QA is still required.");
        }

        [MenuItem("Project Oen/Audio/Audit First Playable (One Click)")]
        public static void AuditOneClick()
        {
            var manifest = ProjectOenAudioFirstPlayableManifestAudit.Audit();
            var catalog = AssetDatabase.LoadAssetAtPath<AudioCatalog>(CatalogPath);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(RuntimePrefabPath);
            var profileGuids = AssetDatabase.IsValidFolder(ProfilesRoot)
                ? AssetDatabase.FindAssets("t:AudioAmbienceProfile", new[] { ProfilesRoot })
                : Array.Empty<string>();
            var coverage = manifest.Ok
                ? (clipCount: manifest.ClipCount, eventCount: manifest.EventCount)
                : (clipCount: 0, eventCount: 0);

            var definitionCount = catalog?.Events.Count ?? 0;
            var catalogOk = manifest.Ok && catalog != null && definitionCount == manifest.EventCount;
            var profileCount = profileGuids.Length;
            var profilesOk = catalogOk && AuditGeneratedProfiles(FindDefinitions());
            var prefabOk = prefab != null &&
                           prefab.GetComponent<AudioService>() != null &&
                           prefab.GetComponent<AudioWorldStateRouter>() != null &&
                           prefab.GetComponentsInChildren<AudioAmbienceController>(true).Length >= 3;
            var coverageOk = manifest.Ok &&
                             coverage.clipCount >= ExpectedFirstPlayableClipCount &&
                             coverage.eventCount >= ExpectedFirstPlayableEventCount;

            if (!manifest.Ok)
                Debug.LogError("First-playable audit: manifest/import integrity failed: " + manifest.Error);
            if (!coverageOk)
            {
                Debug.LogError(
                    $"First-playable audit: incomplete manifest-verified canonical clip coverage: " +
                    $"{coverage.clipCount}/{ExpectedFirstPlayableClipCount} clips across " +
                    $"{coverage.eventCount}/{ExpectedFirstPlayableEventCount} events.");
            }
            if (!catalogOk)
            {
                Debug.LogError(
                    $"First-playable audit: catalog mismatch; catalog definitions={definitionCount}, " +
                    $"manifest events={(manifest.Ok ? manifest.EventCount : 0)}.");
            }
            if (profileCount < ExpectedGeneratedProfileCount)
            {
                Debug.LogError(
                    $"First-playable audit: expected at least {ExpectedGeneratedProfileCount} generated profiles, " +
                    $"found {profileCount}.");
            }
            if (!prefabOk)
            {
                Debug.LogError(
                    "First-playable audit: runtime prefab is missing or lacks AudioService, " +
                    "AudioWorldStateRouter, or the three ambience controllers.");
            }

            Debug.Log(
                $"Project Oen first-playable audit: manifest={(manifest.Ok ? "OK" : "FAILED")}, " +
                $"clipCoverage={(coverageOk ? "OK" : "INCOMPLETE")}, catalog={(catalogOk ? "OK" : "MISMATCH")}, " +
                $"definitions={definitionCount}, generatedProfiles={profileCount}/{(profilesOk ? "SYNCED" : "CHECK")}, " +
                $"runtimePrefab={(prefabOk ? "OK" : "MISSING/INVALID")}.");
        }

        private static (int clipCount, int eventCount) MeasureCanonicalClipCoverage()
        {
            var manifest = ProjectOenAudioFirstPlayableManifestAudit.Audit();
            return manifest.Ok
                ? (manifest.ClipCount, manifest.EventCount)
                : (0, 0);
        }

        private static Dictionary<AudioEventId, AudioEventDefinition> FindDefinitions()
        {
            var result = new Dictionary<AudioEventId, AudioEventDefinition>();
            var seen = new Dictionary<AudioEventId, string>();
            if (!AssetDatabase.IsValidFolder(DefinitionsRoot))
                return result;

            foreach (var guid in AssetDatabase.FindAssets("t:AudioEventDefinition", new[] { DefinitionsRoot }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var definition = AssetDatabase.LoadAssetAtPath<AudioEventDefinition>(path);
                if (definition == null || definition.Id == AudioEventId.None)
                    continue;

                if (seen.TryGetValue(definition.Id, out var existingPath))
                {
                    throw new InvalidOperationException(
                        $"duplicate AudioEventDefinition for '{definition.Id}': '{existingPath}' and '{path}'.");
                }
                seen.Add(definition.Id, path);

                // Stale definitions are deliberately left as tuning/history assets by the catalog
                // builder, but their clip arrays are cleared and they must not enter generated profiles.
                if (definition.ClipCount > 0)
                    result.Add(definition.Id, definition);
            }

            return result;
        }

        private static ProfileSpec[] GeneratedProfileSpecs()
        {
            return new[]
            {
                new ProfileSpec("FP_Biome_Silence"),
                new ProfileSpec(
                    "FP_Biome_Beach_Day",
                    new LayerSpec(AudioEventId.SFX_AMB_Beach_OceanNear, 1.00f)),
                new ProfileSpec(
                    "FP_Biome_Jungle_Day",
                    new LayerSpec(AudioEventId.SFX_AMB_Jungle_DayBed, 0.90f)),
                new ProfileSpec("FP_Weather_Calm"),
                new ProfileSpec(
                    "FP_Weather_Wind",
                    new LayerSpec(AudioEventId.SFX_WTH_Storm_Wind, 0.65f)),
                new ProfileSpec(
                    "FP_Weather_RainFire",
                    new LayerSpec(AudioEventId.SFX_WTH_Storm_Wind, 0.65f),
                    new LayerSpec(AudioEventId.SFX_WTH_Rain_Heavy, 0.80f)),
                new ProfileSpec(
                    "FP_Weather_Signal",
                    new LayerSpec(AudioEventId.SFX_WTH_Storm_Wind, 0.80f),
                    new LayerSpec(AudioEventId.SFX_WTH_Rain_Heavy, 1.00f)),
                new ProfileSpec("FP_Music_Calm"),
                new ProfileSpec(
                    "FP_Music_Wind",
                    new LayerSpec(AudioEventId.MUS_Storm_Phase1, 0.45f)),
                new ProfileSpec(
                    "FP_Music_RainFire",
                    new LayerSpec(AudioEventId.MUS_Storm_Phase2, 0.50f)),
                new ProfileSpec(
                    "FP_Music_Signal",
                    new LayerSpec(AudioEventId.MUS_Storm_Phase3, 0.55f)),
            };
        }

        private static Dictionary<string, AudioAmbienceProfile> SyncGeneratedProfiles(
            IReadOnlyDictionary<AudioEventId, AudioEventDefinition> definitions)
        {
            var result = new Dictionary<string, AudioAmbienceProfile>(StringComparer.Ordinal);
            foreach (var spec in GeneratedProfileSpecs())
                result.Add(spec.Name, SyncGeneratedProfile(spec, definitions));
            return result;
        }

        private static AudioAmbienceProfile SyncGeneratedProfile(
            ProfileSpec spec,
            IReadOnlyDictionary<AudioEventId, AudioEventDefinition> definitions)
        {
            var path = $"{ProfilesRoot}/{spec.Name}.asset";
            var profile = AssetDatabase.LoadAssetAtPath<AudioAmbienceProfile>(path);
            var created = false;
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<AudioAmbienceProfile>();
                AssetDatabase.CreateAsset(profile, path);
                created = true;
            }

            var preservedGain = new Dictionary<AudioEventId, float>();
            var existingLayers = profile.Layers;
            if (existingLayers != null)
            {
                for (var index = 0; index < existingLayers.Count; index++)
                {
                    var layer = existingLayers[index];
                    var definition = layer?.Definition;
                    if (definition == null || preservedGain.ContainsKey(definition.Id))
                        continue;
                    preservedGain.Add(definition.Id, Mathf.Clamp01(layer.Gain));
                }
            }

            var validLayers = new List<(AudioEventDefinition definition, float gain)>();
            foreach (var layer in spec.Layers)
            {
                if (!definitions.TryGetValue(layer.Id, out var definition) || definition == null)
                {
                    Debug.LogWarning(
                        $"Project Oen audio: generated profile '{spec.Name}' omits unavailable event '{layer.Id}'.");
                    continue;
                }

                if (!definition.Loop)
                {
                    Debug.LogWarning(
                        $"Project Oen audio: generated profile '{spec.Name}' omits non-loop event '{layer.Id}'.",
                        definition);
                    continue;
                }

                var gain = preservedGain.TryGetValue(layer.Id, out var tunedGain)
                    ? tunedGain
                    : Mathf.Clamp01(layer.Gain);
                validLayers.Add((definition, gain));
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
            Debug.Log(
                $"Project Oen audio: {(created ? "created" : "synchronized")} generated profile '{spec.Name}' " +
                $"with {validLayers.Count} active layer(s).",
                profile);
            return profile;
        }

        private static bool AuditGeneratedProfiles(
            IReadOnlyDictionary<AudioEventId, AudioEventDefinition> definitions)
        {
            var ok = true;
            foreach (var spec in GeneratedProfileSpecs())
            {
                var path = $"{ProfilesRoot}/{spec.Name}.asset";
                var profile = AssetDatabase.LoadAssetAtPath<AudioAmbienceProfile>(path);
                if (profile == null)
                {
                    Debug.LogError($"First-playable audit: missing generated profile '{path}'.");
                    ok = false;
                    continue;
                }

                var expected = spec.Layers
                    .Where(layer =>
                        definitions.TryGetValue(layer.Id, out var definition) &&
                        definition != null &&
                        definition.Loop)
                    .Select(layer => layer.Id)
                    .ToArray();
                var actual = profile.Layers
                    .Where(layer => layer?.Definition != null)
                    .Select(layer => layer.Definition.Id)
                    .ToArray();

                if (!actual.SequenceEqual(expected))
                {
                    Debug.LogError(
                        $"First-playable audit: generated profile '{spec.Name}' layer membership drift. " +
                        $"Expected [{string.Join(", ", expected)}], got [{string.Join(", ", actual)}].",
                        profile);
                    ok = false;
                }
            }

            return ok;
        }

        private static GameObject CreateRuntimePrefab(
            AudioCatalog catalog,
            AudioAmbienceProfile biomeSilence,
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
                routerObject.FindProperty("_shelterDay").objectReferenceValue = biomeSilence;
                routerObject.FindProperty("_shelterNight").objectReferenceValue = biomeSilence;

                ConfigureBiomeBindings(routerObject, biomeSilence, beachDay, jungleDay);
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
            AudioAmbienceProfile biomeSilence,
            AudioAmbienceProfile beachDay,
            AudioAmbienceProfile jungleDay)
        {
            var biomes = routerObject.FindProperty("_biomes");
            biomes.arraySize = 4;

            ConfigureBiomeBinding(
                biomes.GetArrayElementAtIndex(0),
                AudioBiome.Beach,
                beachDay,
                biomeSilence);
            ConfigureBiomeBinding(
                biomes.GetArrayElementAtIndex(1),
                AudioBiome.Jungle,
                jungleDay,
                biomeSilence);
            ConfigureBiomeBinding(
                biomes.GetArrayElementAtIndex(2),
                AudioBiome.Ridge,
                biomeSilence,
                biomeSilence);
            ConfigureBiomeBinding(
                biomes.GetArrayElementAtIndex(3),
                AudioBiome.Camp,
                biomeSilence,
                biomeSilence);
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
