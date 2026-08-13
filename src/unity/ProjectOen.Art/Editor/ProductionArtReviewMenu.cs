using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Editor entrypoints for the four generated production-art review scenes.
    /// Review-ProductionArt.ps1 continues to call OpenShowcase for the default
    /// Stormnatten landing scene after all audits complete.
    /// </summary>
    public static class ProductionArtReviewMenu
    {
        private const string WorldScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/StormnattenArtShowcase.unity";
        private const string UiScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/DiegeticUiArtShowcase.unity";
        private const string VfxScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/ProductionVfxShowcase.unity";
        private const string MaterialScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/MaterialCalibrationShowcase.unity";

        [MenuItem("Project OEN/Art/Open Stormnatten Art Showcase")]
        public static void OpenShowcase()
        {
            OpenReviewScene(WorldScenePath, "Stormnatten");
        }

        [MenuItem("Project OEN/Art/Open Diegetic UI Art Showcase")]
        public static void OpenUiShowcase()
        {
            OpenReviewScene(UiScenePath, "Diegetic UI");
        }

        [MenuItem("Project OEN/Art/Open Production VFX Showcase")]
        public static void OpenVfxShowcase()
        {
            OpenReviewScene(VfxScenePath, "Production VFX");
        }

        [MenuItem("Project OEN/Art/Open Material Calibration Showcase")]
        public static void OpenMaterialCalibrationShowcase()
        {
            OpenReviewScene(MaterialScenePath, "Material Calibration");
        }

        private static void OpenReviewScene(string scenePath, string label)
        {
            SceneAsset scene = AssetDatabase.LoadAssetAtPath<SceneAsset>(scenePath);
            if (scene == null)
                throw new InvalidOperationException(label + " review scene missing. Build the production-art review pipeline first: " + scenePath);

            EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            Selection.activeObject = scene;
            Debug.Log("[ProjectOEN.Art] Opened " + label + " visual-review scene: " + scenePath);
        }
    }
}