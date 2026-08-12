using System;
using System.Collections.Generic;
using UnityEngine;

namespace ProjectOen.Audio
{
    public enum AudioFoleyAction : byte
    {
        Pickup = 0,
        Drop = 1,
        Impact = 2,
        Handle = 3,
        Open = 4,
        Close = 5,
        Tighten = 6,
        Creak = 7,
        Tension = 8,
        TensionRelease = 9,
        Break = 10,
        Chop = 11,
        Scrape = 12,
        Pour = 13,
        SplashSmall = 14,
        SplashLarge = 15,
        Flap = 16,
        Ignite = 17,
        Extinguish = 18,
        AddFuel = 19,
        Use = 20,
    }

    [CreateAssetMenu(
        fileName = "FoleyProfile",
        menuName = "Project Oen/Audio/Foley Profile")]
    public sealed class AudioFoleyProfile : ScriptableObject
    {
        [Serializable]
        private struct Entry
        {
            [SerializeField] private AudioFoleyAction _action;
            [SerializeField] private AudioEventId _eventId;

            public AudioFoleyAction Action => _action;
            public AudioEventId EventId => _eventId;
        }

        [SerializeField] private Entry[] _entries = Array.Empty<Entry>();

        public bool TryResolve(AudioFoleyAction action, out AudioEventId eventId)
        {
            if (_entries != null)
            {
                for (var i = 0; i < _entries.Length; i++)
                {
                    if (_entries[i].Action != action)
                        continue;

                    eventId = _entries[i].EventId;
                    return eventId != AudioEventId.None;
                }
            }

            eventId = AudioEventId.None;
            return false;
        }

        private void OnValidate()
        {
            if (_entries == null || _entries.Length < 2)
                return;

            var seen = new HashSet<AudioFoleyAction>();
            for (var i = 0; i < _entries.Length; i++)
            {
                if (seen.Add(_entries[i].Action))
                    continue;

                Debug.LogError(
                    $"Duplicate Foley action '{_entries[i].Action}' in profile '{name}'.",
                    this);
            }
        }
    }
}
