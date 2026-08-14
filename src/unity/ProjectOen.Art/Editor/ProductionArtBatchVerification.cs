using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Runs the complete production-art review pipeline in one real Unity Editor
    /// process and writes a machine-readable report beside Assets/.
    /// </summary>
    public static class ProductionArtBatchVerification
    {
        public const string ReportFileName = "ProjectOEN-ArtVerification.json";

        private static readonly string[] ReviewScenePaths =
        {
            "Assets/ProjectOEN/ProductionArt/Scenes/ProductionVfxShowcase.unity",
            "Assets/ProjectOEN/ProductionArt/Scenes/DiegeticUiArtShowcase.unity",
            "Assets/ProjectOEN/ProductionArt/Scenes/MaterialCalibrationShowcase.unity",
            "Assets/ProjectOEN/ProductionArt/Scenes/StateTransitionShowcase.unity",
            "Assets/ProjectOEN/ProductionArt/Scenes/HeroReadabilityShowcase.unity",
            "Assets/ProjectOEN/ProductionArt/Scenes/StormnattenArtShowcase.unity",
        };

        [Serializable]
        private sealed class VerificationStep
        {
            public string name;
            public string method;
            public string status;
            public long durationMs;
            public string error;
        }

        [Serializable]
        private sealed class VerificationReport
        {
            public string status;
            public string startedUtc;
            public string finishedUtc;
            public string unityVersion;
            public string projectPath;
            public int passed;
            public int failed;
            public List<VerificationStep> steps = new List<VerificationStep>();
        }

        [MenuItem("Project OEN/Art/Run Full On-Machine Verification")]
        public static void RunAll()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)?.FullName ?? Application.dataPath;
            var report = new VerificationReport
            {
                status = "RUNNING",
                startedUtc = DateTime.UtcNow.ToString("O"),
                finishedUtc = string.Empty,
                unityVersion = Application.unityVersion,
                projectPath = projectRoot,
            };

            try
            {
                RunStep("01 Build production-art prefabs", nameof(ProductionArtPrefabBuilder.BuildAll), ProductionArtPrefabBuilder.BuildAll, report);
                RunStep("02 Build canonical state appearance", nameof(ProductionArtStateAppearanceBuilder.BuildAll), ProductionArtStateAppearanceBuilder.BuildAll, report);
                RunStep("03 Audit canonical state appearance", nameof(ProductionArtStateAppearanceAudit.AuditAll), ProductionArtStateAppearanceAudit.AuditAll, report);
                RunStep("04 Build material calibration", nameof(ProductionArtMaterialCalibrationBuilder.BuildShowcase), ProductionArtMaterialCalibrationBuilder.BuildShowcase, report);
                RunStep("05 Audit material calibration", nameof(ProductionArtMaterialCalibrationAudit.AuditShowcase), ProductionArtMaterialCalibrationAudit.AuditShowcase, report);
                RunStep("06 Build runtime state catalogs", nameof(ProductionArtStateCatalogBuilder.BuildAll), ProductionArtStateCatalogBuilder.BuildAll, report);
                RunStep("07 Build state-transition showcase", nameof(ProductionArtStateTransitionShowcaseBuilder.BuildShowcase), ProductionArtStateTransitionShowcaseBuilder.BuildShowcase, report);
                RunStep("08 Audit runtime state transitions", nameof(ProductionArtStateTransitionShowcaseAudit.AuditShowcase), ProductionArtStateTransitionShowcaseAudit.AuditShowcase, report);
                RunStep("09 Build hero readability showcase", nameof(ProductionArtHeroReadabilityShowcaseBuilder.BuildShowcase), ProductionArtHeroReadabilityShowcaseBuilder.BuildShowcase, report);
                RunStep("10 Audit hero readability", nameof(ProductionArtHeroReadabilityShowcaseAudit.AuditShowcase), ProductionArtHeroReadabilityShowcaseAudit.AuditShowcase, report);
                RunStep("11 Build production decals", nameof(ProductionArtDecalBuilder.BuildAll), ProductionArtDecalBuilder.BuildAll, report);
                RunStep("12 Build production VFX", nameof(ProductionArtVfxBuilder.BuildAll), ProductionArtVfxBuilder.BuildAll, report);
                RunStep("13 Build VFX showcase", nameof(ProductionArtVfxShowcaseBuilder.BuildShowcase), ProductionArtVfxShowcaseBuilder.BuildShowcase, report);
                RunStep("14 Audit VFX showcase", nameof(ProductionArtVfxShowcaseAudit.AuditShowcase), ProductionArtVfxShowcaseAudit.AuditShowcase, report);
                RunStep("15 Build diegetic UI prefabs", nameof(ProductionArtDiegeticUiBuilder.BuildAll), ProductionArtDiegeticUiBuilder.BuildAll, report);
                RunStep("16 Build diegetic UI showcase", nameof(ProductionArtUiShowcaseBuilder.BuildShowcase), ProductionArtUiShowcaseBuilder.BuildShowcase, report);
                RunStep("17 Audit diegetic UI showcase", nameof(ProductionArtUiShowcaseAudit.AuditShowcase), ProductionArtUiShowcaseAudit.AuditShowcase, report);
                RunStep("18 Build Stormnatten showcase", nameof(ProductionArtShowcaseBuilder.BuildShowcase), ProductionArtShowcaseBuilder.BuildShowcase, report);
                RunStep("19 Add camp/signal storm atmosphere", nameof(ProductionArtStormAtmosphereBuilder.AddStormAtmosphere), ProductionArtStormAtmosphereBuilder.AddStormAtmosphere, report);
                RunStep("20 Add bounded storm motion FX", nameof(ProductionArtStormFxBuilder.AddStormMotionFx), ProductionArtStormFxBuilder.AddStormMotionFx, report);
                RunStep("21 Add renderer-culled wind response", nameof(ProductionArtWindResponseBuilder.AddWindResponse), ProductionArtWindResponseBuilder.AddWindResponse, report);
                RunStep("22 Audit imported Stormnatten showcase", nameof(ProductionArtShowcaseAudit.AuditShowcase), ProductionArtShowcaseAudit.AuditShowcase, report);
                RunStep("23 Verify six review scenes stay build-isolated", nameof(VerifyReviewSceneInventory), VerifyReviewSceneInventory, report);

                report.status = "PASS";
                report.finishedUtc = DateTime.UtcNow.ToString("O");
                WriteReport(projectRoot, report);
                Debug.Log("[ProjectOEN.Art.Batch] PASS steps=" + report.passed +
                          " failed=" + report.failed +
                          " unity=" + report.unityVersion +
                          " report=" + Path.Combine(projectRoot, ReportFileName));
            }
            catch (Exception ex)
            {
                report.status = "FAIL";
                report.finishedUtc = DateTime.UtcNow.ToString("O");
                WriteReport(projectRoot, report);
                Debug.LogError("[ProjectOEN.Art.Batch] FAIL after " + report.passed +
                               " passed step(s); report=" + Path.Combine(projectRoot, ReportFileName) +
                               "\n" + ex);
                throw;
            }
        }

        private static void RunStep(string name, string method, Action action, VerificationReport report)
        {
            var result = new VerificationStep
            {
                name = name,
                method = method,
                status = "RUNNING",
                durationMs = 0,
                error = string.Empty,
            };
            report.steps.Add(result);

            var stopwatch = Stopwatch.StartNew();
            Debug.Log("[ProjectOEN.Art.Batch] START " + name + " -> " + method);
            try
            {
                action();
                AssetDatabase.SaveAssets();
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
                stopwatch.Stop();
                result.durationMs = stopwatch.ElapsedMilliseconds;
                result.status = "PASS";
                report.passed++;
                Debug.Log("[ProjectOEN.Art.Batch] PASS " + name + " ms=" + result.durationMs);
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                result.durationMs = stopwatch.ElapsedMilliseconds;
                result.status = "FAIL";
                result.error = ex.GetType().FullName + ": " + ex.Message;
                report.failed++;
                Debug.LogError("[ProjectOEN.Art.Batch] FAIL " + name + " ms=" + result.durationMs + " -> " + result.error);
                throw;
            }
        }

        private static void VerifyReviewSceneInventory()
        {
            var enabledBuildScenes = new HashSet<string>(
                EditorBuildSettings.scenes
                    .Where(scene => scene != null && scene.enabled)
                    .Select(scene => scene.path),
                StringComparer.OrdinalIgnoreCase);

            foreach (string scenePath in ReviewScenePaths)
            {
                if (AssetDatabase.LoadAssetAtPath<SceneAsset>(scenePath) == null)
                    throw new InvalidOperationException("Expected review scene missing after one-shot build: " + scenePath);
                if (enabledBuildScenes.Contains(scenePath))
                    throw new InvalidOperationException("Visual-review scene leaked into enabled build settings: " + scenePath);
            }
        }

        private static void WriteReport(string projectRoot, VerificationReport report)
        {
            string path = Path.Combine(projectRoot, ReportFileName);
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
        }
    }
}
