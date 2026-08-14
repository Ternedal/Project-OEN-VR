using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Converts normalized weather values into local shelter feedback: rain-on-tarp gain and
    /// wind-dependent flap cadence. This stays local/diegetic while broad weather lives in the
    /// world-state weather layer.
    /// </summary>
    public sealed class AudioTarpWeatherEmitter : MonoBehaviour
    {
        [SerializeField] private AudioService _audioService;
        [SerializeField] private AudioLoopEmitter _rainLoop;
        [SerializeField] private AudioRandomEmitter _flapEmitter;
        [SerializeField] private AudioEventDefinition _rainOnTarpLoop;

        [Header("Flap cadence")]
        [SerializeField] private Vector2 _calmDelaySeconds = new(10f, 18f);
        [SerializeField] private Vector2 _stormDelaySeconds = new(1.2f, 3.5f);

        private float _wind;
        private float _rain;

        public float Wind => _wind;
        public float Rain => _rain;

        private void Start()
        {
            ApplyWeather();
        }

        public void SetWeather(float windNormalized, float rainNormalized)
        {
            _wind = Mathf.Clamp01(windNormalized);
            _rain = Mathf.Clamp01(rainNormalized);
            ApplyWeather();
        }

        public void SetWind(float normalized)
        {
            _wind = Mathf.Clamp01(normalized);
            ApplyWind();
        }

        public void SetRain(float normalized)
        {
            _rain = Mathf.Clamp01(normalized);
            ApplyRain();
        }

        public void OnTarpHandled()
        {
            PlayOneShot(AudioEventId.SFX_ENV_Tarp_Handle);
        }

        public void OnTensionChanged()
        {
            PlayOneShot(AudioEventId.SFX_ENV_Tarp_Tension);
        }

        private void ApplyWeather()
        {
            ApplyWind();
            ApplyRain();
        }

        private void ApplyWind()
        {
            if (_flapEmitter == null)
                return;

            if (_wind <= 0.05f)
            {
                _flapEmitter.StopEmitting();
                return;
            }

            var minDelay = Mathf.Lerp(_calmDelaySeconds.x, _stormDelaySeconds.x, _wind);
            var maxDelay = Mathf.Lerp(_calmDelaySeconds.y, _stormDelaySeconds.y, _wind);
            _flapEmitter.SetDelayRange(minDelay, maxDelay);
            _flapEmitter.StartEmitting();
        }

        private void ApplyRain()
        {
            if (_rainLoop == null)
                return;

            if (_rain <= 0.02f)
            {
                _rainLoop.Stop();
                return;
            }

            _rainLoop.Configure(_rainOnTarpLoop, false);
            _rainLoop.SetGain(Mathf.Lerp(0.25f, 1f, _rain));
            if (!_rainLoop.IsPlaying)
                _rainLoop.Play();
        }

        private void PlayOneShot(AudioEventId id)
        {
            if (_audioService != null)
                _audioService.TryPlayOneShot(id, transform.position);
        }
    }
}
