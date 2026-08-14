using System;
using System.Collections.Generic;
using UnityEngine;

namespace ProjectOen.Art.Runtime
{
    [CreateAssetMenu(menuName = "Project OEN/Art/Sprite State Set", fileName = "SpriteStateSet")]
    public sealed class ProductionArtSpriteStateSet : ScriptableObject
    {
        [Serializable]
        public sealed class Entry
        {
            public string key;
            public Sprite sprite;

            public Entry(string key, Sprite sprite)
            {
                this.key = key;
                this.sprite = sprite;
            }
        }

        [SerializeField] private string assetId;
        [SerializeField] private string displayName;
        [SerializeField] private string category;
        [SerializeField] private string defaultState;
        [SerializeField] private List<Entry> states = new List<Entry>();

        public string AssetId => assetId;
        public string DisplayName => displayName;
        public string Category => category;
        public string DefaultState => defaultState;
        public IReadOnlyList<Entry> States => states;

        public bool TryGetSprite(string stateKey, out Sprite sprite)
        {
            sprite = null;
            if (string.IsNullOrWhiteSpace(stateKey))
                return false;

            for (int i = 0; i < states.Count; i++)
            {
                Entry entry = states[i];
                if (entry != null && string.Equals(entry.key, stateKey, StringComparison.OrdinalIgnoreCase))
                {
                    sprite = entry.sprite;
                    return sprite != null;
                }
            }
            return false;
        }

        public bool ContainsState(string stateKey)
        {
            Sprite unused;
            return TryGetSprite(stateKey, out unused);
        }

        // Used by the deterministic editor builder. Kept runtime-safe so generated
        // state-set assets do not depend on editor-only serialization helpers.
        public void Configure(string id, string name, string sourceCategory, string initialState, List<Entry> entries)
        {
            assetId = id ?? string.Empty;
            displayName = name ?? string.Empty;
            category = sourceCategory ?? string.Empty;
            defaultState = initialState ?? string.Empty;
            states = entries ?? new List<Entry>();
        }
    }
}
