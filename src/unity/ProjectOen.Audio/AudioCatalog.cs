using System.Collections.Generic;
using UnityEngine;

namespace ProjectOen.Audio
{
    [CreateAssetMenu(
        fileName = "AudioCatalog",
        menuName = "Project Oen/Audio/Audio Catalog")]
    public sealed class AudioCatalog : ScriptableObject
    {
        [SerializeField] private AudioEventDefinition[] _events =
            System.Array.Empty<AudioEventDefinition>();

        public IReadOnlyList<AudioEventDefinition> Events => _events;
    }
}
