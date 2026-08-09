using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

// Builds the first real two-player co-op scene (CoopGame.unity) -> ProjektOenApp-coop.apk
public static class CoopGameSetup
{
    const string SceneDir = "Assets/Scenes";
    const string ScenePath = SceneDir + "/CoopGame.unity";
    const string PlayerPrefabPath = "Assets/Prefabs/PlayerRig.prefab";
    const string BoxPrefabPath = "Assets/Prefabs/CoopBox.prefab";
    const string HandshakePrefabPath = "Assets/Prefabs/Handshake.prefab";
    const string Apk = "Build/ProjektOenApp-coop.apk";

    static void Log(string s, string r) => Debug.Log($"[OEN-SETUP] {s}: {r}");
    static void Fail(string s, string w) => Debug.LogError($"[OEN-SETUP] {s}: FEJL - {w}");

    public static void SetupAndBuild() { Setup(); Build(); }

    public static void Setup()
    {
        var player = AssetDatabase.LoadAssetAtPath<GameObject>(PlayerPrefabPath);
        var boxg = AssetDatabase.LoadAssetAtPath<GameObject>(BoxPrefabPath);
        if (player == null) Fail("Setup", "PlayerRig.prefab ikke fundet");
        if (boxg == null) Fail("Setup", "CoopBox.prefab ikke fundet");
        var hs = CreateHandshakePrefab();
        CreateScene(player, boxg, hs);
        AssetDatabase.SaveAssets();
        Log("Setup", "faerdig");
    }

    static GameObject CreateHandshakePrefab()
    {
        var noType = FindType("Fusion.NetworkObject");
        var hsType = FindType("ProjectOen.Networking.HandshakeExchange");
        if (noType == null || hsType == null) { Fail("CreateHandshakePrefab", "NetworkObject/HandshakeExchange ikke fundet"); return null; }
        if (!Directory.Exists("Assets/Prefabs")) Directory.CreateDirectory("Assets/Prefabs");
        var root = new GameObject("Handshake");
        root.AddComponent(noType);
        root.AddComponent(hsType);
        var prefab = PrefabUtility.SaveAsPrefabAsset(root, HandshakePrefabPath);
        UnityEngine.Object.DestroyImmediate(root);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Log("CreateHandshakePrefab", HandshakePrefabPath + " (NetworkObject + HandshakeExchange)");
        return prefab;
    }

    static void CreateScene(GameObject playerPrefab, GameObject boxPrefab, GameObject handshakePrefab)
    {
        if (!Directory.Exists(SceneDir)) Directory.CreateDirectory(SceneDir);
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        var origin = new GameObject("XR Origin");

        var cameraGo = new GameObject("Main Camera");
        cameraGo.transform.SetParent(origin.transform, false);
        cameraGo.transform.localPosition = new Vector3(0f, 1.6f, 0f);
        cameraGo.tag = "MainCamera";
        var cam = cameraGo.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.05f, 0.07f, 0.11f);
        cam.nearClipPlane = 0.01f;
        var driver = FindType("UnityEngine.InputSystem.XR.TrackedPoseDriver");
        if (driver != null) cameraGo.AddComponent(driver);

        // Local pose sources, driven from live XR devices (M0a's proven path).
        var headSrc = new GameObject("HeadSrc").transform; headSrc.SetParent(origin.transform, false);
        var leftSrc = new GameObject("LeftSrc").transform; leftSrc.SetParent(origin.transform, false);
        var rightSrc = new GameObject("RightSrc").transform; rightSrc.SetParent(origin.transform, false);

        var headRigType = FindType("M0bHeadRig");
        if (headRigType == null) Fail("CreateScene", "M0bHeadRig ikke fundet");
        else
        {
            var rigGo = new GameObject("XrDeviceRig");
            var so = new SerializedObject(rigGo.AddComponent(headRigType));
            SetRef(so, "_head", headSrc); SetRef(so, "_left", leftSrc); SetRef(so, "_right", rightSrc);
            so.ApplyModifiedProperties();
            Log("CreateScene", "M0bHeadRig wired");
        }

        // Simple ground so the space reads as a room.
        var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "Floor";
        floor.transform.localScale = new Vector3(1.2f, 1f, 1.2f);
        var fr = floor.GetComponent<Renderer>();
        if (fr != null) fr.sharedMaterial.color = new Color(0.18f, 0.20f, 0.24f);

        var light = new GameObject("Directional Light").AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.1f;
        light.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        var noType = FindType("Fusion.NetworkObject");
        var gameType = FindType("CoopGame");
        if (gameType == null) Fail("CreateScene", "CoopGame ikke fundet");
        else
        {
            var go = new GameObject("CoopGame");
            var so = new SerializedObject(go.AddComponent(gameType));
            if (playerPrefab != null) SetRef(so, "_playerPrefab", playerPrefab.GetComponent(noType));
            if (boxPrefab != null) SetRef(so, "_boxPrefab", boxPrefab.GetComponent(noType));
            if (handshakePrefab != null) SetRef(so, "_handshakePrefab", handshakePrefab.GetComponent(noType));
            SetRef(so, "_head", headSrc); SetRef(so, "_left", leftSrc); SetRef(so, "_right", rightSrc);
            so.ApplyModifiedProperties();
            Log("CreateScene", "CoopGame wired (prefabs + XR-kilder)");
        }

        EditorSceneManager.SaveScene(scene, ScenePath);
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        Log("Scene", ScenePath + " oprettet + i build list");
    }

    static void SetRef(SerializedObject so, string prop, UnityEngine.Object val)
    {
        var p = so.FindProperty(prop);
        if (p != null) p.objectReferenceValue = val; else Fail("SetRef", prop + " ikke fundet");
    }

    public static void Build()
    {
        var apk = Path.GetFullPath(Apk);
        Directory.CreateDirectory(Path.GetDirectoryName(apk));
        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Android, BuildTarget.Android);
        var opts = new BuildPlayerOptions { scenes = new[] { ScenePath }, locationPathName = apk, target = BuildTarget.Android, targetGroup = BuildTargetGroup.Android, options = BuildOptions.None };
        var report = BuildPipeline.BuildPlayer(opts);
        if (report.summary.result != BuildResult.Succeeded) { Log("Build", "retry"); report = BuildPipeline.BuildPlayer(opts); }
        if (report.summary.result == BuildResult.Succeeded) Log("Build", "OK -> " + apk + " (" + (report.summary.totalSize / 1024 / 1024) + " MB)");
        else { Fail("Build", report.summary.result + ", " + report.summary.totalErrors + " fejl"); EditorApplication.Exit(1); }
    }

    static Type FindType(string fullName) =>
        AppDomain.CurrentDomain.GetAssemblies().Select(a => { try { return a.GetType(fullName); } catch { return null; } }).FirstOrDefault(t => t != null);
}
