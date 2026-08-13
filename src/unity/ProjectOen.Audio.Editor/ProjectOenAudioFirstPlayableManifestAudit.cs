using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Audio.Editor
{
    /// <summary>
    /// Verifies that the Unity project contains the exact staged first-playable WAV payload
    /// described by FIRST_PLAYABLE_MANIFEST.csv before generated definitions or scene state are mutated.
    /// This prevents stale files from an older extraction, duplicate event/variation pairs and modified
    /// source WAVs from silently entering the AudioCatalog.
    /// </summary>
    internal static class ProjectOenAudioFirstPlayableManifestAudit
    {
        internal const string ManifestFileName = "FIRST_PLAYABLE_MANIFEST.csv";
        private const string AudioRoot = "Assets/ProjectOen/Audio";

        internal readonly struct Entry
        {
            public Entry(
                AudioEventId eventId,
                int variation,
                string sourcePack,
                string unityPath,
                string sha256,
                long bytes)
            {
                EventId = eventId;
                Variation = variation;
                SourcePack = sourcePack;
                UnityPath = unityPath;
                Sha256 = sha256;
                Bytes = bytes;
            }

            public AudioEventId EventId { get; }
            public int Variation { get; }
            public string SourcePack { get; }
            public string UnityPath { get; }
            public string Sha256 { get; }
            public long Bytes { get; }
        }

        internal sealed class Result
        {
            public bool Ok { get; set; }
            public string Error { get; set; } = string.Empty;
            public int ClipCount { get; set; }
            public int EventCount { get; set; }
            public IReadOnlyList<Entry> Entries { get; set; } = Array.Empty<Entry>();
        }

        internal static Result Audit()
        {
            try
            {
                var entries = LoadEntries();
                VerifyImportedPayload(entries);
                return new Result
                {
                    Ok = true,
                    ClipCount = entries.Count,
                    EventCount = entries.Select(entry => entry.EventId).Distinct().Count(),
                    Entries = entries,
                };
            }
            catch (Exception exception)
            {
                return new Result
                {
                    Ok = false,
                    Error = exception.Message,
                };
            }
        }

        internal static IReadOnlyList<Entry> RequireVerifiedEntries()
        {
            var result = Audit();
            if (!result.Ok)
                throw new InvalidOperationException(
                    "Project Oen first-playable manifest audit failed: " + result.Error);
            return result.Entries;
        }

        internal static bool TryParseCanonicalClipName(
            string clipName,
            out AudioEventId eventId,
            out int variation)
        {
            eventId = AudioEventId.None;
            variation = 0;
            if (string.IsNullOrWhiteSpace(clipName))
                return false;

            var separator = clipName.LastIndexOf('_');
            if (separator <= 0 || separator >= clipName.Length - 1)
                return false;

            var eventName = clipName.Substring(0, separator);
            if (eventName == "SFX_STS_Hunger_Warn" || eventName == "SFX_STS_Thirst_Warn")
                return false;

            if (!int.TryParse(
                    clipName.Substring(separator + 1),
                    NumberStyles.None,
                    CultureInfo.InvariantCulture,
                    out variation) ||
                variation <= 0)
                return false;

            return Enum.TryParse(eventName, out eventId) && eventId != AudioEventId.None;
        }

        private static List<Entry> LoadEntries()
        {
            var projectRoot = ProjectRoot();
            var manifestPath = Path.Combine(projectRoot, ManifestFileName);
            if (!File.Exists(manifestPath))
            {
                throw new InvalidOperationException(
                    $"missing '{ManifestFileName}' at the Unity project root. " +
                    "Extract the complete oen-unity-first-playable-audio-v1 artifact at the project root before running the audio builder.");
            }

            var lines = File.ReadAllLines(manifestPath, Encoding.UTF8);
            if (lines.Length < 2)
                throw new InvalidOperationException($"'{ManifestFileName}' is empty or has no data rows.");

            var header = ParseCsvLine(lines[0]);
            var expectedHeader = new[]
            {
                "event_id", "variation", "source_pack", "unity_path", "sha256", "bytes",
            };
            if (header.Count != expectedHeader.Length ||
                !header.SequenceEqual(expectedHeader, StringComparer.Ordinal))
            {
                throw new InvalidOperationException(
                    $"'{ManifestFileName}' header drift; expected {string.Join(",", expectedHeader)}.");
            }

            var entries = new List<Entry>(lines.Length - 1);
            var paths = new HashSet<string>(StringComparer.Ordinal);
            var eventVariations = new HashSet<string>(StringComparer.Ordinal);

            for (var lineNumber = 2; lineNumber <= lines.Length; lineNumber++)
            {
                if (string.IsNullOrWhiteSpace(lines[lineNumber - 1]))
                    continue;

                var fields = ParseCsvLine(lines[lineNumber - 1]);
                if (fields.Count != expectedHeader.Length)
                {
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: expected {expectedHeader.Length} fields, got {fields.Count}.");
                }

                var eventName = fields[0].Trim();
                if (eventName == "SFX_STS_Hunger_Warn" || eventName == "SFX_STS_Thirst_Warn" ||
                    !Enum.TryParse(eventName, out AudioEventId eventId) ||
                    eventId == AudioEventId.None)
                {
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: non-canonical event_id '{eventName}'.");
                }

                if (!int.TryParse(
                        fields[1], NumberStyles.None, CultureInfo.InvariantCulture, out var variation) ||
                    variation <= 0)
                {
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: invalid variation '{fields[1]}'.");
                }

                var sourcePack = fields[2].Trim();
                if (string.IsNullOrWhiteSpace(sourcePack))
                    throw new InvalidOperationException($"'{ManifestFileName}' line {lineNumber}: blank source_pack.");

                var unityPath = NormalizeUnityPath(fields[3]);
                if (!unityPath.StartsWith(AudioRoot + "/", StringComparison.Ordinal) ||
                    unityPath.Contains("../", StringComparison.Ordinal) ||
                    !unityPath.EndsWith(".wav", StringComparison.OrdinalIgnoreCase))
                {
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: invalid Unity WAV path '{fields[3]}'.");
                }

                var expectedFileName = $"{eventName}_{variation:00}.wav";
                if (!string.Equals(Path.GetFileName(unityPath), expectedFileName, StringComparison.Ordinal))
                {
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: filename must be '{expectedFileName}', got '{Path.GetFileName(unityPath)}'.");
                }

                var hash = fields[4].Trim().ToLowerInvariant();
                if (hash.Length != 64 || hash.Any(ch => !Uri.IsHexDigit(ch)))
                {
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: invalid SHA-256 '{fields[4]}'.");
                }

                if (!long.TryParse(
                        fields[5], NumberStyles.None, CultureInfo.InvariantCulture, out var bytes) ||
                    bytes <= 0)
                {
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: invalid byte count '{fields[5]}'.");
                }

                if (!paths.Add(unityPath))
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: duplicate unity_path '{unityPath}'.");

                var eventVariationKey = $"{eventName}:{variation}";
                if (!eventVariations.Add(eventVariationKey))
                    throw new InvalidOperationException(
                        $"'{ManifestFileName}' line {lineNumber}: duplicate event/variation '{eventVariationKey}'.");

                entries.Add(new Entry(eventId, variation, sourcePack, unityPath, hash, bytes));
            }

            if (entries.Count == 0)
                throw new InvalidOperationException($"'{ManifestFileName}' contains no usable rows.");

            return entries;
        }

        private static void VerifyImportedPayload(IReadOnlyList<Entry> entries)
        {
            var projectRoot = ProjectRoot();
            var manifestPaths = new HashSet<string>(
                entries.Select(entry => entry.UnityPath),
                StringComparer.Ordinal);

            foreach (var entry in entries)
            {
                var absolutePath = Path.Combine(
                    projectRoot,
                    entry.UnityPath.Replace('/', Path.DirectorySeparatorChar));
                if (!File.Exists(absolutePath))
                    throw new InvalidOperationException($"manifested WAV is missing: '{entry.UnityPath}'.");

                var info = new FileInfo(absolutePath);
                if (info.Length != entry.Bytes)
                {
                    throw new InvalidOperationException(
                        $"manifested WAV size mismatch for '{entry.UnityPath}': expected {entry.Bytes}, got {info.Length}.");
                }

                var actualHash = Sha256(absolutePath);
                if (!string.Equals(actualHash, entry.Sha256, StringComparison.Ordinal))
                {
                    throw new InvalidOperationException(
                        $"manifested WAV SHA-256 mismatch for '{entry.UnityPath}': expected {entry.Sha256}, got {actualHash}.");
                }

                var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(entry.UnityPath);
                if (clip == null)
                {
                    throw new InvalidOperationException(
                        $"manifested WAV has not imported as AudioClip yet: '{entry.UnityPath}'. " +
                        "Let Unity finish importing, then rerun the builder.");
                }

                if (!TryParseCanonicalClipName(clip.name, out var parsedEvent, out var parsedVariation) ||
                    parsedEvent != entry.EventId ||
                    parsedVariation != entry.Variation)
                {
                    throw new InvalidOperationException(
                        $"imported clip identity drift at '{entry.UnityPath}': clip name '{clip.name}' does not match manifest event/variation.");
                }
            }

            var audioRootAbsolute = Path.Combine(
                projectRoot,
                AudioRoot.Replace('/', Path.DirectorySeparatorChar));
            if (!Directory.Exists(audioRootAbsolute))
                throw new InvalidOperationException($"missing imported audio root '{AudioRoot}'.");

            foreach (var absolutePath in Directory.EnumerateFiles(
                         audioRootAbsolute,
                         "*.wav",
                         SearchOption.AllDirectories))
            {
                var unityPath = NormalizeUnityPath(
                    Path.GetRelativePath(projectRoot, absolutePath));
                var clipName = Path.GetFileNameWithoutExtension(absolutePath);
                if (!TryParseCanonicalClipName(clipName, out _, out _))
                    continue;

                if (!manifestPaths.Contains(unityPath))
                {
                    throw new InvalidOperationException(
                        $"stale/unmanaged canonical WAV found outside the current manifest: '{unityPath}'. " +
                        "Remove old first-playable audio files or regenerate/extract the current staged artifact into a clean audio tree.");
                }
            }
        }

        private static string ProjectRoot()
        {
            var assets = new DirectoryInfo(Application.dataPath);
            if (assets.Parent == null)
                throw new InvalidOperationException("unable to resolve Unity project root from Application.dataPath.");
            return assets.Parent.FullName;
        }

        private static string NormalizeUnityPath(string value)
            => (value ?? string.Empty).Trim().Replace('\\', '/');

        private static string Sha256(string path)
        {
            using var stream = File.OpenRead(path);
            using var sha = SHA256.Create();
            var bytes = sha.ComputeHash(stream);
            var builder = new StringBuilder(bytes.Length * 2);
            for (var index = 0; index < bytes.Length; index++)
                builder.Append(bytes[index].ToString("x2", CultureInfo.InvariantCulture));
            return builder.ToString();
        }

        private static List<string> ParseCsvLine(string line)
        {
            var result = new List<string>();
            var field = new StringBuilder();
            var quoted = false;

            for (var index = 0; index < line.Length; index++)
            {
                var ch = line[index];
                if (quoted)
                {
                    if (ch == '"')
                    {
                        if (index + 1 < line.Length && line[index + 1] == '"')
                        {
                            field.Append('"');
                            index++;
                        }
                        else
                        {
                            quoted = false;
                        }
                    }
                    else
                    {
                        field.Append(ch);
                    }
                    continue;
                }

                if (ch == '"' && field.Length == 0)
                {
                    quoted = true;
                    continue;
                }

                if (ch == ',')
                {
                    result.Add(field.ToString());
                    field.Clear();
                    continue;
                }

                field.Append(ch);
            }

            if (quoted)
                throw new InvalidOperationException("unterminated quoted CSV field.");

            result.Add(field.ToString());
            return result;
        }
    }
}
