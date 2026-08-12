using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Dedicated emitter for persistent world sounds such as fire, tarp rain or machinery.
    /// Uses its own AudioSource so looping state belongs to the scene object.
    /// </summary>
    [RequireComponent(typeof(AudioSource))]
    public sealed class AudioLoopEmitter : MonoBehaviour
    {
        [SerializeField] private AudioEventDefinition _definition;
        [SerializeField] private bool _playOnEnable = true;
        [SerializeField, Range(0f, 1f)] private float _gain = 1f;

        private AudioSource _source;
        private float _baseVolume = 1f;

        public AudioEventDefinition Definition => _definition;
        public bool IsPlaying => _source != null && _source.isPlaying;
        public float Gain => _gain;

        private void Awake()
        {
            EnsureSource();
        }

        private void OnEnable()
        {
            if (_playOnEnable)
                Play();
        }

        private void OnDisable()
        {
            Stop();
        }

        public void Configure(AudioEventDefinition definition, bool restartIfPlaying = true)
        {
            if (_definition == definition)
                return;

            var wasPlaying = IsPlaying;
            Stop();
            _definition = definition;

            if (restartIfPlaying && wasPlaying && isActiveAndEnabled)
                Play();
        }

        public void SetGain(float gain)
        {
            _gain = Mathf.Clamp01(gain);
            if (_source != null)
                _source.volume = _baseVolume * _gain;
        }

        public bool Play()
        {
            EnsureSource();

            if (_definition == null || !_definition.Loop || !_definition.TryPickClip(out var clip))
                return false;

            _source.clip = clip;
            _source.outputAudioMixerGroup = _definition.Output;
            _source.loop = true;
            _source.spatialBlend = _definition.SpatialBlend;
            _baseVolume = _definition.PickVolume();
            _source.volume = _baseVolume * _gain;
            _source.pitch = _definition.PickPitch();
            _source.priority = _definition.Priority;
            _source.minDistance = _definition.MinDistance;
            _source.maxDistance = _definition.MaxDistance;
            _source.rolloffMode = _definition.RolloffMode;
            _source.Play();
            return true;
        }

        public void Stop()
        {
            if (_source == null)
                return;

            _source.Stop();
            _source.clip = null;
        }

        private void EnsureSource()
        {
            if (_source != null)
                return;

            _source = GetComponent<AudioSource>();
            _source.playOnAwake = false;
        }
    }
}
