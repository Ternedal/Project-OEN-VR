using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Converts the EN-011 puddle and EN-025 shoreline-foam holder prefabs into
    /// real cheap Unity ground decals by assigning their state-specific transparent
    /// textures. The broad OBJ plane remains the stable mesh/GUID holder; the visual
    /// state lives in an individual RGBA texture.
    /// </summary>
    public static class ProductionArtDecalBuilder
    {
        private const string DecalRoot = "Assets/ProjectOEN/ProductionArt/Decals/environment_set_dressing";
        private const string PrefabRoot = "Assets/ProjectOEN/ProductionArt/Prefabs/environment_set_dressing";
        private const string MaterialRoot = "Assets/ProjectOEN/ProductionArt/UnityMaterials/Decals";

        [MenuItem("Project OEN/Art/Build Ground Decals")]
        public static void BuildAll()
        {
            if (!AssetDatabase.IsValidFolder(DecalRoot))
                throw new InvalidOperationException("Missing Project OEN decal root: " + DecalRoot);
            if (!AssetDatabase.IsValidFolder(PrefabRoot))
                throw new InvalidOperationException("Production environment prefabs must be built before decals: " + PrefabRoot);

            EnsureFolder(MaterialRoot);
            string[] textureGuids = AssetDatabase.FindAssets("t:Texture2D", new[] { DecalRoot });
            var failures = new List<string>();
            int built = 0;

            foreach (string guid in textureGuids)
            {
                string texturePath = AssetDatabase.GUIDToAssetPath(guid);
                string stem = Path.GetFileNameWithoutExtension(texturePath);
                if (!stem.StartsWith("en-011_", StringComparison.OrdinalIgnoreCase) &&
                    !stem.StartsWith("en-025_", StringComparison.OrdinalIgnoreCase))
                    continue;

                try
                {
                    BuildOne(texturePath, stem);
                    built++;
                }
                catch (Exception ex)
                {
                    failures.Add(stem + ": " + ex.Message);
                }
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            if (built != 5)
                failures.Add("Expected exactly 5 Project OEN ground decal variants, built " + built + ".");

            if (failures.Count > 0)
                throw new InvalidOperationException("Project OEN ground decal build failed:\n" + string.Join("\n", failures));

            Debug.Log("[ProjectOEN.Art] Built 5 state-specific ground decal materials/prefabs (3 puddle + 2 shoreline foam)." );
        }

        private static void BuildOne(string texturePath, string stem)
        {
            string prefabPath = PrefabRoot + "/" + stem + ".prefab";
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            if (prefab == null)
                throw new InvalidOperationException("Matching holder prefab not found: " + prefabPath);

            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
            if (texture == null)
                throw new InvalidOperationException("Decal texture was not imported: " + texturePath);

            Material material = BuildOrUpdateMaterial(stem, texture);
            GameObject root = PrefabUtility.LoadPrefabContents(prefabPath);
            try
            {
                Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
                if (renderers.Length == 0)
                    throw new InvalidOperationException("Holder prefab contains no renderer: " + prefabPath);

                foreach (Renderer renderer in renderers)
                {
                    renderer.sharedMaterial = material;
                    renderer.shadowCastingMode = ShadowCastingMode.Off;
                    renderer.receiveShadows = false;
                }

                // Ground decals must never become invisible collision slabs.
                foreach (Collider collider in root.GetComponentsInChildren<Collider>(true))
                    UnityEngine.Object.DestroyImmediate(collider);

                PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
            }
            finally
            {
                PrefabUtility.UnloadPrefabContents(root);
            }
        }

        private static Material BuildOrUpdateMaterial(string stem, Texture2D texture)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null) shader = Shader.Find("Unlit/Transparent");
            if (shader == null) shader = Shader.Find("Sprites/Default");
            if (shader == null)
                throw new InvalidOperationException("No transparent unlit shader available for Project OEN ground decals.");

            string materialPath = MaterialRoot + "/" + stem + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (material == null)
            {
                material = new Material(shader) { name = stem };
                AssetDatabase.CreateAsset(material, materialPath);
            }
            else
            {
                material.shader = shader;
                material.name = stem;
            }

            if (material.HasProperty("_BaseMap")) material.SetTexture("_BaseMap", texture);
            if (material.HasProperty("_MainTex")) material.SetTexture("_MainTex", texture);
            if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", Color.white);
            if (material.HasProperty("_Color")) material.SetColor("_Color", Color.white);
            if (material.HasProperty("_Surface")) material.SetFloat("_Surface", 1.0f);
            if (material.HasProperty("_Blend")) material.SetFloat("_Blend", 0.0f);
            if (material.HasProperty("_ZWrite")) material.SetFloat("_ZWrite", 0.0f);
            if (material.HasProperty("_Cull")) material.SetFloat("_Cull", 0.0f);
            material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.SetOverrideTag("RenderType", "Transparent");
            material.renderQueue = (int)RenderQueue.Transparent;

            EditorUtility.SetDirty(material);
            return material;
        }

        private static void EnsureFolder(string path)
        {
            string normalized = path.Replace('\\', '/').TrimEnd('/');
            if (AssetDatabase.IsValidFolder(normalized)) return;
            string[] parts = normalized.Split('/');
            string current = parts[0];
            for (int i = 1; i < parts.Length; i++)
            {
                string next = current + "/" + parts[i];
                if (!AssetDatabase.IsValidFolder(next))
                    AssetDatabase.CreateFolder(current, parts[i]);
                current = next;
            }
        }
    }
}
