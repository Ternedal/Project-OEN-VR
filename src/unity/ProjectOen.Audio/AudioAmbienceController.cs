using System.Collections;
using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Crossfades layered ambience profiles using two AudioSource banks.
    /// Designed for biome, shelter and weather transitions without hard cuts.
    /// </summary>
    public sealed class AudioAmbienceController : MonoBehaviour
    {
        [SerializeField] private AudioAmbienceProfile _initialProfile;
        [SerializeField, Min(0f)] private float _defaultFadeSeconds = 4f;
        [SerializeField, Range(1, 12)] private int _maxLayers = 6;
        [SerializeField] private Transform _sourceRoot;

        private AudioSource[][] _banks;
        private int _activeBank;
        private AudioAmbienceProfile _currentProfile;
        private AudioAmbienceProfile _targetProfile;
        private Coroutine _transitionRoutine;

        public AudioAmbienceProfile CurrentProfile => _currentProfile;
        public AudioAmbienceProfile TargetProfile => _targetProfile;

        private void Awake()
        {
            BuildBanks();
        }

        private void OnEnable()
        {
            // On the first enable Start() owns initial-profile setup. On later enables the
            // controller must restore the last settled profile because OnDisable() stops both banks.
            if (_banks != null && _currentProfile != null)
                ApplyImmediate(_currentProfile);
        }

        private void Start()
        {
            if (_initialProfile != null && _currentProfile == null)
                ApplyImmediate(_initialProfile);
        }

        private void OnDisable()
        {
            if (_transitionRoutine != null)
            {
                StopCoroutine(_transitionRoutine);
                _transitionRoutine = null;
            }

            if (_banks != null)
            {
                StopBank(_banks[0]);
                StopBank(_banks[1]);
            }
        }

        public void TransitionTo(AudioAmbienceProfile profile)
            => TransitionTo(profile, _defaultFadeSeconds);

        public void TransitionTo(AudioAmbienceProfile profile, float fadeSeconds)
        {
            if (profile == null || profile == _targetProfile)
                return;

            if (_transitionRoutine != null)
                StopCoroutine(_transitionRoutine);

            _targetProfile = profile;
            _transitionRoutine = StartCoroutine(TransitionRoutine(profile, Mathf.Max(0f, fadeSeconds)));
        }

        public void ApplyImmediate(AudioAmbienceProfile profile)
        {
            if (profile == null || _banks == null)
                return;

            if (_transitionRoutine != null)
            {
                StopCoroutine(_transitionRoutine);
                _transitionRoutine = null;
            }

            StopBank(_banks[0]);
            StopBank(_banks[1]);
            _activeBank = 0;
            PrepareBank(_banks[_activeBank], profile, true);
            _currentProfile = profile;
            _targetProfile = profile;
        }

        private IEnumerator TransitionRoutine(AudioAmbienceProfile nextProfile, float duration)
        {
            var oldBankIndex = _activeBank;
            var newBankIndex = 1 - _activeBank;
            var oldBank = _banks[oldBankIndex];
            var newBank = _banks[newBankIndex];

            var targetVolumes = PrepareBank(newBank, nextProfile, false);
            var oldStartVolumes = CaptureVolumes(oldBank);

            if (duration <= 0f)
            {
                SetVolumes(newBank, targetVolumes, 1f);
                StopBank(oldBank);
                _activeBank = newBankIndex;
                _currentProfile = nextProfile;
                _targetProfile = nextProfile;
                _transitionRoutine = null;
                yield break;
            }

            var elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                var t = Mathf.Clamp01(elapsed / duration);
                var smooth = t * t * (3f - 2f * t);

                for (var i = 0; i < oldBank.Length; i++)
                {
                    if (oldBank[i] != null)
                        oldBank[i].volume = oldStartVolumes[i] * (1f - smooth);
                }

                SetVolumes(newBank, targetVolumes, smooth);
                yield return null;
            }

            SetVolumes(newBank, targetVolumes, 1f);
            StopBank(oldBank);
            _activeBank = newBankIndex;
            _currentProfile = nextProfile;
            _targetProfile = nextProfile;
            _transitionRoutine = null;
        }

        private void BuildBanks()
        {
            var root = _sourceRoot != null ? _sourceRoot : transform;
            _banks = new AudioSource[2][];

            for (var bankIndex = 0; bankIndex < _banks.Length; bankIndex++)
            {
                _banks[bankIndex] = new AudioSource[_maxLayers];
                for (var layerIndex = 0; layerIndex < _maxLayers; layerIndex++)
                {
                    var child = new GameObject($"Ambience_{bankIndex}_{layerIndex:00}");
                    child.transform.SetParent(root, false);
                    var source = child.AddComponent<AudioSource>();
                    source.playOnAwake = false;
                    source.loop = true;
                    _banks[bankIndex][layerIndex] = source;
                }
            }
        }

        private float[] PrepareBank(AudioSource[] bank, AudioAmbienceProfile profile, bool useTargetVolume)
        {
            StopBank(bank);
            var targetVolumes = new float[bank.Length];
            var layers = profile.Layers;
            var count = Mathf.Min(bank.Length, layers.Count);

            for (var i = 0; i < count; i++)
            {
                var layer = layers[i];
                var definition = layer?.Definition;
                if (definition == null || !definition.Loop || !definition.TryPickClip(out var clip))
                    continue;

                var source = bank[i];
                source.clip = clip;
                source.outputAudioMixerGroup = definition.Output;
                source.loop = true;
                source.spatialBlend = definition.SpatialBlend;
                source.pitch = definition.PickPitch();
                source.priority = definition.Priority;
                source.minDistance = definition.MinDistance;
                source.maxDistance = definition.MaxDistance;
                source.rolloffMode = definition.RolloffMode;

                targetVolumes[i] = definition.PickVolume() * layer.Gain;
                source.volume = useTargetVolume ? targetVolumes[i] : 0f;
                source.Play();
            }

            return targetVolumes;
        }

        private static float[] CaptureVolumes(AudioSource[] bank)
        {
            var values = new float[bank.Length];
            for (var i = 0; i < bank.Length; i++)
                values[i] = bank[i] != null ? bank[i].volume : 0f;
            return values;
        }

        private static void SetVolumes(AudioSource[] bank, float[] targets, float multiplier)
        {
            for (var i = 0; i < bank.Length && i < targets.Length; i++)
            {
                if (bank[i] != null)
                    bank[i].volume = targets[i] * multiplier;
            }
        }

        private static void StopBank(AudioSource[] bank)
        {
            if (bank == null)
                return;

            foreach (var source in bank)
            {
                if (source == null)
                    continue;

                source.Stop();
                source.clip = null;
                source.volume = 0f;
            }
        }
    }
}
