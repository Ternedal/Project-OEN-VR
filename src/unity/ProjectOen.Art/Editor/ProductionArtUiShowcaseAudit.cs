using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace ProjectOen.Art.Editor
{
    /// <summary>
    /// Audits the actually imported diegetic-UI showcase at physical VR scale.
    /// This is an art/structure gate, not a replacement for headset legibility
    /// testing or interaction usability testing.
    /// </summary>
    public static class ProductionArtUiShowcaseAudit
    {
        private const string ScenePath = "Assets/ProjectOEN/ProductionArt/Scenes/DiegeticUiArtShowcase.unity";
        private const int MinSpriteRenderers = 22;
        private const int MaxSpriteRenderers = 32;
        private const int MaxColliders = 1;

        [MenuItem("Project OEN/Art/Audit Diegetic UI Showcase")]
        public static void AuditShowcase()
        {
            if (!System.IO.File.Exists(ScenePath))
                throw new InvalidOperationException("Diegetic UI showcase scene is missing: " + ScenePath);

            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();

            RequireNamed(roots, "Diegetic UI Physical Scale Review");
            RequireNamed(roots, "Diegetic UI Review Camera");

            GameObject[] all = roots.SelectMany(r => r.GetComponentsInChildren<Transform>(true))
                .Select(t => t.gameObject)
                .Distinct()
                .ToArray();

            RequireNamed(all, "Wrist Status - physical scale");
            RequireNamed(all, "Planning Board - physical scale");
            RequireNamed(all, "Interaction Markers - physical scale");
            RequireNamed(all, "Meta Status - physical scale");
            RequireNamed(all, "1m Scale Reference");

            SpriteRenderer[] sprites = all.SelectMany(go => go.GetComponents<SpriteRenderer>()).ToArray();
            if (sprites.Length < MinSpriteRenderers || sprites.Length > MaxSpriteRenderers)
                throw new InvalidOperationException("Unexpected SpriteRenderer count: " + sprites.Length +
                    " (expected " + MinSpriteRenderers + ".." + MaxSpriteRenderers + ")");

            foreach (SpriteRenderer renderer in sprites)
            {
                if (renderer.sprite == null)
                    throw new InvalidOperationException("Null production sprite on: " + renderer.gameObject.name);
                if (renderer.shadowCastingMode != ShadowCastingMode.Off)
                    throw new InvalidOperationException("Diegetic UI must not cast realtime shadows: " + renderer.gameObject.name);
                if (renderer.receiveShadows)
                    throw new InvalidOperationException("Diegetic UI must not receive realtime shadows: " + renderer.gameObject.name);
            }

            Collider[] colliders = all.SelectMany(go => go.GetComponents<Collider>()).ToArray();
            if (colliders.Length > MaxColliders)
                throw new InvalidOperationException("Diegetic UI art layer has too many colliders: " + colliders.Length +
                    " (max " + MaxColliders + ")");

            if (all.SelectMany(go => go.GetComponents<Light>()).Any())
                throw new InvalidOperationException("Diegetic UI review scene must not add realtime lights.");
            if (all.SelectMany(go => go.GetComponents<ParticleSystem>()).Any())
                throw new InvalidOperationException("Diegetic UI review scene must not add particle systems.");

            AuditBounds(all, "Wrist Status - physical scale", 0.15f, 0.50f);
            AuditBounds(all, "Planning Board - physical scale", 0.60f, 1.20f);
            AuditBounds(all, "Interaction Markers - physical scale", 0.40f, 0.90f);
            AuditBounds(all, "Meta Status - physical scale", 0.30f, 0.80f);

            bool leakedIntoBuild = EditorBuildSettings.scenes.Any(s => s.enabled &&
                string.Equals(s.path, ScenePath, StringComparison.OrdinalIgnoreCase));
            if (leakedIntoBuild)
                throw new InvalidOperationException("Diegetic UI visual-review scene must not be enabled in Android build settings.");

            Debug.Log("[ProjectOEN.Art.UI.Audit] PASS: " + sprites.Length +
                      " sprite renderers, " + colliders.Length +
                      " collider(s), zero lights/particles, physical bounds valid, scene excluded from build settings.");
        }

        private static void AuditBounds(GameObject[] all, string name, float minWidth, float maxWidth)
        {
            GameObject root = all.FirstOrDefault(go => go.name == name);
            if (root == null)
                throw new InvalidOperationException("Missing UI review object: " + name);

            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
                throw new InvalidOperationException("No renderers under UI review object: " + name);

            Bounds bounds = renderers[0].bounds;
            for (int i = 1; i < renderers.Length; i++)
                bounds.Encapsulate(renderers[i].bounds);

            float width = bounds.size.x;
            if (width < minWidth || width > maxWidth)
                throw new InvalidOperationException(name + " physical width out of range: " + width.ToString("F3") +
                    "m (expected " + minWidth.ToString("F2") + ".." + maxWidth.ToString("F2") + "m)");
        }

        private static GameObject RequireNamed(GameObject[] objects, string name)
        {
            GameObject found = objects.FirstOrDefault(go => go.name == name);
            if (found == null)
                throw new InvalidOperationException("Required UI showcase object missing: " + name);
            return found;
        }
    }
}
