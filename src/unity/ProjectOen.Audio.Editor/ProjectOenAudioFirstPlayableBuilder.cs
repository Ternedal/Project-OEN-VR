using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Audio;

namespace ProjectOen.Audio.Editor
{
    /// <summary>
    /// Converts imported Project OEN WAV variations into AudioEventDefinition assets and a catalog.
    /// Existing designer tuning is preserved; only ID/clip membership and missing mixer routing are refreshed.
    /// </summary>
    public static class ProjectOenAudioFirstPlayableBuilder
    {
        private const string AudioRoot = "Assets/ProjectOen/Audio";
        private const string DefinitionsRoot = AudioRoot + "/Definitions";
        private const string CatalogPath = DefinitionsRoot + "/AudioCatalog.asset";

        private sealed class ClipBinding
        {
            public AudioEventId Id;
            public int Variation;
            public AudioClip Clip;
            public string AssetPath;
        }

        [MenuItem("Project Oen/Audio/Build First-Playable Definitions + Catalog")]
        public static void BuildFirstPlayable()
        {
            EnsureFolder(DefinitionsRoot);

            var bindings = FindBindings();
            if (bindings.Count == 0)
            {
                Debug.LogError(
                    $"Project Oen audio: no canonical audio clips found below '{AudioRoot}'. " +
                    "Import/extract the first-playable audio pack into the Unity project first.");
                return;
            }

            var existing = FindExistingDefinitions();
            var created = 0;
            var updated = 0;

            foreach (var group in bindings.GroupBy(x => x.Id).OrderBy(x => (ushort)x.Key))
            {
                var clips = group
                    .OrderBy(x => x.Variation)
                    .ThenBy(x => x.AssetPath, StringComparer.Ordinal)
                    .Select(x => x.Clip)
                    .ToArray();

                if (!existing.TryGetValue(group.Key, out var definition) || definition == null)
                {
                    definition = ScriptableObject.CreateInstance<AudioEventDefinition>();
                    var path = $"{DefinitionsRoot}/{CanonicalName(group.Key)}.asset";
                    AssetDatabase.CreateAsset(definition, path);
                    existing[group.Key] = definition;
                    ApplyCreationDefaults(definition, group.Key, group.First().AssetPath);
                    created++;
                }
                else
                {
                    updated++;
                }

                var serialized = new SerializedObject(definition);
                serialized.FindProperty("_id").enumValueIndex = EnumIndex(group.Key);

                var clipsProperty = serialized.FindProperty("_clips");
                clipsProperty.arraySize = clips.Length;
                for (var index = 0; index < clips.Length; index++)
                    clipsProperty.GetArrayElementAtIndex(index).objectReferenceValue = clips[index];

                var output = serialized.FindProperty("_output");
                if (output != null && output.objectReferenceValue == null)
                {
                    var mixerGroup = FindMixerGroup(RouteGroup(group.Key));
                    if (mixerGroup != null)
                        output.objectReferenceValue = mixerGroup;
                }

                serialized.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(definition);
            }

            var catalog = AssetDatabase.LoadAssetAtPath<AudioCatalog>(CatalogPath);
            if (catalog == null)
            {
                catalog = ScriptableObject.CreateInstance<AudioCatalog>();
                AssetDatabase.CreateAsset(catalog, CatalogPath);
            }

            var orderedDefinitions = existing
                .Where(x => x.Key != AudioEventId.None && x.Value != null && HasClips(x.Value))
                .OrderBy(x => (ushort)x.Key)
                .Select(x => x.Value)
                .ToArray();

            var catalogObject = new SerializedObject(catalog);
            var eventsProperty = catalogObject.FindProperty("_events");
            eventsProperty.arraySize = orderedDefinitions.Length;
            for (var index = 0; index < orderedDefinitions.Length; index++)
                eventsProperty.GetArrayElementAtIndex(index).objectReferenceValue = orderedDefinitions[index];
            catalogObject.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(catalog);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Selection.activeObject = catalog;

            var runtimeCount = Enum.GetValues(typeof(AudioEventId))
                .Cast<AudioEventId>()
                .Where(x => x != AudioEventId.None)
                .Distinct()
                .Count();

            Debug.Log(
                $"Project Oen audio first-playable build complete: {bindings.Count} clips, " +
                $"{orderedDefinitions.Length}/{runtimeCount} runtime events populated, " +
                $"{created} definitions created, {updated} updated. Catalog: {CatalogPath}",
                catalog);
        }

        [MenuItem("Project Oen/Audio/Audit First-Playable Clip Coverage")]
        public static void AuditCoverage()
        {
            var bindings = FindBindings();
            var byId = bindings.GroupBy(x => x.Id).ToDictionary(x => x.Key, x => x.Count());
            var ids = Enum.GetValues(typeof(AudioEventId))
                .Cast<AudioEventId>()
                .Where(x => x != AudioEventId.None)
                .Distinct()
                .OrderBy(x => (ushort)x)
                .ToArray();

            var populated = 0;
            foreach (var id in ids)
            {
                if (byId.TryGetValue(id, out var count))
                {
                    populated++;
                    Debug.Log($"Audio coverage: {CanonicalName(id)} = {count} imported variation(s)");
                }
            }

            Debug.Log(
                $"Project Oen audio coverage: {bindings.Count} clips across {populated}/{ids.Length} runtime events. " +
                "Missing events remain production work; they are not synthesized or silently aliased.");
        }

        private static List<ClipBinding> FindBindings()
        {
            if (!AssetDatabase.IsValidFolder(AudioRoot))
                return new List<ClipBinding>();

            var result = new List<ClipBinding>();
            foreach (var guid in AssetDatabase.FindAssets("t:AudioClip", new[] { AudioRoot }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
                if (clip == null)
                    continue;

                if (!TryParseCanonicalClipName(clip.name, out var id, out var variation))
                {
                    Debug.LogWarning(
                        $"Project Oen audio: ignoring clip with non-canonical name '{clip.name}' at '{path}'.",
                        clip);
                    continue;
                }

                result.Add(new ClipBinding
                {
                    Id = id,
                    Variation = variation,
                    Clip = clip,
                    AssetPath = path,
                });
            }

            return result;
        }

        private static Dictionary<AudioEventId, AudioEventDefinition> FindExistingDefinitions()
        {
            var result = new Dictionary<AudioEventId, AudioEventDefinition>();
            foreach (var guid in AssetDatabase.FindAssets("t:AudioEventDefinition", new[] { DefinitionsRoot }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var definition = AssetDatabase.LoadAssetAtPath<AudioEventDefinition>(path);
                if (definition == null || definition.Id == AudioEventId.None)
                    continue;

                if (result.ContainsKey(definition.Id))
                {
                    Debug.LogError(
                        $"Project Oen audio: duplicate existing definition for '{definition.Id}' at '{path}'.",
                        definition);
                    continue;
                }

                result.Add(definition.Id, definition);
            }

            return result;
        }

        private static bool TryParseCanonicalClipName(
            string clipName,
            out AudioEventId id,
            out int variation)
        {
            id = AudioEventId.None;
            variation = 0;

            foreach (var name in CanonicalNames())
            {
                var prefix = name + "_";
                if (!clipName.StartsWith(prefix, StringComparison.Ordinal))
                    continue;

                var suffix = clipName.Substring(prefix.Length);
                if (!int.TryParse(suffix, out variation) || variation <= 0)
                    return false;

                if (!Enum.TryParse(name, out id) || id == AudioEventId.None)
                    return false;

                return true;
            }

            return false;
        }

        private static IEnumerable<string> CanonicalNames()
        {
            return Enum.GetNames(typeof(AudioEventId))
                .Where(name =>
                    name != nameof(AudioEventId.None) &&
                    name != "SFX_STS_Hunger_Warn" &&
                    name != "SFX_STS_Thirst_Warn")
                .OrderByDescending(name => name.Length);
        }

        private static string CanonicalName(AudioEventId id)
        {
            if (id == AudioEventId.SFX_STS_Injury_Warn)
                return nameof(AudioEventId.SFX_STS_Injury_Warn);
            if (id == AudioEventId.SFX_STS_ColdWet_Warn)
                return nameof(AudioEventId.SFX_STS_ColdWet_Warn);
            return Enum.GetName(typeof(AudioEventId), id) ?? id.ToString();
        }

        private static int EnumIndex(AudioEventId id)
        {
            var names = Enum.GetNames(typeof(AudioEventId));
            var canonical = CanonicalName(id);
            var index = Array.IndexOf(names, canonical);
            return Mathf.Max(0, index);
        }

        private static void ApplyCreationDefaults(
            AudioEventDefinition definition,
            AudioEventId id,
            string sampleAssetPath)
        {
            var serialized = new SerializedObject(definition);
            serialized.FindProperty("_id").enumValueIndex = EnumIndex(id);
            serialized.FindProperty("_loop").boolValue = IsLoopEvent(id);

            var spatialBlend = InferSpatialBlend(id, sampleAssetPath);
            serialized.FindProperty("_spatialBlend").floatValue = spatialBlend;
            serialized.FindProperty("_volumeMin").floatValue = 0.90f;
            serialized.FindProperty("_volumeMax").floatValue = 1.00f;

            var fixedPitch = CanonicalName(id).StartsWith("MUS_", StringComparison.Ordinal) ||
                             CanonicalName(id).StartsWith("STG_", StringComparison.Ordinal);
            serialized.FindProperty("_pitchMin").floatValue = fixedPitch ? 1.00f : 0.96f;
            serialized.FindProperty("_pitchMax").floatValue = fixedPitch ? 1.00f : 1.04f;
            serialized.FindProperty("_priority").intValue = DefaultPriority(id);
            serialized.FindProperty("_minDistance").floatValue = spatialBlend > 0f ? 0.75f : 1f;
            serialized.FindProperty("_maxDistance").floatValue = spatialBlend > 0f ? 15f : 1f;

            var mixerGroup = FindMixerGroup(RouteGroup(id));
            if (mixerGroup != null)
                serialized.FindProperty("_output").objectReferenceValue = mixerGroup;

            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(definition);
        }

        private static float InferSpatialBlend(AudioEventId id, string assetPath)
        {
            if (assetPath.IndexOf("/2D/", StringComparison.OrdinalIgnoreCase) >= 0)
                return 0f;
            if (assetPath.IndexOf("/Spatial/", StringComparison.OrdinalIgnoreCase) >= 0)
                return 1f;

            var name = CanonicalName(id);
            if (name.StartsWith("MUS_", StringComparison.Ordinal) ||
                name.StartsWith("STG_", StringComparison.Ordinal) ||
                name.StartsWith("SFX_UI_", StringComparison.Ordinal) ||
                name.StartsWith("SFX_STS_", StringComparison.Ordinal))
                return 0f;

            return 1f;
        }

        private static bool IsLoopEvent(AudioEventId id)
        {
            var name = CanonicalName(id);
            if (name.StartsWith("MUS_", StringComparison.Ordinal))
                return id != AudioEventId.MUS_Finale_Success;

            if (name.StartsWith("SFX_AMB_", StringComparison.Ordinal))
                return id != AudioEventId.SFX_AMB_Shore_Wash;

            return id == AudioEventId.SFX_WTH_Rain_Light ||
                   id == AudioEventId.SFX_WTH_Rain_Heavy ||
                   id == AudioEventId.SFX_WTH_Rain_OnTarp ||
                   id == AudioEventId.SFX_WTH_Storm_Wind ||
                   id == AudioEventId.SFX_WTH_Storm_RoughOcean ||
                   id == AudioEventId.SFX_ENV_Fire_Idle ||
                   id == AudioEventId.SFX_ENV_Fire_Low;
        }

        private static int DefaultPriority(AudioEventId id)
        {
            var name = CanonicalName(id);
            if (name.StartsWith("MUS_", StringComparison.Ordinal) ||
                name.StartsWith("STG_", StringComparison.Ordinal))
                return 40;
            if (name.StartsWith("SFX_STS_", StringComparison.Ordinal))
                return 55;
            if (name.StartsWith("SFX_UI_", StringComparison.Ordinal))
                return 60;
            if (name.StartsWith("SFX_INT_", StringComparison.Ordinal) ||
                name.StartsWith("SFX_CRF_", StringComparison.Ordinal))
                return 70;
            if (name.StartsWith("SFX_PLY_", StringComparison.Ordinal))
                return 75;
            return 80;
        }

        private static string RouteGroup(AudioEventId id)
        {
            var name = CanonicalName(id);
            if (name.StartsWith("SFX_AMB_", StringComparison.Ordinal)) return "Ambience";
            if (name.StartsWith("SFX_WTH_", StringComparison.Ordinal)) return "Weather";
            if (name.StartsWith("SFX_NAT_", StringComparison.Ordinal)) return "Nature";
            if (name.StartsWith("SFX_ENV_", StringComparison.Ordinal)) return "Environment";
            if (name.StartsWith("SFX_PLY_", StringComparison.Ordinal)) return "Player";
            if (name.StartsWith("SFX_INT_", StringComparison.Ordinal) ||
                name.StartsWith("SFX_STS_", StringComparison.Ordinal)) return "Interaction";
            if (name.StartsWith("SFX_CRF_", StringComparison.Ordinal)) return "Crafting";
            if (name.StartsWith("SFX_UI_", StringComparison.Ordinal)) return "UI";
            if (name.StartsWith("MUS_", StringComparison.Ordinal)) return "Music";
            if (name.StartsWith("STG_", StringComparison.Ordinal)) return "Stinger";
            return string.Empty;
        }

        private static AudioMixerGroup FindMixerGroup(string groupName)
        {
            if (string.IsNullOrWhiteSpace(groupName))
                return null;

            foreach (var guid in AssetDatabase.FindAssets("t:AudioMixer"))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var mixer = AssetDatabase.LoadAssetAtPath<AudioMixer>(path);
                if (mixer == null)
                    continue;

                var exact = mixer.FindMatchingGroups(groupName)
                    .FirstOrDefault(group => string.Equals(group.name, groupName, StringComparison.Ordinal));
                if (exact != null)
                    return exact;
            }

            return null;
        }

        private static bool HasClips(AudioEventDefinition definition)
        {
            var serialized = new SerializedObject(definition);
            var clips = serialized.FindProperty("_clips");
            return clips != null && clips.arraySize > 0;
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
