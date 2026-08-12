using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Small editor entrypoint used by Review-ProductionArt.ps1 to open the generated
    /// Stormnatten showcase after the deterministic build/audit passes have completed.
    /// </summary>
    public static class ProductionArtReviewMenu
    {
        private const string ScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/StormnattenArtShowcase.unity";

        [MenuItem("Project OEN/Art/Open Stormnatten Art Showcase")]
        public static void OpenShowcase()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
                throw new InvalidOperationException("Showcase scene missing. Build it first: " + ScenePath);

            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Selection.activeObject = AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath);
            Debug.Log("[ProjectOEN.Art] Opened Stormnatten visual-review scene: " + ScenePath);
        }
    }
}
