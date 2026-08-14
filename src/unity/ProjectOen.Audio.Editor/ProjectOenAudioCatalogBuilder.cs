using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Audio.Editor
{
    public static class ProjectOenAudioCatalogBuilder
    {
        [MenuItem("Project Oen/Audio/Rebuild Selected Audio Catalog")]
        public static void RebuildSelectedCatalog()
        {
            if (Selection.activeObject is not AudioCatalog catalog)
            {
                Debug.LogError("Select an AudioCatalog asset before rebuilding it.");
                return;
            }

            var definitions = FindDefinitions();
            if (!ValidateDefinitions(definitions, true))
                return;

            var ordered = definitions
                .Where(x => x != null && x.Id != AudioEventId.None)
                .OrderBy(x => (ushort)x.Id)
                .ToArray();

            var serialized = new SerializedObject(catalog);
            var eventsProperty = serialized.FindProperty("_events");
            eventsProperty.arraySize = ordered.Length;

            for (var i = 0; i < ordered.Length; i++)
                eventsProperty.GetArrayElementAtIndex(i).objectReferenceValue = ordered[i];

            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(catalog);
            AssetDatabase.SaveAssets();

            Debug.Log(
                $"Project Oen audio: rebuilt catalog '{catalog.name}' with {ordered.Length} definitions.",
                catalog);
        }

        [MenuItem("Project Oen/Audio/Rebuild Selected Audio Catalog", true)]
        private static bool CanRebuildSelectedCatalog()
            => Selection.activeObject is AudioCatalog;

        [MenuItem("Project Oen/Audio/Audit Audio Event Definitions")]
        public static void AuditDefinitions()
        {
            var definitions = FindDefinitions();
            var valid = ValidateDefinitions(definitions, false);

            var present = new HashSet<AudioEventId>(
                definitions
                    .Where(x => x != null && x.Id != AudioEventId.None)
                    .Select(x => x.Id));

            var allRuntimeIds = Enum.GetValues(typeof(AudioEventId))
                .Cast<AudioEventId>()
                .Where(x => x != AudioEventId.None)
                .Distinct()
                .ToArray();

            var missing = allRuntimeIds.Count(x => !present.Contains(x));
            Debug.Log(
                $"Project Oen audio definition audit: {(valid ? "OK" : "ERRORS")}; " +
                $"{present.Count} unique definitions present, {missing} runtime IDs not yet populated.");
        }

        private static AudioEventDefinition[] FindDefinitions()
        {
            return AssetDatabase.FindAssets("t:AudioEventDefinition")
                .Select(AssetDatabase.GUIDToAssetPath)
                .Select(AssetDatabase.LoadAssetAtPath<AudioEventDefinition>)
                .Where(x => x != null)
                .ToArray();
        }

        private static bool ValidateDefinitions(
            IReadOnlyList<AudioEventDefinition> definitions,
            bool requireClips)
        {
            var valid = true;
            var ids = new Dictionary<AudioEventId, AudioEventDefinition>();

            for (var i = 0; i < definitions.Count; i++)
            {
                var definition = definitions[i];
                if (definition == null)
                    continue;

                if (definition.Id == AudioEventId.None)
                {
                    Debug.LogError(
                        $"Audio definition '{definition.name}' has AudioEventId.None.",
                        definition);
                    valid = false;
                    continue;
                }

                if (ids.TryGetValue(definition.Id, out var previous))
                {
                    Debug.LogError(
                        $"Duplicate audio definition ID '{definition.Id}': " +
                        $"'{previous.name}' and '{definition.name}'.",
                        definition);
                    valid = false;
                    continue;
                }

                ids.Add(definition.Id, definition);

                var serialized = new SerializedObject(definition);
                var clips = serialized.FindProperty("_clips");
                if (requireClips && (clips == null || clips.arraySize == 0))
                {
                    Debug.LogError(
                        $"Audio definition '{definition.name}' has no clips.",
                        definition);
                    valid = false;
                    continue;
                }

                if (clips == null)
                    continue;

                var expectedPrefix = definition.Id + "_";
                var referenced = new HashSet<AudioClip>();
                for (var clipIndex = 0; clipIndex < clips.arraySize; clipIndex++)
                {
                    var clip = clips.GetArrayElementAtIndex(clipIndex).objectReferenceValue as AudioClip;
                    if (clip == null)
                    {
                        Debug.LogError(
                            $"Audio definition '{definition.name}' contains a null clip at index {clipIndex}.",
                            definition);
                        valid = false;
                        continue;
                    }

                    if (!referenced.Add(clip))
                    {
                        Debug.LogError(
                            $"Audio definition '{definition.name}' references clip '{clip.name}' more than once.",
                            definition);
                        valid = false;
                    }

                    if (!clip.name.StartsWith(expectedPrefix, StringComparison.Ordinal))
                    {
                        Debug.LogWarning(
                            $"Clip '{clip.name}' does not follow expected event prefix '{expectedPrefix}'.",
                            clip);
                    }
                }
            }

            return valid;
        }
    }
}
