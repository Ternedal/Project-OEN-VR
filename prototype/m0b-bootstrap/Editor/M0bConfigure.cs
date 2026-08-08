#nullable enable

using System;
using System.Linq;
using UnityEditor;
using UnityEditor.XR.Management;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.XR.Management;
using UnityEngine.XR.OpenXR;

// M0b projekt-konfiguration. Genbruger PRÆCIS den XR-opsætning der blev verificeret
// on-device i M0a (Quest 2: OpenXR immersivt, head-tracking, 72 fps, Vulkan) — direkte,
// compile-tjekkede XR Management/OpenXR-kald, ikke reflection. Sætter kun projektet op;
// scene/gameplay bygges bagefter. Fusion/netværk kræver Photon-SDK importeret separat.
public static class M0bConfigure
{
    static void Log(string step, string result) => Debug.Log($"[M0B-SETUP] {step}: {result}");
    static void Fail(string step, string why) => Debug.LogError($"[M0B-SETUP] {step}: FEJL — {why}");

    /// <summary>Kaldes af Bootstrap-M0b.ps1 via -executeMethod.</summary>
    public static void Configure()
    {
        ConfigurePlayer();
        ConfigureXR();
        AssetDatabase.SaveAssets();
        Log("Configure", "færdig");
    }

    static void ConfigurePlayer()
    {
        PlayerSettings.productName = "Projekt Oen";
        PlayerSettings.companyName = "ProjectOen";
        PlayerSettings.applicationIdentifier = "com.projectoen.oen";
        PlayerSettings.colorSpace = ColorSpace.Linear;
        PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
        PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel29;
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
            }

            var manager = general.Manager;
            if (manager == null)
            {
                manager = ScriptableObject.CreateInstance<XRManagerSettings>();
                manager.name = "XR Manager";
                general.Manager = manager;
                AssetDatabase.AddObjectToAsset(manager, perTarget);
            }

            if (!manager.activeLoaders.Any(l => l is OpenXRLoader))
            {
                var loader = ScriptableObject.CreateInstance<OpenXRLoader>();
                loader.name = "OpenXR Loader";
                AssetDatabase.AddObjectToAsset(loader, perTarget);
                var added = manager.TryAddLoader(loader);
                Log("OpenXR loader", added ? "tilføjet som aktiv loader for Android" : "TryAddLoader gav false");
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
            Fail("XR-opsætning", ex.GetType().Name + ": " + ex.Message);
        }
    }

    static XRGeneralSettingsPerBuildTarget GetOrCreatePerBuildTarget()
    {
        XRGeneralSettingsPerBuildTarget perTarget;
        EditorBuildSettings.TryGetConfigObject(XRGeneralSettings.k_SettingsKey, out perTarget);
        if (perTarget == null)
        {
            perTarget = ScriptableObject.CreateInstance<XRGeneralSettingsPerBuildTarget>();
            if (!System.IO.Directory.Exists("Assets/XR")) System.IO.Directory.CreateDirectory("Assets/XR");
            AssetDatabase.CreateAsset(perTarget, "Assets/XR/XRGeneralSettings.asset");
            EditorBuildSettings.AddConfigObject(XRGeneralSettings.k_SettingsKey, perTarget, true);
        }
        return perTarget;
    }

    static void EnableOpenXRFeatures()
    {
        try { UnityEditor.XR.OpenXR.Features.FeatureHelpers.RefreshFeatures(BuildTargetGroup.Android); }
        catch (Exception ex) { Log("OpenXR features", "RefreshFeatures: " + ex.Message); }

        var settings = OpenXRSettings.GetSettingsForBuildTargetGroup(BuildTargetGroup.Android);
        if (settings == null) { Fail("OpenXR features", "OpenXR-settings for Android er null."); return; }

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
}
