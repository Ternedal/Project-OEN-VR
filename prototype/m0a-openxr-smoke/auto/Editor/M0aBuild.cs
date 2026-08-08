// M0a headless build/config for Project Øen.
//
// Formål: gøre hele M0a-opsætningen headless, så Anders kører én kommando i
// stedet for at klikke gennem tyve trin. Hvert trin logger sit resultat, så en
// fejl kan isoleres uden at gætte.
//
// XR-opsætningen bruger DIREKTE, compile-tjekkede kald mod XR Management +
// OpenXR (projektet er låst til Unity 6000.4.10f1 med com.unity.xr.management
// 4.5.0 og com.unity.xr.openxr 1.14.3). Den tidligere reflection-udgave kaldte
// et GetOrCreate(BuildTargetGroup), der ikke findes i 4.x, og oprettede aldrig
// XRManagerSettings når den var null → NullReference under opsætningen.

using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEditor.XR.Management;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using UnityEngine.XR.Management;
using UnityEngine.XR.OpenXR;

public static class M0aBuild
{
    const string SceneDir = "Assets/Scenes";
    const string ScenePath = SceneDir + "/Smoke.unity";
    const string XrAssetDir = "Assets/XR";
    const string XrAssetPath = XrAssetDir + "/XRGeneralSettings.asset";

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
        try
        {
            var perTarget = GetOrCreatePerBuildTarget();

            var general = perTarget.SettingsForBuildTarget(BuildTargetGroup.Android);
            if (general == null)
            {
                general = ScriptableObject.CreateInstance<XRGeneralSettings>();
                general.name = "Android XR Settings";
                perTarget.SetSettingsForBuildTarget(BuildTargetGroup.Android, general);
                AssetDatabase.AddObjectToAsset(general, perTarget);
                Log("XR Management", "oprettede Android XRGeneralSettings");
            }

            var manager = general.Manager;
            if (manager == null)
            {
                manager = ScriptableObject.CreateInstance<XRManagerSettings>();
                manager.name = "XR Manager";
                general.Manager = manager;
                AssetDatabase.AddObjectToAsset(manager, perTarget);
                Log("XR Management", "oprettede XRManagerSettings");
            }

            bool hasOpenXR = manager.activeLoaders.Any(l => l is OpenXRLoader);
            if (!hasOpenXR)
            {
                var loader = ScriptableObject.CreateInstance<OpenXRLoader>();
                loader.name = "OpenXR Loader";
                AssetDatabase.AddObjectToAsset(loader, perTarget);
                bool added = manager.TryAddLoader(loader);
                Log("OpenXR loader", added ? "tilføjet som aktiv loader for Android" : "TryAddLoader gav false");
            }
            else
            {
                Log("OpenXR loader", "allerede aktiv");
            }

            EditorUtility.SetDirty(perTarget);
            EditorUtility.SetDirty(general);
            EditorUtility.SetDirty(manager);
            AssetDatabase.SaveAssets();

            EnableOpenXRFeatures();
            Log("XR", "OpenXR sat op for Android");
        }
        catch (Exception ex)
        {
            Fail("XR-opsætning", ex.GetType().Name + ": " + ex.Message +
                "\nSlå den til manuelt: Project Settings → XR Plug-in Management → Android → OpenXR.");
        }
    }

    static XRGeneralSettingsPerBuildTarget GetOrCreatePerBuildTarget()
    {
        XRGeneralSettingsPerBuildTarget perTarget;
        EditorBuildSettings.TryGetConfigObject(XRGeneralSettings.k_SettingsKey, out perTarget);
        if (perTarget == null)
        {
            perTarget = ScriptableObject.CreateInstance<XRGeneralSettingsPerBuildTarget>();
            if (!Directory.Exists(XrAssetDir)) Directory.CreateDirectory(XrAssetDir);
            AssetDatabase.CreateAsset(perTarget, XrAssetPath);
            EditorBuildSettings.AddConfigObject(XRGeneralSettings.k_SettingsKey, perTarget, true);
            Log("XR Management", "oprettede per-build-target asset");
        }
        return perTarget;
    }

    static void EnableOpenXRFeatures()
    {
        // Præcis to features er nødvendige for M0a: Quest-support (manifest og
        // runtime) og Oculus Touch-profilen (controllere). Feature-typenavnene
        // matches, så en omdøbt feature ikke vælter opsætningen.
        // OpenXR instantierer sine per-buildtarget-settings dovent. RefreshFeatures
        // tvinger dem frem, ellers er GetSettingsForBuildTargetGroup null lige efter
        // loaderen er sat aktiv i samme session.
        try { UnityEditor.XR.OpenXR.Features.FeatureHelpers.RefreshFeatures(BuildTargetGroup.Android); }
        catch (Exception ex) { Log("OpenXR features", "RefreshFeatures: " + ex.Message); }

        var settings = OpenXRSettings.GetSettingsForBuildTargetGroup(BuildTargetGroup.Android);
        if (settings == null) { Fail("OpenXR features", "OpenXR-settings for Android er null selv efter RefreshFeatures."); return; }

        string[] wanted = { "MetaQuest", "OculusTouch" };
        foreach (var feature in settings.GetFeatures())
        {
            if (feature == null) continue;
            var name = feature.GetType().Name;
            if (!wanted.Any(w => name.IndexOf(w, StringComparison.OrdinalIgnoreCase) >= 0)) continue;
            feature.enabled = true;
            EditorUtility.SetDirty(feature);
            Log("OpenXR feature", name + " slået til");
        }
        EditorUtility.SetDirty(settings);
        AssetDatabase.SaveAssets();
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

        var opts = new BuildPlayerOptions
        {
            scenes = new[] { ScenePath },
            locationPathName = apk,
            target = BuildTarget.Android,
            targetGroup = BuildTargetGroup.Android,
            options = BuildOptions.None,
        };

        var report = BuildPipeline.BuildPlayer(opts);

        // Kendt OpenXR-quirk: første build efter aktivering melder somtider
        // "OpenXR Settings found in project but not yet loaded. Please build again."
        // Et andet forsøg i samme session bygger så igennem.
        if (report.summary.result != BuildResult.Succeeded)
        {
            Log("Build", "første forsøg fejlede — prøver igen (OpenXR-load quirk)");
            report = BuildPipeline.BuildPlayer(opts);
        }

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
