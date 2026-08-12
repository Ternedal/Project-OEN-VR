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

        private AudioSource _source;

        private void Awake()
        {
            _source = GetComponent<AudioSource>();
            _source.playOnAwake = false;
        }

        private void OnEnable()
        {
            if (_playOnEnable)
                Play();
        }

        private void OnDisable()
        {
            if (_source != null)
                _source.Stop();
        }

        public bool Play()
        {
            if (_definition == null || !_definition.Loop || !_definition.TryPickClip(out var clip))
                return false;

            _source.clip = clip;
            _source.outputAudioMixerGroup = _definition.Output;
            _source.loop = true;
            _source.spatialBlend = _definition.SpatialBlend;
            _source.volume = _definition.PickVolume();
            _source.pitch = _definition.PickPitch();
            _source.priority = _definition.Priority;
            _source.minDistance = _definition.MinDistance;
            _source.maxDistance = _definition.MaxDistance;
            _source.rolloffMode = _definition.RolloffMode;
            _source.Play();
            return true;
        }
    }
}
