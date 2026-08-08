// UNVERIFIED-IN-SANDBOX
// Ikke kompileret. Ingen Unity Editor i skrivemiljøet.
//
// Formål: gøre hele M0a-opsætningen headless, så Anders kører én kommando i
// stedet for at klikke gennem tyve trin. Hvert trin logger sit resultat, så en
// fejl kan isoleres uden at gætte.
//
// XR-konfigurationen er den skrøbelige del: API'et har flyttet sig mellem
// Unity-versioner. Features slås derfor til ved NAVNEMATCH frem for ved hårde
// typereferencer — så scriptet kompilerer, selv hvis en type er flyttet, og
// fortæller hvad den fandt i stedet for at fejle ved compile.

using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

public static class M0aBuild
{
    const string SceneDir = "Assets/Scenes";
    const string ScenePath = SceneDir + "/Smoke.unity";

    static void Log(string step, string result) => Debug.Log($"[M0A-SETUP] {step}: {result}");
    static void Fail(string step, string why) => Debug.LogError($"[M0A-SETUP] {step}: FEJL — {why}");

    /// <summary>Kaldes af Build-M0a.ps1 via -executeMethod.</summary>
    public static void Configure()
    {
        ConfigurePlayer();
        ConfigureXR();
        CreateScene();
        AssetDatabase.SaveAssets();
        Log("Configure", "færdig");
    }

    public static void ConfigureAndBuild()
    {
        Configure();
        Build();
    }

    static void ConfigurePlayer()
    {
        PlayerSettings.productName = "OenM0aSmoke";
        PlayerSettings.companyName = "ProjectOen";
        PlayerSettings.applicationIdentifier = "com.projectoen.m0asmoke";
        PlayerSettings.colorSpace = ColorSpace.Linear;

        PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
        PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel29;

        // Vulkan først, GLES3 som fallback. Rækkefølgen ER testen i OQ-003:
        // starter appen sort på Quest 1, byttes de om.
        PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
        PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[]
        {
            GraphicsDeviceType.Vulkan,
            GraphicsDeviceType.OpenGLES3,
        });

        Log("PlayerSettings", "IL2CPP/ARM64, minSdk 29, Linear, Vulkan→GLES3");
    }

    static void ConfigureXR()
    {
        // XR Plug-in Management og OpenXR-loaderen slås til via reflection, fordi
        // typenavnene og assembly-placeringen har ændret sig mellem versioner.
        // Et navnematch der fejler giver en tydelig besked; en hård typereference
        // ville give en compile-fejl og stoppe hele scriptet.
        try
        {
            var mgmtType = FindType("UnityEditor.XR.Management.XRGeneralSettingsPerBuildTarget");
            var settingsKeyType = FindType("UnityEngine.XR.Management.XRGeneralSettings");
            if (mgmtType == null || settingsKeyType == null)
            {
                Fail("XR Management", "pakken com.unity.xr.management blev ikke fundet. Er manifest.json korrekt?");
                return;
            }

            var key = (string)settingsKeyType.GetField("k_SettingsKey").GetValue(null);
            object perTarget = null;
            var tryGet = typeof(EditorBuildSettings).GetMethods()
                .First(m => m.Name == "TryGetConfigObject" && m.IsGenericMethod)
                .MakeGenericMethod(mgmtType);
            var args = new object[] { key, null };
            var found = (bool)tryGet.Invoke(null, args);
            perTarget = args[1];

            if (!found || perTarget == null)
            {
                var asset = ScriptableObject.CreateInstance(mgmtType);
                if (!Directory.Exists("Assets/XR")) Directory.CreateDirectory("Assets/XR");
                AssetDatabase.CreateAsset(asset, "Assets/XR/XRGeneralSettingsPerBuildTarget.asset");
                EditorBuildSettings.AddConfigObject(key, asset, true);
                perTarget = asset;
                Log("XR Management", "oprettede settings-asset");
            }

            var getOrCreate = mgmtType.GetMethod("GetOrCreate", new[] { typeof(BuildTargetGroup) });
            var general = getOrCreate.Invoke(perTarget, new object[] { BuildTargetGroup.Android });

            var managerProp = general.GetType().GetProperty("Manager")
                              ?? general.GetType().GetProperty("AssignedSettings");
            var manager = managerProp.GetValue(general);

            var loaderType = FindType("UnityEngine.XR.OpenXR.OpenXRLoader");
            if (loaderType == null)
            {
                Fail("OpenXR", "com.unity.xr.openxr blev ikke fundet.");
                return;
            }

            var loader = ScriptableObject.CreateInstance(loaderType);
            AssetDatabase.CreateAsset(loader, "Assets/XR/OpenXRLoader.asset");

            var tryAdd = manager.GetType().GetMethod("TryAddLoader");
            if (tryAdd != null)
            {
                var ok = (bool)tryAdd.Invoke(manager, new object[] { loader, -1 });
                Log("OpenXR loader", ok ? "tilføjet til Android" : "kunne ikke tilføjes");
            }

            EditorUtility.SetDirty(manager);
            EnableOpenXRFeatures();
        }
        catch (Exception ex)
        {
            Fail("XR-opsætning", ex.Message + "\nSlå den til manuelt: Project Settings → XR Plug-in Management → Android → OpenXR.");
        }
    }

    static void EnableOpenXRFeatures()
    {
        var settingsType = FindType("UnityEngine.XR.OpenXR.OpenXRSettings");
        if (settingsType == null) { Fail("OpenXR features", "OpenXRSettings ikke fundet."); return; }

        var getSettings = settingsType.GetMethod("GetSettingsForBuildTargetGroup");
        var settings = getSettings?.Invoke(null, new object[] { BuildTargetGroup.Android });
        if (settings == null) { Fail("OpenXR features", "kunne ikke hente Android-settings."); return; }

        var getFeatures = settings.GetType().GetMethod("GetFeatures", Type.EmptyTypes);
        var features = getFeatures?.Invoke(settings, null) as Array;
        if (features == null) { Fail("OpenXR features", "GetFeatures() gav intet."); return; }

        // Præcis to features er nødvendige for M0a: Quest-support (manifest og
        // runtime) og Oculus Touch-profilen (controllere). Alt andet er variabler,
        // vi ikke vil have med i en test der skal isolere én ting.
        string[] wanted = { "MetaQuest", "OculusTouch" };
        foreach (var feature in features)
        {
            var name = feature.GetType().Name;
            if (!wanted.Any(w => name.IndexOf(w, StringComparison.OrdinalIgnoreCase) >= 0)) continue;

            var enabled = feature.GetType().GetProperty("enabled");
            enabled?.SetValue(feature, true);
            EditorUtility.SetDirty((UnityEngine.Object)feature);
            Log("OpenXR feature", $"{name} slået til");
        }
    }

    static void CreateScene()
    {
        if (!Directory.Exists(SceneDir)) Directory.CreateDirectory(SceneDir);

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        // Bevidst UDEN XR Interaction Toolkit: M0a skal svare på ét spørgsmål, og
        // hver ekstra pakke er en variabel mere i den fejlsøgning. Kameraets pose
        // drives af Input Systems TrackedPoseDriver, som virker med enhver XR-provider.
        var origin = new GameObject("XR Origin");
        var cameraGo = new GameObject("Main Camera");
        cameraGo.transform.SetParent(origin.transform, false);
        cameraGo.transform.localPosition = new Vector3(0f, 1.6f, 0f);
        cameraGo.tag = "MainCamera";

        var cam = cameraGo.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.05f, 0.06f, 0.09f);
        cam.nearClipPlane = 0.01f;

        var driverType = FindType("UnityEngine.InputSystem.XR.TrackedPoseDriver");
        if (driverType != null) cameraGo.AddComponent(driverType);
        else Fail("TrackedPoseDriver", "Input System ikke fundet — kameraet vil ikke tracke.");

        var smokeType = FindType("SmokeTestHud");
        if (smokeType != null) new GameObject("SmokeTest").AddComponent(smokeType);
        else Fail("SmokeTestHud", "scriptet blev ikke kopieret til Assets/Scripts/.");

        var light = new GameObject("Directional Light").AddComponent<Light>();
        light.type = LightType.Directional;
        light.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        EditorSceneManager.SaveScene(scene, ScenePath);
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        Log("Scene", ScenePath + " oprettet og lagt i build list");
    }

    public static void Build()
    {
        var outDir = Path.GetFullPath("Build");
        Directory.CreateDirectory(outDir);
        var apk = Path.Combine(outDir, "OenM0aSmoke.apk");

        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Android, BuildTarget.Android);

        var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
        {
            scenes = new[] { ScenePath },
            locationPathName = apk,
            target = BuildTarget.Android,
            targetGroup = BuildTargetGroup.Android,
            options = BuildOptions.None,
        });

        if (report.summary.result == BuildResult.Succeeded)
        {
            Log("Build", $"OK → {apk} ({report.summary.totalSize / 1024 / 1024} MB)");
        }
        else
        {
            Fail("Build", $"{report.summary.result}, {report.summary.totalErrors} fejl");
            EditorApplication.Exit(1);
        }
    }

    static Type FindType(string fullName) =>
        AppDomain.CurrentDomain.GetAssemblies()
            .Select(a => { try { return a.GetType(fullName); } catch { return null; } })
            .FirstOrDefault(t => t != null);
}
