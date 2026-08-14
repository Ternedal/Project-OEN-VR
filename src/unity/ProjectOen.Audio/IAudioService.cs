using UnityEngine;

namespace ProjectOen.Audio
{
    public interface IAudioService
    {
        bool TryPlayOneShot(AudioEventId id, Vector3 worldPosition);
        bool TryResolve(AudioEventId id, out AudioEventDefinition definition);
    }
}
