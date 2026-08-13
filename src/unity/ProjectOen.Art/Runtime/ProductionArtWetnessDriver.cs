using System.Collections.Generic;
using UnityEngine;

namespace ProjectOen.Art.Runtime
{
    /// <summary>
    /// Applies scene-wide wet-surface response without cloning or mutating the
    /// shared production materials. The driver is event-driven: it writes
    /// MaterialPropertyBlocks only when enabled, validated in the editor, or
    /// explicitly told that wetness changed. There is deliberately no Update loop.
    ///
    /// Storm/gameplay systems can call SetWetness(0..1). The generated
    /// Stormnatten showcase uses one driver for the whole scene. If a renderer is
    /// inside a ProductionArtStateAppearance prefab, the state-local tint/normal
    /// profile is multiplied with this global wetness response rather than lost.
    /// </summary>
    [ExecuteAlways]
    [DisallowMultipleComponent]
    public sealed class ProductionArtWetnessDriver : MonoBehaviour
    {
        private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static readonly int BumpScaleId = Shader.PropertyToID("_BumpScale");

        [SerializeField, Range(0f, 1f)]
        private float wetness = 0.78f;

        [SerializeField]
        private Transform scopeRoot;

        [SerializeField]
        private bool includeInactive = true;

        private MaterialPropertyBlock propertyBlock;

        public float Wetness => wetness;
        public int LastAffectedRendererCount { get; private set; }

        public void SetWetness(float value)
        {
            wetness = Mathf.Clamp01(value);
            ApplyWetness();
        }

        [ContextMenu("Apply Wetness")]
        public void ApplyWetness()
        {
            if (!gameObject.scene.IsValid())
                return;

            if (propertyBlock == null)
                propertyBlock = new MaterialPropertyBlock();

            int affectedRenderers = 0;
            foreach (Renderer renderer in CollectRenderers())
            {
                if (renderer == null)
                    continue;

                Material[] materials = renderer.sharedMaterials;
                bool affected = false;
                ProductionArtStateAppearance stateAppearance = renderer.GetComponentInParent<ProductionArtStateAppearance>();
                Color stateTint = stateAppearance != null ? stateAppearance.TintMultiplier : Color.white;
                float stateBumpScale = stateAppearance != null ? stateAppearance.NormalScaleMultiplier : 1f;

                for (int materialIndex = 0; materialIndex < materials.Length; materialIndex++)
                {
                    Material material = materials[materialIndex];
                    if (material == null)
                        continue;

                    SurfaceProfile profile;
                    if (!TryGetProfile(CanonicalMaterialName(material.name), out profile))
                        continue;

                    renderer.GetPropertyBlock(propertyBlock, materialIndex);

                    Color wetTint = Color.Lerp(Color.white, profile.wetTint, wetness);
                    Color tint = Multiply(stateTint, wetTint);
                    if (material.HasProperty(BaseColorId))
                        propertyBlock.SetColor(BaseColorId, tint);
                    if (material.HasProperty(ColorId))
                        propertyBlock.SetColor(ColorId, tint);
                    if (material.HasProperty(BumpScaleId))
                    {
                        float wetBumpScale = Mathf.Lerp(1f, profile.wetBumpScale, wetness);
                        propertyBlock.SetFloat(BumpScaleId, stateBumpScale * wetBumpScale);
                    }

                    renderer.SetPropertyBlock(propertyBlock, materialIndex);
                    affected = true;
                }

                if (affected)
                    affectedRenderers++;
            }

            LastAffectedRendererCount = affectedRenderers;
        }

        private void OnEnable()
        {
            ApplyWetness();
        }

#if UNITY_EDITOR
        private void OnValidate()
        {
            wetness = Mathf.Clamp01(wetness);
            if (isActiveAndEnabled)
                ApplyWetness();
        }
#endif

        private IEnumerable<Renderer> CollectRenderers()
        {
            if (scopeRoot != null)
                return scopeRoot.GetComponentsInChildren<Renderer>(includeInactive);

            var result = new List<Renderer>(128);
            GameObject[] roots = gameObject.scene.GetRootGameObjects();
            foreach (GameObject root in roots)
            {
                if (root == null)
                    continue;
                result.AddRange(root.GetComponentsInChildren<Renderer>(includeInactive));
            }
            return result;
        }

        private static Color Multiply(Color a, Color b)
        {
            return new Color(a.r * b.r, a.g * b.g, a.b * b.b, a.a * b.a);
        }

        private static string CanonicalMaterialName(string materialName)
        {
            if (string.IsNullOrEmpty(materialName))
                return string.Empty;

            const string instanceSuffix = " (Instance)";
            if (materialName.EndsWith(instanceSuffix, System.StringComparison.Ordinal))
                return materialName.Substring(0, materialName.Length - instanceSuffix.Length);
            return materialName;
        }

        private static bool TryGetProfile(string materialName, out SurfaceProfile profile)
        {
            // Fire and water are intentionally excluded. Fire should keep its
            // emissive read, while water already owns its smooth response.
            switch (materialName)
            {
                case "Wood":
                    profile = new SurfaceProfile(new Color(0.70f, 0.75f, 0.78f, 1f), 0.68f);
                    return true;
                case "Rope":
                    profile = new SurfaceProfile(new Color(0.74f, 0.78f, 0.80f, 1f), 0.70f);
                    return true;
                case "Tarp":
                    profile = new SurfaceProfile(new Color(0.79f, 0.85f, 0.88f, 1f), 0.78f);
                    return true;
                case "Metal":
                    profile = new SurfaceProfile(new Color(0.80f, 0.84f, 0.86f, 1f), 0.82f);
                    return true;
                case "Stone":
                    profile = new SurfaceProfile(new Color(0.68f, 0.73f, 0.77f, 1f), 0.62f);
                    return true;
                case "Leaf":
                    profile = new SurfaceProfile(new Color(0.72f, 0.80f, 0.75f, 1f), 0.70f);
                    return true;
                case "Cloth":
                    profile = new SurfaceProfile(new Color(0.74f, 0.78f, 0.80f, 1f), 0.72f);
                    return true;
                case "Mud":
                    profile = new SurfaceProfile(new Color(0.62f, 0.67f, 0.69f, 1f), 0.55f);
                    return true;
                case "Char":
                    profile = new SurfaceProfile(new Color(0.78f, 0.80f, 0.82f, 1f), 0.80f);
                    return true;
                default:
                    profile = default(SurfaceProfile);
                    return false;
            }
        }

        private readonly struct SurfaceProfile
        {
            public readonly Color wetTint;
            public readonly float wetBumpScale;

            public SurfaceProfile(Color wetTint, float wetBumpScale)
            {
                this.wetTint = wetTint;
                this.wetBumpScale = wetBumpScale;
            }
        }
    }
}
