using System.Collections;
using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Emits intermittent one-shots around a world point. Useful for fauna, branch snaps,
    /// shoreline washes, fire pops and wind gusts without placing hundreds of emitters.
    /// </summary>
    public sealed class AudioRandomEmitter : MonoBehaviour
    {
        [SerializeField] private AudioService _audioService;
        [SerializeField] private AudioEventId[] _events = System.Array.Empty<AudioEventId>();
        [SerializeField] private Vector2 _delaySeconds = new(4f, 12f);
        [SerializeField, Min(0f)] private float _horizontalRadius = 5f;
        [SerializeField, Min(0f)] private float _verticalJitter = 1f;
        [SerializeField] private bool _playOnEnable = true;

        private Coroutine _routine;

        private void OnEnable()
        {
            if (_playOnEnable)
                StartEmitting();
        }

        private void OnDisable()
        {
            StopEmitting();
        }

        public void StartEmitting()
        {
            if (_routine != null || _audioService == null || _events == null || _events.Length == 0)
                return;

            _routine = StartCoroutine(EmitRoutine());
        }

        public void StopEmitting()
        {
            if (_routine == null)
                return;

            StopCoroutine(_routine);
            _routine = null;
        }

        public bool EmitNow()
        {
            if (_audioService == null || _events == null || _events.Length == 0)
                return false;

            var id = _events[Random.Range(0, _events.Length)];
            if (id == AudioEventId.None)
                return false;

            var offset2D = Random.insideUnitCircle * _horizontalRadius;
            var position = transform.position +
                           new Vector3(offset2D.x, Random.Range(-_verticalJitter, _verticalJitter), offset2D.y);

            return _audioService.TryPlayOneShot(id, position);
        }

        private IEnumerator EmitRoutine()
        {
            while (isActiveAndEnabled)
            {
                var min = Mathf.Max(0.05f, Mathf.Min(_delaySeconds.x, _delaySeconds.y));
                var max = Mathf.Max(min, Mathf.Max(_delaySeconds.x, _delaySeconds.y));
                yield return new WaitForSeconds(Random.Range(min, max));
                EmitNow();
            }

            _routine = null;
        }

        private void OnValidate()
        {
            _delaySeconds.x = Mathf.Max(0.05f, _delaySeconds.x);
            _delaySeconds.y = Mathf.Max(0.05f, _delaySeconds.y);
        }
    }
}
