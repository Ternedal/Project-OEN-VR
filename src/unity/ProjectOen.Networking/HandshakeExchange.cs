// UNVERIFIED-IN-SANDBOX
// Ikke kompileret. Intet Fusion 2 SDK i skrivemiljøet.
// Antagelser: NetworkBehaviour, [Networked] string med Capacity, Object.HasStateAuthority,
// RPC-attributten [Rpc(RpcSources.All, RpcTargets.All)].

using Fusion;
using ProjectOen.Core.Networking;
using UnityEngine;

namespace ProjectOen.Networking
{
    /// <summary>
    /// docs/07 §5. Udveksler de seks felter og afviser FØR spawn.
    ///
    /// Selve reglen ligger i ProjectOen.Core.Networking.CompatibilityHandshake og er
    /// testet: COMPAT-001 (Q1 legacy må spille med Q3 enhanced - grafikprofil må afvige)
    /// og COMPAT-002 (klokkeskævt content hash afvises). Denne klasse transporterer
    /// data og viser resultatet. Den træffer ingen beslutninger.
    /// </summary>
    public sealed class HandshakeExchange : NetworkBehaviour
    {
        [Networked, Capacity(32)] string RemoteGameVersion { get; set; }
        [Networked] int RemoteProtocolVersion { get; set; }
        [Networked, Capacity(64)] string RemoteContentHash { get; set; }
        [Networked] int RemoteSaveSchemaVersion { get; set; }
        [Networked, Capacity(16)] string RemotePlatformProfile { get; set; }
        [Networked, Capacity(128)] string RemoteFeatureFlags { get; set; }

        public HandshakeResult? Result { get; private set; }

        BuildIdentity _local = null!;

        public void Configure(BuildIdentity local) => _local = local;

        public override void Spawned() => PublishLocalIdentity();

        void PublishLocalIdentity()
        {
            RpcAnnounce(
                _local.GameVersion,
                _local.ProtocolVersion,
                _local.ContentHash,
                _local.SaveSchemaVersion,
                _local.PlatformProfile,
                string.Join(",", _local.FeatureFlags));
        }

        [Rpc(RpcSources.All, RpcTargets.All)]
        void RpcAnnounce(string gameVersion, int protocol, string contentHash,
                         int saveSchema, string platformProfile, string featureFlags)
        {
            var remote = new BuildIdentity(gameVersion, protocol, contentHash, saveSchema, platformProfile,
                string.IsNullOrEmpty(featureFlags) ? new string[0] : featureFlags.Split(','));

            Result = CompatibilityHandshake.Evaluate(_local, remote);

            if (!Result.Accepted)
            {
                // Afvis tydeligt frem for at fejle midt i en session. Beskeden er
                // skrevet til en spiller, ikke til en log.
                Debug.LogWarning($"[Handshake] {Result.Code}: {Result.Message}");
            }
        }
    }
}
