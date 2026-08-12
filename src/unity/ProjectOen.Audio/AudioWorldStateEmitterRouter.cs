using System;
using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Starts and stops intermittent world emitters from the already-authoritative audio world state.
    /// This keeps fauna/weather one-shots state-aware without duplicating simulation state.
    /// </summary>
    public sealed class AudioWorldStateEmitterRouter : MonoBehaviour
    {
        [Serializable]
        private sealed class Binding
        {
            [SerializeField] private AudioRandomEmitter _emitter;
            [SerializeField] private AudioBiome _biome;
            [SerializeField] private bool _matchBiome = true;
            [SerializeField] private AudioDayPhase _dayPhase = AudioDayPhase.Day;
            [SerializeField] private bool _matchDayPhase = true;
            [SerializeField] private AudioStormPhase _stormPhase = AudioStormPhase.Calm;
            [SerializeField] private bool _exteriorOnly = true;

            public AudioRandomEmitter Emitter => _emitter;

            public bool Matches(AudioWorldStateRouter state)
            {
                if (state == null || _emitter == null)
                    return false;
                if (_matchBiome && state.Biome != _biome)
                    return false;
                if (_matchDayPhase && state.DayPhase != _dayPhase)
                    return false;
                if (state.StormPhase != _stormPhase)
                    return false;
                if (_exteriorOnly && state.Sheltered)
                    return false;
                return true;
            }
        }

        [SerializeField] private AudioWorldStateRouter _worldState;
        [SerializeField] private Binding[] _bindings = Array.Empty<Binding>();

        private void OnEnable()
        {
            if (!Application.isPlaying)
            {
                StopAll();
                return;
            }

            if (_worldState != null)
                _worldState.StateChanged += Apply;
            Apply();
        }

        private void OnDisable()
        {
            if (_worldState != null)
                _worldState.StateChanged -= Apply;
            StopAll();
        }

        public void Apply()
        {
            if (!Application.isPlaying)
            {
                StopAll();
                return;
            }

            if (_bindings == null)
                return;

            for (var i = 0; i < _bindings.Length; i++)
            {
                var binding = _bindings[i];
                if (binding == null || binding.Emitter == null)
                    continue;

                if (binding.Matches(_worldState))
                    binding.Emitter.StartEmitting();
                else
                    binding.Emitter.StopEmitting();
            }
        }

        private void StopAll()
        {
            if (_bindings == null)
                return;

            for (var i = 0; i < _bindings.Length; i++)
            {
                var emitter = _bindings[i]?.Emitter;
                if (emitter != null)
                    emitter.StopEmitting();
            }
        }
    }
}
