using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

// M0b increment 4: drive three transforms from the LIVE XR devices (head/left/right),
// using the exact InputDevices API that M0a proved on this Quest rig. Robust and
// action-binding-free — unlike a bare AddComponent<TrackedPoseDriver>(), which gets no
// input bindings and writes a zero pose (that was the (0,0,0) in increment 3).
//
// The three targets are the local pose sources bound into NetworkPlayerRig via
// BindLocalRig(), so the [Networked] head/hand pose becomes real, non-zero, and moves.
public class M0bHeadRig : MonoBehaviour
{
    [SerializeField] Transform _head = null;
    [SerializeField] Transform _left = null;
    [SerializeField] Transform _right = null;

    static readonly List<InputDevice> _devs = new List<InputDevice>();

    void Update()
    {
        Drive(_head, XRNode.Head);
        Drive(_left, XRNode.LeftHand);
        Drive(_right, XRNode.RightHand);
    }

    static void Drive(Transform t, XRNode node)
    {
        if (t == null) return;
        _devs.Clear();
        InputDevices.GetDevicesAtXRNode(node, _devs);
        if (_devs.Count == 0) return;
        var d = _devs[0];
        if (d.TryGetFeatureValue(CommonUsages.devicePosition, out var pos)) t.localPosition = pos;
        if (d.TryGetFeatureValue(CommonUsages.deviceRotation, out var rot)) t.localRotation = rot;
    }
}
