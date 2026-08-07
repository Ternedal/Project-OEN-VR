using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;

namespace ProjectOen.Core.Persistence
{
    /// <summary>
    /// Checksum-reglen fra docs/10, én implementering, ét sted.
    ///
    /// 1. Fjern feltet "checksum".
    /// 2. Serialisér resten som kanonisk JSON.
    /// 3. SHA-256, 64 hex-tegn i lowercase.
    ///
    /// Testvektoren er examples/savegame.example.json. Den samme regel er
    /// implementeret i tools/validate_handoff.py, saa CI og runtime skal give
    /// identisk resultat - det er praecis dét, testen beviser.
    /// </summary>
    public static class SaveChecksum
    {
        public const string ChecksumField = "checksum";

        public static string Compute(IDictionary<string, object?> save)
        {
            var body = new Dictionary<string, object?>();
            foreach (var pair in save)
            {
                if (pair.Key == ChecksumField) continue;
                body[pair.Key] = pair.Value;
            }

            var canonical = CanonicalJson.Serialize(body);
            using var sha = SHA256.Create();
            var hash = sha.ComputeHash(Encoding.UTF8.GetBytes(canonical));

            var sb = new StringBuilder(hash.Length * 2);
            foreach (var b in hash) sb.Append(b.ToString("x2"));
            return sb.ToString();
        }

        public static bool Verify(IDictionary<string, object?> save)
        {
            if (!save.TryGetValue(ChecksumField, out var stored) || !(stored is string expected))
                return false;
            return Compute(save) == expected;
        }

        public static void Stamp(IDictionary<string, object?> save) =>
            save[ChecksumField] = Compute(save);
    }
}
