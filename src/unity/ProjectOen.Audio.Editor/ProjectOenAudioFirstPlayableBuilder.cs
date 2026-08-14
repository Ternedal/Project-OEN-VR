using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Audio;

namespace ProjectOen.Audio.Editor
{
    /// <summary>
    /// Converts the manifest-verified Project OEN first-playable WAV payload into
    /// AudioEventDefinition assets and a catalog. Existing designer tuning is preserved for
    /// active definitions, while definitions no longer present in the current staged manifest
    /// are cleared so stale clips can never remain reachable through generated profiles.
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
            TryBuildFirstPlayable();
        }

        internal static bool TryBuildFirstPlayable()
        {
            try
            {
                BuildFirstPlayableInternal();
                return true;
            }
            catch (Exception exception)
            {
                Debug.LogError(
                    "Project Oen audio first-playable build stopped before catalog completion: " +
                    exception.Message);
                return false;
            }
        }

        private static void BuildFirstPlayableInternal()
        {
            EnsureFolder(DefinitionsRoot);

            var bindings = FindBindings();
            if (bindings.Count == 0)
            {
                throw new InvalidOperationException(
                    $"no manifest-verified canonical audio clips found below '{AudioRoot}'. " +
                    "Extract the current oen-unity-first-playable-audio-v1 artifact at the Unity project root first.");
            }

            var existing = FindExistingDefinitions();
            var importedIds = new HashSet<AudioEventId>(bindings.Select(binding => binding.Id));
            var staleCleared = ClearStaleDefinitionClips(existing, importedIds);
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
                serialized.FindProperty("_id").intValue = (int)group.Key;

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

            // The current staged manifest is authoritative. Old definition assets may remain on disk
            // to preserve tuning/history, but they cannot remain in the runtime catalog.
            var orderedDefinitions = importedIds
                .OrderBy(id => (ushort)id)
                .Select(id => existing[id])
                .Where(definition => definition != null && HasClips(definition))
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
                $"Project Oen audio first-playable build complete: {bindings.Count} manifest-verified clips, " +
                $"{orderedDefinitions.Length}/{runtimeCount} runtime events populated, " +
                $"{created} definitions created, {updated} updated, {staleCleared} stale definitions cleared. " +
                $"Catalog: {CatalogPath}",
                catalog);
        }

        [MenuItem("Project Oen/Audio/Audit First-Playable Clip Coverage")]
        public static void AuditCoverage()
        {
            var manifest = ProjectOenAudioFirstPlayableManifestAudit.Audit();
            if (!manifest.Ok)
            {
                Debug.LogError("Project Oen audio coverage audit failed: " + manifest.Error);
                return;
            }

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
                $"Project Oen audio coverage: {bindings.Count} manifest-verified clips across " +
                $"{populated}/{ids.Length} runtime events. Missing events remain production work; " +
                "stale/unmanaged canonical WAVs are rejected rather than silently entering the catalog.");
        }

        private static List<ClipBinding> FindBindings()
        {
            var entries = ProjectOenAudioFirstPlayableManifestAudit.RequireVerifiedEntries();
            var result = new List<ClipBinding>(entries.Count);

            foreach (var entry in entries)
            {
                var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(entry.UnityPath);
                if (clip == null)
                {
                    throw new InvalidOperationException(
                        $"manifested WAV has not imported as AudioClip: '{entry.UnityPath}'.");
                }

                result.Add(new ClipBinding
                {
                    Id = entry.EventId,
                    Variation = entry.Variation,
                    Clip = clip,
                    AssetPath = entry.UnityPath,
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

                if (result.TryGetValue(definition.Id, out var duplicate))
                {
                    var duplicatePath = AssetDatabase.GetAssetPath(duplicate);
                    throw new InvalidOperationException(
                        $"duplicate existing definition for '{definition.Id}': '{duplicatePath}' and '{path}'. " +
                        "Resolve the duplicate before rebuilding the catalog.");
                }

                result.Add(definition.Id, definition);
            }

            return result;
        }

        private static int ClearStaleDefinitionClips(
            IReadOnlyDictionary<AudioEventId, AudioEventDefinition> existing,
            ISet<AudioEventId> importedIds)
        {
            var cleared = 0;
            foreach (var pair in existing)
            {
                if (importedIds.Contains(pair.Key) || pair.Value == null)
                    continue;

                var serialized = new SerializedObject(pair.Value);
                var clips = serialized.FindProperty("_clips");
                if (clips == null || clips.arraySize == 0)
                    continue;

                clips.arraySize = 0;
                serialized.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(pair.Value);
                cleared++;
                Debug.LogWarning(
                    $"Project Oen audio: cleared stale clips from definition '{pair.Key}' because it is not present in the current first-playable manifest.",
                    pair.Value);
            }

            return cleared;
        }

        private static string CanonicalName(AudioEventId id)
        {
            if (id == AudioEventId.SFX_STS_Injury_Warn)
                return nameof(AudioEventId.SFX_STS_Injury_Warn);
            if (id == AudioEventId.SFX_STS_ColdWet_Warn)
                return nameof(AudioEventId.SFX_STS_ColdWet_Warn);
            return Enum.GetName(typeof(AudioEventId), id) ?? id.ToString();
        }

        private static void ApplyCreationDefaults(
            AudioEventDefinition definition,
            AudioEventId id,
            string sampleAssetPath)
        {
            var serialized = new SerializedObject(definition);
            serialized.FindProperty("_id").intValue = (int)id;
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
