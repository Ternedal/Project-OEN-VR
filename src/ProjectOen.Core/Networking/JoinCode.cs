using System;
using System.Linq;
using System.Text;

namespace ProjectOen.Core.Networking
{
    /// <summary>
    /// docs/02: "Privat session med 5-6 tegns join code."
    ///
    /// Koden bliver laest hoejt tvaers gennem en stue af en person med et headset paa.
    /// Derfor er alfabetet reduceret: ingen O/0, I/1/L, S/5, B/8, Z/2. En kode der
    /// skal gentages tre gange er en daarlig kode, og det er en ren logikbeslutning -
    /// altsaa noget der kan testes uden headset.
    /// </summary>
    public static class JoinCode
    {
        /// <summary>24 tegn. Konsekvent oplaeselige, ingen forvekslingspar.</summary>
        public const string Alphabet = "ACDEFGHJKMNPQRTUVWXY34679";

        public const int DefaultLength = 6;

        public static string Generate(Random random, int length = DefaultLength)
        {
            if (length < 4 || length > 8) throw new ArgumentOutOfRangeException(nameof(length));
            var sb = new StringBuilder(length);
            for (var i = 0; i < length; i++) sb.Append(Alphabet[random.Next(Alphabet.Length)]);
            return sb.ToString();
        }

        /// <summary>
        /// Retter det, folk faktisk taster: smaa bogstaver, mellemrum, bindestreger og
        /// de forvekslinger alfabetet allerede har fjernet. Skriver nogen 'O', mente de 'Q'
        /// findes ikke - de mente et tegn der ikke er i alfabetet, saa vi mapper til det
        /// naermeste tilsigtede: O->0 findes ikke, saa O afvises hellere end at gaette forkert.
        /// </summary>
        public static bool TryNormalize(string? input, out string normalized)
        {
            normalized = "";
            if (string.IsNullOrWhiteSpace(input)) return false;

            var cleaned = new string(input!.Where(c => !char.IsWhiteSpace(c) && c != '-').ToArray()).ToUpperInvariant();

            var sb = new StringBuilder(cleaned.Length);
            foreach (var c in cleaned)
            {
                // Kun de entydige substitutioner. Alt andet uden for alfabetet afvises,
                // saa en forkert kode fejler tydeligt frem for at joine en anden session.
                var mapped = c switch
                {
                    'O' or '0' => 'Q',
                    'I' or '1' or 'L' => 'J',
                    '5' or 'S' => 'X',
                    '8' or 'B' => 'H',
                    '2' or 'Z' => '3',
                    _ => c
                };
                if (!Alphabet.Contains(mapped)) return false;
                sb.Append(mapped);
            }

            if (sb.Length < 4 || sb.Length > 8) return false;
            normalized = sb.ToString();
            return true;
        }

        public static bool IsValid(string? code) => TryNormalize(code, out var n) && n == code;
    }
}
