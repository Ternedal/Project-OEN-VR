using UnityEngine;

namespace ProjectOen.Art.Runtime
{
    /// <summary>
    /// Art-only runtime adapter for switching a mount between generated world
    /// prefab states. Intended for infrequent state changes such as shelter,
    /// campfire, signal beacon, repair progress or damaged/intact variants.
    /// </summary>
    public sealed class ProductionArtPrefabStateController : MonoBehaviour
    {
        [SerializeField] private ProductionArtPrefabStateSet stateSet;
        [SerializeField] private Transform mount;
        [SerializeField] private string initialState;
        [SerializeField] private bool applyInitialStateOnStart = true;

        private GameObject currentInstance;

        public ProductionArtPrefabStateSet StateSet => stateSet;
        public string CurrentState { get; private set; }
        public GameObject CurrentInstance => currentInstance;

        private void Start()
        {
            if (mount == null)
                mount = transform;

            if (applyInitialStateOnStart)
            {
                string state = string.IsNullOrWhiteSpace(initialState) && stateSet != null
                    ? stateSet.DefaultState
                    : initialState;
                if (!string.IsNullOrWhiteSpace(state))
                    SetState(state);
            }
        }

        public bool SetState(string stateKey)
        {
            if (stateSet == null)
                return false;
            if (mount == null)
                mount = transform;
            if (string.Equals(CurrentState, stateKey, System.StringComparison.OrdinalIgnoreCase) && currentInstance != null)
                return true;

            GameObject prefab;
            if (!stateSet.TryGetPrefab(stateKey, out prefab))
                return false;

            ReleaseCurrentInstance();

            currentInstance = Instantiate(prefab, mount, false);
            currentInstance.name = prefab.name + " [" + stateKey + "]";
            CurrentState = stateKey;
            return true;
        }

        public bool HasState(string stateKey)
        {
            return stateSet != null && stateSet.ContainsState(stateKey);
        }

        public void Configure(ProductionArtPrefabStateSet set, Transform targetMount, string stateKey)
        {
            stateSet = set;
            mount = targetMount;
            initialState = stateKey;
        }

        private void ReleaseCurrentInstance()
        {
            if (currentInstance == null)
                return;

            if (Application.isPlaying)
            {
                UnityEngine.Object.Destroy(currentInstance);
            }
#if UNITY_EDITOR
            else
            {
                // Editor-side art audits deliberately exercise real SetState calls.
                // Immediate destruction keeps those deterministic and prevents old
                // state instances from surviving beside the replacement.
                UnityEngine.Object.DestroyImmediate(currentInstance);
            }
#else
            else
            {
                UnityEngine.Object.Destroy(currentInstance);
            }
#endif
            currentInstance = null;
        }
    }
}
