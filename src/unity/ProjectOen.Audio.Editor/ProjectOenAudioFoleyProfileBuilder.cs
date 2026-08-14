using System;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Audio.Editor
{
    public static class ProjectOenAudioFoleyProfileBuilder
    {
        private const string Root = "Assets/ProjectOen/Audio/FoleyProfiles";

        private readonly struct Mapping
        {
            public Mapping(AudioFoleyAction action, AudioEventId eventId)
            {
                Action = action;
                EventId = eventId;
            }

            public AudioFoleyAction Action { get; }
            public AudioEventId EventId { get; }
        }

        [MenuItem("Project Oen/Audio/Rebuild Default Foley Profiles")]
        public static void RebuildDefaultProfiles()
        {
            EnsureFolder(Root);

            WriteProfile("Tarp", new[]
            {
                M(AudioFoleyAction.Flap, AudioEventId.SFX_ENV_Tarp_Flap),
                M(AudioFoleyAction.Handle, AudioEventId.SFX_ENV_Tarp_Handle),
                M(AudioFoleyAction.Tension, AudioEventId.SFX_ENV_Tarp_Tension),
            });

            WriteProfile("Rope", new[]
            {
                M(AudioFoleyAction.Handle, AudioEventId.SFX_ENV_Rope_Handle),
                M(AudioFoleyAction.Tighten, AudioEventId.SFX_ENV_Rope_Tighten),
                M(AudioFoleyAction.Creak, AudioEventId.SFX_ENV_Rope_Creak),
                M(AudioFoleyAction.TensionRelease, AudioEventId.SFX_ENV_Rope_TensionRelease),
            });

            WriteProfile("Wood", new[]
            {
                M(AudioFoleyAction.Pickup, AudioEventId.SFX_ENV_Wood_Pickup),
                M(AudioFoleyAction.Drop, AudioEventId.SFX_ENV_Wood_Drop),
                M(AudioFoleyAction.Impact, AudioEventId.SFX_ENV_Wood_Hit),
                M(AudioFoleyAction.Break, AudioEventId.SFX_ENV_Wood_Break),
                M(AudioFoleyAction.Chop, AudioEventId.SFX_ENV_Wood_Chop),
            });

            WriteProfile("Stone", new[]
            {
                M(AudioFoleyAction.Pickup, AudioEventId.SFX_ENV_Stone_Pickup),
                M(AudioFoleyAction.Drop, AudioEventId.SFX_ENV_Stone_Drop),
                M(AudioFoleyAction.Impact, AudioEventId.SFX_ENV_Stone_Hit),
            });

            WriteProfile("Water", new[]
            {
                M(AudioFoleyAction.SplashSmall, AudioEventId.SFX_ENV_Water_SplashSmall),
                M(AudioFoleyAction.SplashLarge, AudioEventId.SFX_ENV_Water_SplashLarge),
                M(AudioFoleyAction.Pour, AudioEventId.SFX_ENV_Water_Pour),
            });

            WriteProfile("Container", new[]
            {
                M(AudioFoleyAction.Drop, AudioEventId.SFX_ENV_Container_SetDown),
                M(AudioFoleyAction.Open, AudioEventId.SFX_ENV_Container_Open),
                M(AudioFoleyAction.Close, AudioEventId.SFX_ENV_Container_Close),
            });

            WriteProfile("Crate", new[]
            {
                M(AudioFoleyAction.Drop, AudioEventId.SFX_ENV_Container_SetDown),
                M(AudioFoleyAction.Open, AudioEventId.SFX_ENV_Crate_Open),
                M(AudioFoleyAction.Close, AudioEventId.SFX_ENV_Crate_Close),
            });

            WriteProfile("Metal", new[]
            {
                M(AudioFoleyAction.Scrape, AudioEventId.SFX_ENV_Metal_Scrape),
                M(AudioFoleyAction.Impact, AudioEventId.SFX_ENV_Metal_Impact),
            });

            WriteProfile("Fire", new[]
            {
                M(AudioFoleyAction.AddFuel, AudioEventId.SFX_ENV_Fire_AddWood),
                M(AudioFoleyAction.Ignite, AudioEventId.SFX_ENV_Fire_Ignite),
                M(AudioFoleyAction.Extinguish, AudioEventId.SFX_ENV_Fire_Extinguish),
            });

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Project Oen audio: rebuilt 9 default Foley profiles.");
        }

        private static Mapping M(AudioFoleyAction action, AudioEventId eventId)
            => new Mapping(action, eventId);

        private static void WriteProfile(string name, Mapping[] mappings)
        {
            var path = $"{Root}/{name}.asset";
            var profile = AssetDatabase.LoadAssetAtPath<AudioFoleyProfile>(path);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<AudioFoleyProfile>();
                AssetDatabase.CreateAsset(profile, path);
            }

            var serialized = new SerializedObject(profile);
            var entries = serialized.FindProperty("_entries");
            entries.arraySize = mappings.Length;

            for (var i = 0; i < mappings.Length; i++)
            {
                var entry = entries.GetArrayElementAtIndex(i);
                entry.FindPropertyRelative("_action").enumValueIndex = (int)mappings[i].Action;
                entry.FindPropertyRelative("_eventId").intValue = (ushort)mappings[i].EventId;
            }

            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(profile);
        }

        private static void EnsureFolder(string fullPath)
        {
            var parts = fullPath.Split('/');
            var current = parts[0];

            for (var i = 1; i < parts.Length; i++)
            {
                var next = $"{current}/{parts[i]}";
                if (!AssetDatabase.IsValidFolder(next))
                    AssetDatabase.CreateFolder(current, parts[i]);

                current = next;
            }
        }
    }
}
