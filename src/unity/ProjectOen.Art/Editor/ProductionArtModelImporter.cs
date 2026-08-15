using System;
using UnityEditor;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Owns the deterministic model-import contract for generated production art.
    /// OBJ payloads intentionally omit vertex normals, so Unity must calculate them
    /// with one explicit hard-surface-friendly policy on every platform.
    /// </summary>
    public sealed class ProductionArtModelImporter : AssetPostprocessor
    {
        private const string MeshRoot = "Assets/ProductionArt/Meshes/";
        internal const float NormalSmoothingAngle = 60f;

        private void OnPreprocessModel()
        {
            if (!assetPath.StartsWith(MeshRoot, StringComparison.Ordinal))
                return;

            var importer = (ModelImporter)assetImporter;
            importer.importNormals = ModelImporterNormals.Calculate;
            importer.normalCalculationMode = ModelImporterNormalCalculationMode.AreaAndAngleWeighted;
            importer.normalSmoothingSource = ModelImporterNormalSmoothingSource.FromAngle;
            importer.normalSmoothingAngle = NormalSmoothingAngle;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
        }
    }
}
