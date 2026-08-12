using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Quest-friendly footstep driver. Can emit from locomotion distance or be called manually
    /// from another locomotion system via EmitStep(). Surface is resolved with a short ground ray.
    /// </summary>
    public sealed class FootstepAudioEmitter : MonoBehaviour
    {
        [SerializeField] private AudioService _audioService;
        [SerializeField] private Transform _movementReference;
        [SerializeField] private bool _driveFromDistance = true;
        [SerializeField, Min(0.1f)] private float _stepDistance = 0.72f;
        [SerializeField, Min(0f)] private float _minimumSpeed = 0.15f;
        [SerializeField, Min(0.5f)] private float _teleportResetDistance = 2.5f;

        [Header("Ground Probe")]
        [SerializeField] private LayerMask _groundMask = ~0;
        [SerializeField, Min(0f)] private float _rayStartHeight = 0.35f;
        [SerializeField, Min(0.1f)] private float _rayDistance = 1.6f;
        [SerializeField] private AudioSurfaceType _fallbackSurface = AudioSurfaceType.Dirt;

        private Vector3 _lastPosition;
        private float _distanceSinceStep;
        private bool _hasLastPosition;

        private Transform MovementReference => _movementReference != null ? _movementReference : transform;

        private void OnEnable()
        {
            ResetTracking();
        }

        private void Update()
        {
            if (!_driveFromDistance || _audioService == null)
                return;

            var current = MovementReference.position;
            if (!_hasLastPosition)
            {
                _lastPosition = current;
                _hasLastPosition = true;
                return;
            }

            var delta = current - _lastPosition;
            delta.y = 0f;
            var distance = delta.magnitude;
            _lastPosition = current;

            if (distance >= _teleportResetDistance)
            {
                _distanceSinceStep = 0f;
                return;
            }

            var deltaTime = Mathf.Max(Time.deltaTime, 0.0001f);
            var speed = distance / deltaTime;
            if (speed < _minimumSpeed)
                return;

            _distanceSinceStep += distance;
            if (_distanceSinceStep < _stepDistance)
                return;

            _distanceSinceStep %= _stepDistance;
            EmitStep();
        }

        public bool EmitStep()
        {
            if (_audioService == null)
                return false;

            var reference = MovementReference;
            var origin = reference.position + Vector3.up * _rayStartHeight;
            var surface = _fallbackSurface;
            var position = reference.position;

            if (Physics.Raycast(
                    origin,
                    Vector3.down,
                    out var hit,
                    _rayDistance,
                    _groundMask,
                    QueryTriggerInteraction.Ignore))
            {
                position = hit.point;
                var tag = hit.collider.GetComponentInParent<AudioSurfaceTag>();
                if (tag != null)
                    surface = tag.Surface;
            }

            return _audioService.TryPlayOneShot(ToEventId(surface), position);
        }

        public void ResetTracking()
        {
            _lastPosition = MovementReference.position;
            _distanceSinceStep = 0f;
            _hasLastPosition = true;
        }

        private static AudioEventId ToEventId(AudioSurfaceType surface)
        {
            return surface switch
            {
                AudioSurfaceType.SandDry => AudioEventId.SFX_PLY_Footstep_SandDry,
                AudioSurfaceType.SandWet => AudioEventId.SFX_PLY_Footstep_SandWet,
                AudioSurfaceType.Rock => AudioEventId.SFX_PLY_Footstep_Rock,
                AudioSurfaceType.Wood => AudioEventId.SFX_PLY_Footstep_Wood,
                AudioSurfaceType.Leaves => AudioEventId.SFX_PLY_Footstep_Leaves,
                AudioSurfaceType.ShallowWater => AudioEventId.SFX_PLY_Footstep_ShallowWater,
                _ => AudioEventId.SFX_PLY_Footstep_Dirt,
            };
        }
    }
}
