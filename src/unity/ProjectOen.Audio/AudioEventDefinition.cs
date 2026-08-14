using UnityEngine;
using UnityEngine.Audio;

namespace ProjectOen.Audio
{
    [CreateAssetMenu(
        fileName = "SFX_AudioEvent",
        menuName = "Project Oen/Audio/Audio Event Definition")]
    public sealed class AudioEventDefinition : ScriptableObject
    {
        [SerializeField] private AudioEventId _id = AudioEventId.None;
        [SerializeField] private AudioClip[] _clips = System.Array.Empty<AudioClip>();
        [SerializeField] private AudioMixerGroup _output;

        [Header("Playback")]
        [SerializeField] private bool _loop;
        [SerializeField, Range(0f, 1f)] private float _spatialBlend = 1f;
        [SerializeField, Range(0f, 1f)] private float _volumeMin = 0.9f;
        [SerializeField, Range(0f, 1f)] private float _volumeMax = 1f;
        [SerializeField, Range(0.1f, 3f)] private float _pitchMin = 0.96f;
        [SerializeField, Range(0.1f, 3f)] private float _pitchMax = 1.04f;
        [SerializeField, Range(0, 256)] private int _priority = 128;

        [Header("3D")]
        [SerializeField, Min(0f)] private float _minDistance = 1f;
        [SerializeField, Min(0.01f)] private float _maxDistance = 15f;
        [SerializeField] private AudioRolloffMode _rolloffMode = AudioRolloffMode.Logarithmic;

        public AudioEventId Id => _id;
        public AudioMixerGroup Output => _output;
        public bool Loop => _loop;
        public float SpatialBlend => _spatialBlend;
        public int Priority => _priority;
        public float MinDistance => _minDistance;
        public float MaxDistance => _maxDistance;
        public AudioRolloffMode RolloffMode => _rolloffMode;
        public int ClipCount => _clips?.Length ?? 0;

        public bool TryPickClip(out AudioClip clip)
        {
            clip = null;
            if (_clips == null || _clips.Length == 0)
                return false;

            clip = _clips[Random.Range(0, _clips.Length)];
            return clip != null;
        }

        public float PickVolume() => Random.Range(_volumeMin, _volumeMax);
        public float PickPitch() => Random.Range(_pitchMin, _pitchMax);

        private void OnValidate()
        {
            if (_volumeMin > _volumeMax)
                (_volumeMin, _volumeMax) = (_volumeMax, _volumeMin);

            if (_pitchMin > _pitchMax)
                (_pitchMin, _pitchMax) = (_pitchMax, _pitchMin);

            if (_maxDistance < _minDistance)
                _maxDistance = _minDistance;
        }
    }
}
