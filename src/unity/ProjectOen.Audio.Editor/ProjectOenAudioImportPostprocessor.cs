using System;
using UnityEditor;
using UnityEngine;

namespace ProjectOen.Audio.Editor
{
    /// <summary>
    /// Enforces the Quest-oriented Project OEN audio import contract from folder semantics.
    /// Expected landing root: Assets/ProjectOen/Audio/.
    ///
    /// Folder tokens:
    /// - /Spatial/   => force mono
    /// - /2D/        => preserve source channels
    /// - /Streaming/ => Streaming + Vorbis
    /// - /OneShots/  => DecompressOnLoad + ADPCM
    /// - /Compressed/=> CompressedInMemory + Vorbis
    /// </summary>
    public sealed class ProjectOenAudioImportPostprocessor : AssetPostprocessor
    {
        private const string Root = "Assets/ProjectOen/Audio/";

        private void OnPreprocessAudio()
        {
            if (!assetPath.StartsWith(Root, StringComparison.OrdinalIgnoreCase))
                return;

            var importer = (AudioImporter)assetImporter;
            var normalized = assetPath.Replace('\\', '/');
            var spatial = normalized.IndexOf("/Spatial/", StringComparison.OrdinalIgnoreCase) >= 0;
            var streaming = normalized.IndexOf("/Streaming/", StringComparison.OrdinalIgnoreCase) >= 0;
            var oneShot = normalized.IndexOf("/OneShots/", StringComparison.OrdinalIgnoreCase) >= 0;
            var compressed = normalized.IndexOf("/Compressed/", StringComparison.OrdinalIgnoreCase) >= 0;

            importer.forceToMono = spatial;
            importer.normalize = false;
            importer.loadInBackground = streaming;
            importer.preloadAudioData = !streaming;
            importer.ambisonic = false;

            var settings = importer.defaultSampleSettings;
            settings.sampleRateSetting = AudioSampleRateSetting.OverrideSampleRate;
            settings.sampleRateOverride = 48000;

            if (streaming)
            {
                settings.loadType = AudioClipLoadType.Streaming;
                settings.compressionFormat = AudioCompressionFormat.Vorbis;
                settings.quality = 0.62f;
            }
            else if (oneShot)
            {
                settings.loadType = AudioClipLoadType.DecompressOnLoad;
                settings.compressionFormat = AudioCompressionFormat.ADPCM;
                settings.quality = 1f;
            }
            else if (compressed)
            {
                settings.loadType = AudioClipLoadType.CompressedInMemory;
                settings.compressionFormat = AudioCompressionFormat.Vorbis;
                settings.quality = 0.72f;
            }
            else
            {
                Debug.LogWarning(
                    $"Project OEN audio asset '{assetPath}' is missing a load-profile folder token " +
                    "(/Streaming/, /OneShots/ or /Compressed/). Using CompressedInMemory/Vorbis fallback.");
                settings.loadType = AudioClipLoadType.CompressedInMemory;
                settings.compressionFormat = AudioCompressionFormat.Vorbis;
                settings.quality = 0.72f;
            }

            importer.defaultSampleSettings = settings;
        }
    }
}
