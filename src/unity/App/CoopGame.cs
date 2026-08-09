using System.Collections.Generic;
using System.Threading.Tasks;
using Fusion;
using ProjectOen.Core.Networking;
using ProjectOen.Networking;
using UnityEngine;
using UnityEngine.XR;

// M0b: first real two-player co-op scene.
// Both Quests launch this same build, auto-join the same Shared session, and each spawns its
// OWN InputDevices-driven player rig (head + two hands). Every client sees every other client's
// rig via the [Networked] pose on NetworkPlayerRig. The shared box is spawned once by the
// Shared-mode master client; grabbing it (grip button) requests state authority and submits the
// hand target so CoopSolver moves it identically for both players.
public class CoopGame : MonoBehaviour
{
    [SerializeField] NetworkObject _playerPrefab;
    [SerializeField] NetworkObject _boxPrefab;
    [SerializeField] NetworkObject _handshakePrefab;
    [SerializeField] Transform _head;
    [SerializeField] Transform _left;
    [SerializeField] Transform _right;

    [Header("Build identity (handshake-gate, docs/07 §5)")]
    [SerializeField] string _gameVersion = "0.1.0";
    [SerializeField] int _protocolVersion = 1;
    [SerializeField] string _contentHash = "m0b-dev";
    [SerializeField] int _saveSchemaVersion = 1;
    [SerializeField] string _platformProfile = "Q2_BASE";

    // Log-only som default: en fejl i gaten må ikke kunne blokere co-op-testen.
    // Sæt true for at teste den rigtige afvisning (COMPAT-002).
    [SerializeField] bool _enforceHandshakeGate = false;

    NetworkRunner _runner;
    NetworkedCoopObject _box;
    HandshakeExchange _handshake;
    int _slot;
    bool _gateLogged;
    static readonly List<InputDevice> _devs = new List<InputDevice>();

    BuildIdentity LocalIdentity() => new BuildIdentity(
        _gameVersion, _protocolVersion, _contentHash, _saveSchemaVersion, _platformProfile);

    bool Rejected() => _handshake != null && _handshake.Result != null && !_handshake.Result.Accepted;

    async void Start()
    {
        Debug.Log("[OEN-COOP] starting Shared session 'oen-coop'...");
        _runner = gameObject.AddComponent<NetworkRunner>();
        _runner.ProvideInput = false;
        var result = await _runner.StartGame(new StartGameArgs
        {
            GameMode = GameMode.Shared,
            SessionName = "oen-coop",
            PlayerCount = 2,
        });
        if (!result.Ok) { Debug.LogError("[OEN-COOP] StartGame FAILED: " + result.ShutdownReason); return; }
        _slot = _runner.LocalPlayer.PlayerId % 2;
        Debug.Log("[OEN-COOP] connected. LocalPlayer=" + _runner.LocalPlayer + " slot=" + _slot + " master=" + _runner.IsSharedModeMasterClient);

        // Handshake FØR rig/box, så en inkompatibel klient kan afvises før spawn (docs/07 §5).
        if (_handshakePrefab != null)
        {
            var hsObj = _runner.Spawn(_handshakePrefab, Vector3.zero, Quaternion.identity, _runner.LocalPlayer,
                (r, obj) => { var hs = obj.GetComponent<HandshakeExchange>(); if (hs != null) hs.Configure(LocalIdentity()); });
            _handshake = hsObj != null ? hsObj.GetComponent<HandshakeExchange>() : null;
            Debug.Log("[OEN-COOP] handshake spawned=" + (_handshake != null) + " identity=" + _gameVersion + "/p" + _protocolVersion + "/" + _contentHash);
        }
        else Debug.LogWarning("[OEN-COOP] intet handshake-prefab wiret - gaten er inaktiv");

        // Giv en evt. peer et kort vindue til at annoncere sig, før vi spawner.
        for (int i = 0; i < 20 && Rejected() == false && _handshake != null && _handshake.Result == null; i++)
            await Task.Delay(100);

        if (_enforceHandshakeGate && Rejected())
        {
            var r = _handshake.Result;
            Debug.LogError("[OEN-COOP] AFVIST FOER SPAWN: " + r.Code + " - " + r.Message);
            await _runner.Shutdown();
            return;
        }

        var rig = _runner.Spawn(_playerPrefab, Vector3.zero, Quaternion.identity, _runner.LocalPlayer,
            (r, obj) => { var pr = obj.GetComponent<NetworkPlayerRig>(); if (pr != null) pr.BindLocalRig(_head, _left, _right); });
        Debug.Log("[OEN-COOP] my rig spawned inputAuth=" + (rig != null && rig.HasInputAuthority));

        if (_runner.IsSharedModeMasterClient)
        {
            var box = _runner.Spawn(_boxPrefab, new Vector3(0f, 1f, -1.5f), Quaternion.identity);
            _box = box != null ? box.GetComponent<NetworkedCoopObject>() : null;
            Debug.Log("[OEN-COOP] master spawned box stateAuth=" + (box != null && box.HasStateAuthority));
        }

        // Heartbeat so two-client presence is verifiable from logcat (players/rigs count).
        for (int i = 0; i < 40; i++)
        {
            await Task.Delay(1000);
            if (_runner == null || !_runner.IsRunning) return;
            if (_box == null) { var f = FindAnyObjectByType<NetworkedCoopObject>(); if (f != null) _box = f; }
            int players = 0; foreach (var _ in _runner.ActivePlayers) players++;
            int rigs = FindObjectsByType<NetworkPlayerRig>(FindObjectsSortMode.None).Length;
            string hp = _head != null ? _head.position.ToString("F2") : "?";
            string bph = _box != null ? _box.Phase.ToString() : "?";
            string bp = _box != null ? _box.transform.position.ToString("F2") : "?";
            string hs = _handshake == null ? "none" : (_handshake.Result == null ? "pending" : (_handshake.Result.Accepted ? "OK" : "REJECT:" + _handshake.Result.Code));
            if (!_gateLogged && _handshake != null && _handshake.Result != null)
            {
                _gateLogged = true;
                Debug.Log("[OEN-COOP] handshake resultat: " + _handshake.Result.Code + " - " + _handshake.Result.Message + " (enforce=" + _enforceHandshakeGate + ")");
            }
            Debug.Log($"[OEN-COOP] t={i} players={players} rigs={rigs} hs={hs} head={hp} boxPhase={bph} boxPos={bp}");
        }
        Debug.Log("[OEN-COOP] heartbeat done");
    }

    void Update()
    {
        if (_runner == null || !_runner.IsRunning) return;
        if (_box == null) { var f = FindAnyObjectByType<NetworkedCoopObject>(); if (f != null) _box = f; }
        if (_box == null) return;

        bool grip; Vector3 handPos;
        ReadGrip(out grip, out handPos);

        // Shared-mode grab: take state authority on the box, then submit the hand target.
        if (grip && !_box.Object.HasStateAuthority) _box.Object.RequestStateAuthority();
        if (_box.Object.HasStateAuthority) _box.SubmitHandTarget(_slot, handPos, grip);
    }

    void ReadGrip(out bool grip, out Vector3 handPos)
    {
        grip = false;
        handPos = _right != null ? _right.position : Vector3.zero;
        if (GripAt(XRNode.RightHand)) { grip = true; if (_right != null) handPos = _right.position; return; }
        if (GripAt(XRNode.LeftHand)) { grip = true; if (_left != null) handPos = _left.position; return; }
    }

    static bool GripAt(XRNode node)
    {
        _devs.Clear();
        InputDevices.GetDevicesAtXRNode(node, _devs);
        if (_devs.Count == 0) return false;
        return _devs[0].TryGetFeatureValue(CommonUsages.gripButton, out var g) && g;
    }
}
