using UnityEngine;

namespace ProjectOen.Art.Runtime
{
    /// <summary>
    /// Lightweight, state-local appearance modifier for generated production-art
    /// prefabs. It writes MaterialPropertyBlocks only when the state is enabled,
    /// validated in the editor, or explicitly re-applied. There is deliberately
    /// no Update/LateUpdate loop and no material cloning.
    ///
    /// Global storm wetness remains owned by ProductionArtWetnessDriver. When a
    /// wetness driver is present, it combines its wet-surface tint/normal response
    /// with this state-local profile instead of overwriting it.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class ProductionArtStateAppearance : MonoBehaviour
    {
        private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static readonly int BumpScaleId = Shader.PropertyToID("_BumpScale");
        private static readonly int EmissionColorId = Shader.PropertyToID("_EmissionColor");

        [SerializeField]
        private string profileKey;

        [SerializeField]
        private Color tintMultiplier = Color.white;

        [SerializeField, Range(0.1f, 1.2f)]
        private float normalScaleMultiplier = 1f;

        [SerializeField, Range(0f, 1.2f)]
        private float emissionScale = 1f;

        [SerializeField]
        private bool applyOnEnable = true;

        private MaterialPropertyBlock propertyBlock;

        public string ProfileKey => profileKey;
        public Color TintMultiplier => tintMultiplier;
        public float NormalScaleMultiplier => normalScaleMultiplier;
        public float EmissionScale => emissionScale;

        private void OnEnable()
        {
            if (!applyOnEnable)
                return;

            ApplyAppearance();
            RefreshWetnessDrivers();
        }

#if UNITY_EDITOR
        private void OnValidate()
        {
            normalScaleMultiplier = Mathf.Clamp(normalScaleMultiplier, 0.1f, 1.2f);
            emissionScale = Mathf.Clamp(emissionScale, 0f, 1.2f);
            if (isActiveAndEnabled)
            {
                ApplyAppearance();
                RefreshWetnessDrivers();
            }
        }
#endif

        [ContextMenu("Apply State Appearance")]
        public void ApplyAppearance()
        {
            if (propertyBlock == null)
                propertyBlock = new MaterialPropertyBlock();

            Renderer[] renderers = GetComponentsInChildren<Renderer>(true);
            foreach (Renderer renderer in renderers)
            {
                if (renderer == null)
                    continue;

                Material[] materials = renderer.sharedMaterials;
                for (int materialIndex = 0; materialIndex < materials.Length; materialIndex++)
                {
                    Material material = materials[materialIndex];
                    if (material == null)
                        continue;

                    string materialName = CanonicalMaterialName(material.name);
                    bool isFire = string.Equals(materialName, "Fire", System.StringComparison.OrdinalIgnoreCase);
                    bool isWater = string.Equals(materialName, "Water", System.StringComparison.OrdinalIgnoreCase);
                    renderer.GetPropertyBlock(propertyBlock, materialIndex);

                    // Fire keeps its authored base colour and is distinguished by
                    // emission strength. Water owns its own surface response.
                    if (!isFire && !isWater)
                    {
                        if (material.HasProperty(BaseColorId))
                            propertyBlock.SetColor(BaseColorId, tintMultiplier);
                        if (material.HasProperty(ColorId))
                            propertyBlock.SetColor(ColorId, tintMultiplier);
                        if (material.HasProperty(BumpScaleId))
                            propertyBlock.SetFloat(BumpScaleId, normalScaleMultiplier);
                    }

                    if (isFire && material.HasProperty(EmissionColorId))
                    {
                        Color authoredEmission = material.GetColor(EmissionColorId);
                        propertyBlock.SetColor(EmissionColorId, authoredEmission * emissionScale);
                    }

                    renderer.SetPropertyBlock(propertyBlock, materialIndex);
                }
            }
        }

        public void Configure(string key, Color tint, float normalScale, float fireEmissionScale)
        {
            profileKey = key ?? string.Empty;
            tintMultiplier = tint;
            normalScaleMultiplier = Mathf.Clamp(normalScale, 0.1f, 1.2f);
            emissionScale = Mathf.Clamp(fireEmissionScale, 0f, 1.2f);
            applyOnEnable = true;
        }

        private void RefreshWetnessDrivers()
        {
            if (!gameObject.scene.IsValid())
                return;

            ProductionArtWetnessDriver[] drivers = FindObjectsOfType<ProductionArtWetnessDriver>(true);
            foreach (ProductionArtWetnessDriver driver in drivers)
            {
                if (driver != null && driver.isActiveAndEnabled)
                    driver.ApplyWetness();
            }
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
    }
}
