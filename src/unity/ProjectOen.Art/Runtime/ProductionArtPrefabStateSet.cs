using System;
using System.Collections.Generic;
using UnityEngine;

namespace ProjectOen.Art.Runtime
{
    [CreateAssetMenu(menuName = "Project OEN/Art/Prefab State Set", fileName = "PrefabStateSet")]
    public sealed class ProductionArtPrefabStateSet : ScriptableObject
    {
        [Serializable]
        public sealed class Entry
        {
            public string key;
            public GameObject prefab;

            public Entry(string key, GameObject prefab)
            {
                this.key = key;
                this.prefab = prefab;
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

        public bool TryGetPrefab(string stateKey, out GameObject prefab)
        {
            prefab = null;
            if (string.IsNullOrWhiteSpace(stateKey))
                return false;

            for (int i = 0; i < states.Count; i++)
            {
                Entry entry = states[i];
                if (entry != null && string.Equals(entry.key, stateKey, StringComparison.OrdinalIgnoreCase))
                {
                    prefab = entry.prefab;
                    return prefab != null;
                }
            }
            return false;
        }

        public bool ContainsState(string stateKey)
        {
            GameObject unused;
            return TryGetPrefab(stateKey, out unused);
        }

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
