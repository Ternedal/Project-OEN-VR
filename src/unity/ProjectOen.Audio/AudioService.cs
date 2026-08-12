using System.Collections.Generic;
using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Scene-owned audio playback service. Deliberately not a singleton.
    /// Runtime state (lookup + AudioSource pool) lives here; ScriptableObjects remain definition data.
    /// </summary>
    public sealed class AudioService : MonoBehaviour, IAudioService
    {
        [SerializeField] private AudioCatalog _catalog;
        [SerializeField, Min(4)] private int _oneShotPoolSize = 24;
        [SerializeField] private Transform _poolRoot;

        private readonly Dictionary<AudioEventId, AudioEventDefinition> _lookup = new();
        private AudioSource[] _oneShotPool = System.Array.Empty<AudioSource>();

        private void Awake()
        {
            BuildLookup();
            BuildPool();
        }

        public bool TryResolve(AudioEventId id, out AudioEventDefinition definition)
            => _lookup.TryGetValue(id, out definition);

        public bool TryPlayOneShot(AudioEventId id, Vector3 worldPosition)
        {
            if (!TryResolve(id, out var definition) || definition == null)
                return false;

            if (definition.Loop || !definition.TryPickClip(out var clip))
                return false;

            var source = FindFreeSource();
            if (source == null)
                return false;

            ConfigureSource(source, definition, worldPosition);
            source.clip = clip;
            source.loop = false;
            source.Play();
            return true;
        }

        private void BuildLookup()
        {
            _lookup.Clear();

            if (_catalog == null)
                return;

            foreach (var definition in _catalog.Events)
            {
                if (definition == null || definition.Id == AudioEventId.None)
                    continue;

                if (_lookup.ContainsKey(definition.Id))
                {
                    Debug.LogError(
                        $"Duplicate audio event id '{definition.Id}' in catalog '{_catalog.name}'.",
                        _catalog);
                    continue;
                }

                _lookup.Add(definition.Id, definition);
            }
        }

        private void BuildPool()
        {
            var root = _poolRoot != null ? _poolRoot : transform;
            _oneShotPool = new AudioSource[_oneShotPoolSize];

            for (var i = 0; i < _oneShotPool.Length; i++)
            {
                var child = new GameObject($"AudioOneShot_{i:00}");
                child.transform.SetParent(root, false);
                var source = child.AddComponent<AudioSource>();
                source.playOnAwake = false;
                _oneShotPool[i] = source;
            }
        }

        private AudioSource FindFreeSource()
        {
            foreach (var source in _oneShotPool)
            {
                if (source != null && !source.isPlaying)
                    return source;
            }

            return null;
        }

        private static void ConfigureSource(
            AudioSource source,
            AudioEventDefinition definition,
            Vector3 worldPosition)
        {
            source.transform.position = worldPosition;
            source.outputAudioMixerGroup = definition.Output;
            source.spatialBlend = definition.SpatialBlend;
            source.volume = definition.PickVolume();
            source.pitch = definition.PickPitch();
            source.priority = definition.Priority;
            source.minDistance = definition.MinDistance;
            source.maxDistance = definition.MaxDistance;
            source.rolloffMode = definition.RolloffMode;
        }
    }
}
