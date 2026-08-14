using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Keeps a world-audio composition anchor near an explicitly assigned target.
    /// Scene/editor composition is responsible for assigning the target; the component never
    /// searches globally at runtime.
    /// </summary>
    public sealed class AudioWorldAnchorFollower : MonoBehaviour
    {
        [SerializeField] private Transform _target;
        [SerializeField] private bool _followVertical = false;

        public Transform Target => _target;
        public bool HasTarget => _target != null;

        public void Configure(Transform target, bool followVertical = false)
        {
            _target = target;
            _followVertical = followVertical;
            SnapToTarget();
        }

        private void LateUpdate()
        {
            SnapToTarget();
        }

        private void SnapToTarget()
        {
            if (_target == null)
                return;

            var targetPosition = _target.position;
            if (!_followVertical)
                targetPosition.y = transform.position.y;
            transform.position = targetPosition;
        }
    }
}
