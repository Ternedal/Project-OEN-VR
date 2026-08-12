using System;
using UnityEngine;
using UnityEngine.Audio;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Keeps location/day ambience, storm ambience and adaptive music on separate buses so
    /// weather can layer over the current biome without a profile for every state combination.
    /// </summary>
    public sealed class AudioWorldStateRouter : MonoBehaviour
    {
        [Serializable]
        private sealed class BiomeBinding
        {
            [SerializeField] private AudioBiome _biome;
            [SerializeField] private AudioAmbienceProfile _day;
            [SerializeField] private AudioAmbienceProfile _night;

            public AudioBiome Biome => _biome;
            public AudioAmbienceProfile Resolve(AudioDayPhase phase) =>
                phase == AudioDayPhase.Night ? _night : _day;
        }

        [Serializable]
        private sealed class StormBinding
        {
            [SerializeField] private AudioStormPhase _phase;
            [SerializeField] private AudioAmbienceProfile _weatherProfile;
            [SerializeField] private AudioAmbienceProfile _musicProfile;
            [SerializeField] private AudioMixerSnapshot _exteriorSnapshot;
            [SerializeField] private AudioMixerSnapshot _shelteredSnapshot;

            public AudioStormPhase Phase => _phase;
            public AudioAmbienceProfile WeatherProfile => _weatherProfile;
            public AudioAmbienceProfile MusicProfile => _musicProfile;
            public AudioMixerSnapshot ExteriorSnapshot => _exteriorSnapshot;
            public AudioMixerSnapshot ShelteredSnapshot => _shelteredSnapshot;
        }

        [Header("Layer controllers")]
        [SerializeField] private AudioAmbienceController _biomeAmbience;
        [SerializeField] private AudioAmbienceController _weatherAmbience;
        [SerializeField] private AudioAmbienceController _musicAmbience;

        [Header("Biome profiles")]
        [SerializeField] private BiomeBinding[] _biomes = Array.Empty<BiomeBinding>();
        [SerializeField] private AudioAmbienceProfile _shelterDay;
        [SerializeField] private AudioAmbienceProfile _shelterNight;

        [Header("Storm progression")]
        [SerializeField] private StormBinding[] _storms = Array.Empty<StormBinding>();
        [SerializeField, Min(0f)] private float _biomeFadeSeconds = 4f;
        [SerializeField, Min(0f)] private float _weatherFadeSeconds = 3f;
        [SerializeField, Min(0f)] private float _musicFadeSeconds = 2.5f;
        [SerializeField, Min(0f)] private float _snapshotFadeSeconds = 1.5f;

        [Header("Initial state")]
        [SerializeField] private AudioBiome _biome = AudioBiome.Beach;
        [SerializeField] private AudioDayPhase _dayPhase = AudioDayPhase.Day;
        [SerializeField] private AudioStormPhase _stormPhase = AudioStormPhase.Calm;
        [SerializeField] private bool _sheltered;

        public AudioBiome Biome => _biome;
        public AudioDayPhase DayPhase => _dayPhase;
        public AudioStormPhase StormPhase => _stormPhase;
        public bool Sheltered => _sheltered;

        /// <summary>
        /// Raised after an audio-relevant world state changes and after the initial state is applied.
        /// Dependent audio adapters can subscribe without polling or owning simulation state.
        /// </summary>
        public event Action StateChanged;

        private void Start()
        {
            ApplyBiomeLayer();
            ApplyStormLayer();
            StateChanged?.Invoke();
        }

        public void SetBiome(AudioBiome biome)
        {
            if (_biome == biome)
                return;

            _biome = biome;
            if (!_sheltered)
                ApplyBiomeLayer();
            StateChanged?.Invoke();
        }

        public void SetDayPhase(AudioDayPhase phase)
        {
            if (_dayPhase == phase)
                return;

            _dayPhase = phase;
            ApplyBiomeLayer();
            StateChanged?.Invoke();
        }

        public void SetStormPhase(AudioStormPhase phase)
        {
            if (_stormPhase == phase)
                return;

            _stormPhase = phase;
            ApplyStormLayer();
            StateChanged?.Invoke();
        }

        public void SetSheltered(bool sheltered)
        {
            if (_sheltered == sheltered)
                return;

            _sheltered = sheltered;
            ApplyBiomeLayer();
            ApplyMixerSnapshot();
            StateChanged?.Invoke();
        }

        private void ApplyBiomeLayer()
        {
            if (_biomeAmbience == null)
                return;

            AudioAmbienceProfile profile = null;
            if (_sheltered)
            {
                profile = _dayPhase == AudioDayPhase.Night ? _shelterNight : _shelterDay;
            }
            else
            {
                for (var i = 0; i < _biomes.Length; i++)
                {
                    var binding = _biomes[i];
                    if (binding == null || binding.Biome != _biome)
                        continue;

                    profile = binding.Resolve(_dayPhase);
                    break;
                }
            }

            if (profile != null)
                _biomeAmbience.TransitionTo(profile, _biomeFadeSeconds);
        }

        private void ApplyStormLayer()
        {
            var binding = FindStormBinding();
            if (binding == null)
                return;

            // Calm should use assigned empty/near-silent weather and music profiles so both
            // state layers can crossfade back to silence cleanly.
            if (_weatherAmbience != null && binding.WeatherProfile != null)
                _weatherAmbience.TransitionTo(binding.WeatherProfile, _weatherFadeSeconds);

            if (_musicAmbience != null && binding.MusicProfile != null)
                _musicAmbience.TransitionTo(binding.MusicProfile, _musicFadeSeconds);

            ApplyMixerSnapshot(binding);
        }

        private void ApplyMixerSnapshot()
        {
            var binding = FindStormBinding();
            if (binding != null)
                ApplyMixerSnapshot(binding);
        }

        private void ApplyMixerSnapshot(StormBinding binding)
        {
            var snapshot = _sheltered && binding.ShelteredSnapshot != null
                ? binding.ShelteredSnapshot
                : binding.ExteriorSnapshot;

            if (snapshot != null)
                snapshot.TransitionTo(_snapshotFadeSeconds);
        }

        private StormBinding FindStormBinding()
        {
            for (var i = 0; i < _storms.Length; i++)
            {
                var binding = _storms[i];
                if (binding != null && binding.Phase == _stormPhase)
                    return binding;
            }

            return null;
        }
    }
}
