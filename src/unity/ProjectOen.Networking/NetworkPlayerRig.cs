// UNVERIFIED-IN-SANDBOX
// Ikke kompileret. Intet Fusion 2 SDK i skrivemiljøet.
// Antagelser: NetworkBehaviour, [Networked] Vector3/Quaternion, Object.HasInputAuthority,
// NetworkTransform eller manuel interpolation. Hvis NetworkTransform bruges i stedet,
// forsvinder halvdelen af denne fil - det afgøres i M0b.

using Fusion;
using UnityEngine;

namespace ProjectOen.Networking
{
    /// <summary>
    /// docs/07 §3 og §6: hver klient ejer sin egen head/hand-pose. Ingen anden klient
    /// må skrive den. Interpolation skjuler jitter på den fjerne avatar.
    ///
    /// Poser er BEVIDST ikke save-state. docs/06 §7: PlayerState har authority for
    /// logiske statusværdier, ikke rå pose - en pose i et checkpoint ville være
    /// meningsløs efter en rekalibrering.
    /// </summary>
    public sealed class NetworkPlayerRig : NetworkBehaviour
    {
        [SerializeField] Transform _head = null!;
        [SerializeField] Transform _leftHand = null!;
        [SerializeField] Transform _rightHand = null!;

        [SerializeField] Transform _localHead = null!;
        [SerializeField] Transform _localLeftHand = null!;
        [SerializeField] Transform _localRightHand = null!;

        [SerializeField] float _remoteInterpolation = 12f;

        [Networked] Vector3 HeadPosition { get; set; }
        [Networked] Quaternion HeadRotation { get; set; }
        [Networked] Vector3 LeftPosition { get; set; }
        [Networked] Quaternion LeftRotation { get; set; }
        [Networked] Vector3 RightPosition { get; set; }
        [Networked] Quaternion RightRotation { get; set; }

        public int PlayerSlot { get; private set; }

        public override void Spawned() => PlayerSlot = Object.InputAuthority.PlayerId % 2;

        public override void FixedUpdateNetwork()
        {
            if (!Object.HasInputAuthority) return;

            // Kun ejeren skriver sin egen pose.
            HeadPosition = _localHead.position;
            HeadRotation = _localHead.rotation;
            LeftPosition = _localLeftHand.position;
            LeftRotation = _localLeftHand.rotation;
            RightPosition = _localRightHand.position;
            RightRotation = _localRightHand.rotation;
        }

        public override void Render()
        {
            if (Object.HasInputAuthority)
            {
                // Lokalt greb skal svare samme frame (docs/07 §9). Ingen interpolation.
                Apply(_head, _localHead.position, _localHead.rotation, 1f);
                Apply(_leftHand, _localLeftHand.position, _localLeftHand.rotation, 1f);
                Apply(_rightHand, _localRightHand.position, _localRightHand.rotation, 1f);
                return;
            }

            var t = 1f - Mathf.Exp(-_remoteInterpolation * Time.deltaTime);
            Apply(_head, HeadPosition, HeadRotation, t);
            Apply(_leftHand, LeftPosition, LeftRotation, t);
            Apply(_rightHand, RightPosition, RightRotation, t);
        }

        static void Apply(Transform target, Vector3 position, Quaternion rotation, float t)
        {
            target.position = Vector3.Lerp(target.position, position, t);
            target.rotation = Quaternion.Slerp(target.rotation, rotation, t);
        }
    }
}
