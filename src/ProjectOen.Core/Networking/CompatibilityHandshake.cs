#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;

namespace ProjectOen.Core.Networking
{
    /// <summary>De seks felter fra docs/07 afsnit 5.</summary>
    public sealed class BuildIdentity
    {
        public BuildIdentity(string gameVersion, int protocolVersion, string contentHash,
                             int saveSchemaVersion, string platformProfile, IEnumerable<string>? featureFlags = null)
        {
            GameVersion = gameVersion;
            ProtocolVersion = protocolVersion;
            ContentHash = contentHash;
            SaveSchemaVersion = saveSchemaVersion;
            PlatformProfile = platformProfile;
            FeatureFlags = new HashSet<string>(featureFlags ?? Enumerable.Empty<string>(), StringComparer.Ordinal);
        }

        public string GameVersion { get; }
        public int ProtocolVersion { get; }
        public string ContentHash { get; }
        public int SaveSchemaVersion { get; }

        /// <summary>Q1_LEGACY, Q2_BASE eller Q3_ENHANCED. Maa afvige mellem klienter.</summary>
        public string PlatformProfile { get; }

        public ISet<string> FeatureFlags { get; }
    }

    public sealed class HandshakeResult
    {
        HandshakeResult(bool accepted, string code, string message)
        {
            Accepted = accepted;
            Code = code;
            Message = message;
        }

        public bool Accepted { get; }
        public string Code { get; }
        public string Message { get; }

        public static HandshakeResult Ok() => new HandshakeResult(true, "OK", "Kompatibel.");
        public static HandshakeResult Reject(string code, string message) => new HandshakeResult(false, code, message);
    }

    /// <summary>
    /// docs/07 afsnit 5: "Quest 1 maa spille med Quest 2/3, hvis protocol/content/schema
    /// matcher. Grafikprofil maa vaere forskellig."
    ///
    /// Det er hele grundlaget for cross-play-lanen, og reglen er derfor skrevet som ren
    /// logik med tests frem for at ligge spredt i netvaerkskoden. COMPAT-001 og COMPAT-002
    /// i docs/13 er de to testcases, denne klasse skal kunne besvare.
    /// </summary>
    public static class CompatibilityHandshake
    {
        public static HandshakeResult Evaluate(BuildIdentity local, BuildIdentity remote)
        {
            if (local.ProtocolVersion != remote.ProtocolVersion)
                return HandshakeResult.Reject("PROTOCOL_MISMATCH",
                    $"Netvaerksprotokol {local.ProtocolVersion} mod {remote.ProtocolVersion}. Begge skal opdatere til samme build.");

            if (!string.Equals(local.ContentHash, remote.ContentHash, StringComparison.Ordinal))
                return HandshakeResult.Reject("CONTENT_MISMATCH",
                    "Scenarioindholdet er ikke ens. Sessionen afvises foer spawn frem for at fejle undervejs.");

            if (local.SaveSchemaVersion != remote.SaveSchemaVersion)
                return HandshakeResult.Reject("SAVE_SCHEMA_MISMATCH",
                    $"Save schema {local.SaveSchemaVersion} mod {remote.SaveSchemaVersion}. Checkpoint-resume ville ikke kunne deles.");

            // Feature flags skal kunne opfyldes af begge. En grafikforbedring er ikke et
            // feature flag - den hoerer til platformprofilen.
            var missingRemote = local.FeatureFlags.Except(remote.FeatureFlags).ToList();
            if (missingRemote.Count > 0)
                return HandshakeResult.Reject("FEATURE_MISSING",
                    $"Modparten mangler: {string.Join(", ", missingRemote)}.");

            var missingLocal = remote.FeatureFlags.Except(local.FeatureFlags).ToList();
            if (missingLocal.Count > 0)
                return HandshakeResult.Reject("FEATURE_MISSING",
                    $"Denne build mangler: {string.Join(", ", missingLocal)}.");

            // Semantisk spilversion og platformprofil maa bevidst afvige. Uden det
            // findes der ingen Q1-Q3-lane overhovedet.
            return HandshakeResult.Ok();
        }
    }
}
