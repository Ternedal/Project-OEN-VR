using UnityEngine;

namespace ProjectOen.Audio
{
    public enum AudioFireState : byte
    {
        Off = 0,
        Low = 1,
        Burning = 2,
    }

    /// <summary>
    /// Audio adapter for the campfire gameplay state. The gameplay system only needs to call
    /// SetBurnIntensity/SetState and explicit interaction hooks; clip selection remains in audio data.
    /// </summary>
    public sealed class AudioFireStateEmitter : MonoBehaviour
    {
        [SerializeField] private AudioService _audioService;
        [SerializeField] private AudioLoopEmitter _fireLoop;
        [SerializeField] private AudioRandomEmitter _firePops;
        [SerializeField] private AudioEventDefinition _lowLoop;
        [SerializeField] private AudioEventDefinition _burningLoop;
        [SerializeField] private AudioFireState _initialState = AudioFireState.Off;

        private AudioFireState _state;

        public AudioFireState State => _state;

        private void Start()
        {
            ApplyState(_initialState);
        }

        public void SetBurnIntensity(float normalized)
        {
            normalized = Mathf.Clamp01(normalized);
            var next = normalized <= 0.02f
                ? AudioFireState.Off
                : normalized < 0.35f
                    ? AudioFireState.Low
                    : AudioFireState.Burning;

            SetState(next);
        }

        public void SetState(AudioFireState state)
        {
            if (_state == state)
                return;

            ApplyState(state);
        }

        public void OnIgnited()
        {
            PlayOneShot(AudioEventId.SFX_ENV_Fire_Ignite);
            SetState(AudioFireState.Burning);
        }

        public void OnWoodAdded()
        {
            PlayOneShot(AudioEventId.SFX_ENV_Fire_AddWood);
            SetState(AudioFireState.Burning);
        }

        public void OnExtinguished()
        {
            PlayOneShot(AudioEventId.SFX_ENV_Fire_Extinguish);
            SetState(AudioFireState.Off);
        }

        private void ApplyState(AudioFireState state)
        {
            _state = state;

            if (_fireLoop == null)
                return;

            switch (_state)
            {
                case AudioFireState.Off:
                    _fireLoop.Stop();
                    _firePops?.StopEmitting();
                    break;

                case AudioFireState.Low:
                    _fireLoop.Configure(_lowLoop, false);
                    _fireLoop.SetGain(0.75f);
                    _fireLoop.Play();
                    if (_firePops != null)
                    {
                        _firePops.SetDelayRange(8f, 16f);
                        _firePops.StartEmitting();
                    }
                    break;

                case AudioFireState.Burning:
                    _fireLoop.Configure(_burningLoop, false);
                    _fireLoop.SetGain(1f);
                    _fireLoop.Play();
                    if (_firePops != null)
                    {
                        _firePops.SetDelayRange(3f, 8f);
                        _firePops.StartEmitting();
                    }
                    break;
            }
        }

        private void PlayOneShot(AudioEventId id)
        {
            if (_audioService != null)
                _audioService.TryPlayOneShot(id, transform.position);
        }
    }
}
