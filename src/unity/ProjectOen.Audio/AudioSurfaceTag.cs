using UnityEngine;

namespace ProjectOen.Audio
{
    public enum AudioSurfaceType : byte
    {
        SandDry = 0,
        SandWet = 1,
        Dirt = 2,
        Rock = 3,
        Wood = 4,
        Leaves = 5,
        ShallowWater = 6,
    }

    /// <summary>
    /// Lightweight marker used by FootstepAudioEmitter to resolve the material below the player.
    /// Put it on terrain proxy colliders, walkable meshes or parent objects.
    /// </summary>
    public sealed class AudioSurfaceTag : MonoBehaviour
    {
        [SerializeField] private AudioSurfaceType _surface = AudioSurfaceType.Dirt;

        public AudioSurfaceType Surface => _surface;
    }
}
