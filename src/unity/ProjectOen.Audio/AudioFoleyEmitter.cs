using UnityEngine;

namespace ProjectOen.Audio
{
    /// <summary>
    /// Reusable object-level Foley bridge. Prefabs bind semantic actions to an AudioFoleyProfile
    /// instead of referencing clips directly. The scene-owned AudioService remains the playback owner.
    /// </summary>
    public sealed class AudioFoleyEmitter : MonoBehaviour
    {
        [SerializeField] private AudioService _audioService;
        [SerializeField] private AudioFoleyProfile _profile;
        [SerializeField] private Transform _emissionPoint;

        private Vector3 EmissionPosition =>
            _emissionPoint != null ? _emissionPoint.position : transform.position;

        public bool TryEmit(AudioFoleyAction action)
            => TryEmitAt(action, EmissionPosition);

        public bool TryEmitAt(AudioFoleyAction action, Vector3 worldPosition)
        {
            if (_audioService == null || _profile == null)
                return false;

            if (!_profile.TryResolve(action, out var eventId))
                return false;

            return _audioService.TryPlayOneShot(eventId, worldPosition);
        }

        // Parameterless wrappers are intentionally provided for UnityEvent/animation-event wiring.
        public void EmitPickup() => TryEmit(AudioFoleyAction.Pickup);
        public void EmitDrop() => TryEmit(AudioFoleyAction.Drop);
        public void EmitImpact() => TryEmit(AudioFoleyAction.Impact);
        public void EmitHandle() => TryEmit(AudioFoleyAction.Handle);
        public void EmitOpen() => TryEmit(AudioFoleyAction.Open);
        public void EmitClose() => TryEmit(AudioFoleyAction.Close);
        public void EmitTighten() => TryEmit(AudioFoleyAction.Tighten);
        public void EmitCreak() => TryEmit(AudioFoleyAction.Creak);
        public void EmitTension() => TryEmit(AudioFoleyAction.Tension);
        public void EmitTensionRelease() => TryEmit(AudioFoleyAction.TensionRelease);
        public void EmitBreak() => TryEmit(AudioFoleyAction.Break);
        public void EmitChop() => TryEmit(AudioFoleyAction.Chop);
        public void EmitScrape() => TryEmit(AudioFoleyAction.Scrape);
        public void EmitPour() => TryEmit(AudioFoleyAction.Pour);
        public void EmitSplashSmall() => TryEmit(AudioFoleyAction.SplashSmall);
        public void EmitSplashLarge() => TryEmit(AudioFoleyAction.SplashLarge);
        public void EmitFlap() => TryEmit(AudioFoleyAction.Flap);
        public void EmitIgnite() => TryEmit(AudioFoleyAction.Ignite);
        public void EmitExtinguish() => TryEmit(AudioFoleyAction.Extinguish);
        public void EmitAddFuel() => TryEmit(AudioFoleyAction.AddFuel);
        public void EmitUse() => TryEmit(AudioFoleyAction.Use);
    }
}
