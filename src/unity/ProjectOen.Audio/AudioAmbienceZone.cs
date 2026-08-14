using System.Collections.Generic;
using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Trigger volume that changes the active ambience profile when the player enters.
    /// Assign an exit profile for nested spaces such as shelters inside a beach biome.
    /// Multiple matching colliders are tracked as one occupancy session so XR/player rigs do not
    /// transition out merely because one child collider leaves while another remains inside.
    /// </summary>
    [RequireComponent(typeof(Collider))]
    public sealed class AudioAmbienceZone : MonoBehaviour
    {
        [SerializeField] private AudioAmbienceController _controller;
        [SerializeField] private AudioAmbienceProfile _enterProfile;
        [SerializeField] private AudioAmbienceProfile _exitProfile;
        [SerializeField, Min(0f)] private float _fadeSeconds = 3f;
        [SerializeField] private string _requiredTag = "Player";

        private readonly HashSet<Collider> _occupants = new();

        private void Reset()
        {
            var zone = GetComponent<Collider>();
            if (zone != null)
                zone.isTrigger = true;
        }

        private void OnDisable()
        {
            _occupants.Clear();
        }

        private void OnTriggerEnter(Collider other)
        {
            if (!Matches(other))
                return;

            var wasEmpty = _occupants.Count == 0;
            _occupants.Add(other);
            if (!wasEmpty || _controller == null || _enterProfile == null)
                return;

            _controller.TransitionTo(_enterProfile, _fadeSeconds);
        }

        private void OnTriggerExit(Collider other)
        {
            if (other == null || !_occupants.Remove(other) || _occupants.Count != 0)
                return;

            if (_controller == null || _exitProfile == null)
                return;

            _controller.TransitionTo(_exitProfile, _fadeSeconds);
        }

        private bool Matches(Collider other)
        {
            if (other == null)
                return false;

            if (string.IsNullOrWhiteSpace(_requiredTag))
                return true;

            return other.CompareTag(_requiredTag) ||
                   (other.transform.root != null && other.transform.root.CompareTag(_requiredTag));
        }
    }
}
