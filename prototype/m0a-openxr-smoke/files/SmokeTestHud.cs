// M0a smoke test — PROJECT ØEN
//
// Formål: besvare ét spørgsmål på Quest 1 — starter og tracker OpenXR?
// Der er ikke projektkode. Den skal ikke ind i Assets/ProjectOen/.
//
// Verifikationsstatus: skrevet uden Unity Editor i miljøet. Den er IKKE kompileret.
// API'erne (UnityEngine.XR.InputDevices, CommonUsages) er stabile på tværs af
// Unity 2019-6, men rapportér straks hvis Editoren melder en compile-fejl.
//
// Der er to uafhængige aflæsninger med vilje: en HUD i verden og en logcat-linje
// hvert sekund. Renderer HUD'en ikke, har du stadig svaret i loggen.

using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.XR;

public class SmokeTestHud : MonoBehaviour
{
    const string LogTag = "OenM0a";

    TextMesh _text;
    Transform _worldAnchor;
    Transform _leftHand;
    Transform _rightHand;

    float _fpsAccum;
    int _fpsFrames;
    float _fpsTimer;
    float _fps;
    float _logTimer;

    void Start()
    {
        Application.targetFrameRate = 72;

        // Referencekube: står stille i verden. Følger den med hovedet,
        // er der ingen positionel tracking. Det er selve testen.
        _worldAnchor = BuildCube("WorldAnchor", new Color(0.7f, 0.7f, 0.7f), 0.25f).transform;
        _worldAnchor.position = new Vector3(0f, 1.0f, 2.0f);

        _leftHand = BuildCube("LeftHand", new Color(0.2f, 0.5f, 1.0f), 0.06f).transform;
        _rightHand = BuildCube("RightHand", new Color(1.0f, 0.5f, 0.2f), 0.06f).transform;

        BuildHud();
        Debug.Log($"[{LogTag}] Start. device={SystemInfo.deviceModel} gfx={SystemInfo.graphicsDeviceType} " +
                  $"unity={Application.unityVersion}");
    }

    GameObject BuildCube(string name, Color color, float size)
    {
        var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
        go.name = name;
        go.transform.localScale = Vector3.one * size;
        Destroy(go.GetComponent<Collider>());
        var mat = go.GetComponent<Renderer>().material;
        mat.color = color;
        return go;
    }

    void BuildHud()
    {
        var go = new GameObject("Hud");
        go.transform.SetParent(transform, false);
        go.transform.position = new Vector3(0f, 1.4f, 1.6f);

        _text = go.AddComponent<TextMesh>();
        _text.characterSize = 0.06f;
        _text.fontSize = 96;
        _text.anchor = TextAnchor.UpperLeft;
        _text.alignment = TextAlignment.Left;
        _text.color = Color.white;

        // Indbygget font. Navnet ændrede sig i nyere Unity-versioner, så vi prøver begge.
        var font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")
                   ?? Resources.GetBuiltinResource<Font>("Arial.ttf");
        if (font != null)
        {
            _text.font = font;
            _text.GetComponent<Renderer>().material = font.material;
        }
        else
        {
            // Ingen font: HUD'en er tabt, men logcat-sporet virker stadig.
            Debug.LogWarning($"[{LogTag}] Ingen indbygget font fundet — brug adb logcat.");
        }
    }

    void Update()
    {
        _fpsAccum += Time.unscaledDeltaTime;
        _fpsFrames++;
        _fpsTimer += Time.unscaledDeltaTime;
        if (_fpsTimer >= 0.5f)
        {
            _fps = _fpsFrames / Mathf.Max(_fpsAccum, 0.0001f);
            _fpsAccum = 0f;
            _fpsFrames = 0;
            _fpsTimer = 0f;
        }

        var head = Read(XRNode.Head);
        var left = Read(XRNode.LeftHand);
        var right = Read(XRNode.RightHand);

        if (left.tracked) _leftHand.SetPositionAndRotation(left.position, left.rotation);
        if (right.tracked) _rightHand.SetPositionAndRotation(right.position, right.rotation);

        var report = Report(head, left, right);
        if (_text != null)
        {
            _text.text = report;
            // Hold HUD'en foran spilleren uden at den klistrer til hovedrotationen.
            var cam = Camera.main;
            if (cam != null)
            {
                var flat = cam.transform.forward;
                flat.y = 0f;
                if (flat.sqrMagnitude > 0.001f)
                {
                    _text.transform.position = cam.transform.position + flat.normalized * 1.6f + Vector3.up * 0.15f;
                    _text.transform.rotation = Quaternion.LookRotation(flat.normalized);
                }
            }
        }

        _logTimer += Time.unscaledDeltaTime;
        if (_logTimer >= 1f)
        {
            _logTimer = 0f;
            Debug.Log($"[{LogTag}] {report.Replace('\n', '|')}");
        }
    }

    struct NodeState
    {
        public bool valid;
        public bool tracked;
        public Vector3 position;
        public Quaternion rotation;
    }

    static readonly List<InputDevice> Devices = new List<InputDevice>();

    NodeState Read(XRNode node)
    {
        var state = new NodeState { rotation = Quaternion.identity };
        Devices.Clear();
        InputDevices.GetDevicesAtXRNode(node, Devices);
        if (Devices.Count == 0) return state;

        var device = Devices[0];
        state.valid = device.isValid;
        if (device.TryGetFeatureValue(CommonUsages.devicePosition, out var pos))
        {
            state.position = pos;
            state.tracked = true;
        }
        if (device.TryGetFeatureValue(CommonUsages.deviceRotation, out var rot))
        {
            state.rotation = rot;
        }
        return state;
    }

    string Report(NodeState head, NodeState left, NodeState right)
    {
        var sb = new StringBuilder();
        sb.Append("PROJECT OEN — M0a\n");
        sb.Append($"device: {SystemInfo.deviceModel}\n");
        sb.Append($"gfx:    {SystemInfo.graphicsDeviceType}\n");
        sb.Append($"unity:  {Application.unityVersion}\n");
        sb.Append($"fps:    {_fps:0.0}\n");
        sb.Append($"head:   valid={head.valid} tracked={head.tracked} pos={Fmt(head.position)}\n");
        sb.Append($"left:   valid={left.valid} tracked={left.tracked}\n");
        sb.Append($"right:  valid={right.valid} tracked={right.tracked}\n");
        sb.Append(head.tracked
            ? "TRACKING: JA — den graa kube skal blive staaende naar du gaar"
            : "TRACKING: NEJ — ingen positionsdata fra hovedet");
        return sb.ToString();
    }

    static string Fmt(Vector3 v) => $"({v.x:0.00},{v.y:0.00},{v.z:0.00})";
}
