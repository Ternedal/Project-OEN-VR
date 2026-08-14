using System;
using System.Collections.Generic;
using UnityEngine;

namespace ProjectOen.Audio
{
    [CreateAssetMenu(
        fileName = "AMB_Profile",
        menuName = "Project Oen/Audio/Ambience Profile")]
    public sealed class AudioAmbienceProfile : ScriptableObject
    {
        [Serializable]
        public sealed class Layer
        {
            [SerializeField] private AudioEventDefinition _definition;
            [SerializeField, Range(0f, 1f)] private float _gain = 1f;

            public AudioEventDefinition Definition => _definition;
            public float Gain => _gain;
        }

        [SerializeField] private Layer[] _layers = Array.Empty<Layer>();

        public IReadOnlyList<Layer> Layers => _layers;

        private void OnValidate()
        {
            if (_layers == null)
                _layers = Array.Empty<Layer>();
        }
    }
}
