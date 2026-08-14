using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ProjectOen.Audio.Editor
{
    /// <summary>
    /// Batchmode evidence runner for the three physical Unity-side audio merge gates.
    ///
    /// Example:
    /// Unity -batchmode -quit -projectPath <project> \
    ///   -executeMethod ProjectOen.Audio.Editor.ProjectOenAudioPremergeBatch.Run \
    ///   -oenAudioScene Assets/Scenes/Gameplay.unity \
    ///   -oenAudioEvidence build/audio-unity-premerge-evidence.json
    ///
    /// The current oen-unity-first-playable-audio-v1 artifact must already be extracted at
    /// the Unity project root. The runner never saves the gameplay scene; scene installation
    /// is audited in memory and discarded on Editor exit.
    /// </summary>
    public static class ProjectOenAudioPremergeBatch
    {
        private const string ManifestFileName = "FIRST_PLAYABLE_MANIFEST.csv";
        private const string RuntimePrefabPath =
            "Assets/ProjectOen/Audio/GeneratedFirstPlayable/Runtime/AudioRuntime_FirstPlayable.prefab";
        private const string DefaultEvidencePath = "build/audio-unity-premerge-evidence.json";
        private const string SceneArg = "-oenAudioScene";
        private const string EvidenceArg = "-oenAudioEvidence";

        [Serializable]
        private sealed class GateResult
        {
            public string gateId = string.Empty;
            public bool passed;
            public string detail = string.Empty;
        }

        [Serializable]
        private sealed class Evidence
        {
            public int schemaVersion = 1;
            public string generatedUtc = string.Empty;
            public string unityVersion = string.Empty;
            public string scenePath = string.Empty;
            public string manifestSha256 = string.Empty;
            public int manifestClipCount;
            public int manifestEventCount;
            public int missingScriptCount;
            public int errorCount;
            public int warningCount;
            public GateResult[] gates = Array.Empty<GateResult>();
            public string[] errors = Array.Empty<string>();
            public string[] warnings = Array.Empty<string>();
        }

        public static void Run()
        {
            var errors = new List<string>();
            var warnings = new List<string>();
            Application.logMessageReceived += CaptureLog;

            var evidence = new Evidence
            {
                generatedUtc = DateTime.UtcNow.ToString("O", CultureInfo.InvariantCulture),
                unityVersion = Application.unityVersion,
            };

            var exitCode = 1;
            try
            {
                var scenePath = RequiredArgument(SceneArg).Replace('\\', '/');
                var evidencePath = OptionalArgument(EvidenceArg) ?? DefaultEvidencePath;
                evidence.scenePath = scenePath;

                if (!scenePath.StartsWith("Assets/", StringComparison.Ordinal) ||
                    !scenePath.EndsWith(".unity", StringComparison.OrdinalIgnoreCase))
                {
                    throw new InvalidOperationException(
                        $"{SceneArg} must be a project-relative Assets/.../*.unity path, got '{scenePath}'.");
                }

                var projectRoot = ProjectRoot();
                var absoluteScenePath = Path.Combine(
                    projectRoot,
                    scenePath.Replace('/', Path.DirectorySeparatorChar));
                if (!File.Exists(absoluteScenePath))
                    throw new FileNotFoundException("audio premerge target scene does not exist", absoluteScenePath);

                var manifestPath = Path.Combine(projectRoot, ManifestFileName);
                if (!File.Exists(manifestPath))
                    throw new FileNotFoundException(
                        "current Unity first-playable artifact is not extracted at the project root",
                        manifestPath);

                evidence.manifestSha256 = Sha256(manifestPath);

                EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
                AssetDatabase.Refresh();

                var manifest = ProjectOenAudioFirstPlayableManifestAudit.Audit();
                evidence.manifestClipCount = manifest.ClipCount;
                evidence.manifestEventCount = manifest.EventCount;

                var compileGate = new GateResult
                {
                    gateId = "unity_import_compile",
                    passed = manifest.Ok,
                    detail = manifest.Ok
                        ? $"Unity {Application.unityVersion} executed the ProjectOen.Audio.Editor batch runner and manifest/import audit passed for {manifest.ClipCount} clips / {manifest.EventCount} events."
                        : "Manifest/import audit failed: " + manifest.Error,
                };

                var beforeBuildErrors = errors.Count;
                ProjectOenAudioOneClickFirstPlayableBuilder.BuildOneClick();
                ProjectOenAudioOneClickFirstPlayableBuilder.AuditOneClick();
                var buildErrors = errors.Count - beforeBuildErrors;

                var firstPlayableGate = new GateResult
                {
                    gateId = "unity_first_playable_audit",
                    passed = manifest.Ok && buildErrors == 0,
                    detail = buildErrors == 0
                        ? "One-click build plus first-playable audit completed without Unity error logs."
                        : $"One-click build/audit emitted {buildErrors} Unity error log(s).",
                };

                var beforeSceneErrors = errors.Count;
                ProjectOenAudioSceneInstaller.InstallIntoActiveScene();
                ProjectOenAudioSceneInstaller.AuditActiveScene();
                var sceneErrors = errors.Count - beforeSceneErrors;

                evidence.missingScriptCount = CountGeneratedRuntimeMissingScripts();
                var sceneGate = new GateResult
                {
                    gateId = "unity_active_scene_audit",
                    passed = firstPlayableGate.passed && sceneErrors == 0 && evidence.missingScriptCount == 0,
                    detail = sceneErrors == 0 && evidence.missingScriptCount == 0
                        ? "Active-scene install/audit completed without Unity error logs and generated runtime Missing Scripts=0. Scene was not saved."
                        : $"Active-scene install/audit errors={sceneErrors}, generated runtime Missing Scripts={evidence.missingScriptCount}.",
                };

                if (evidence.missingScriptCount != 0)
                {
                    compileGate.passed = false;
                    compileGate.detail += $" Generated runtime Missing Scripts={evidence.missingScriptCount}.";
                }

                evidence.gates = new[] { compileGate, firstPlayableGate, sceneGate };
                evidence.errorCount = errors.Count;
                evidence.warningCount = warnings.Count;
                evidence.errors = errors.ToArray();
                evidence.warnings = warnings.ToArray();

                var allPassed = evidence.gates.All(gate => gate.passed) && evidence.errorCount == 0;
                WriteEvidence(projectRoot, evidencePath, evidence);

                Debug.Log(
                    $"Project Oen audio Unity premerge batch: status={(allPassed ? "PASSED" : "FAILED")}, " +
                    $"manifest={evidence.manifestClipCount}/{evidence.manifestEventCount}, " +
                    $"missingScripts={evidence.missingScriptCount}, errors={evidence.errorCount}, warnings={evidence.warningCount}. " +
                    $"Evidence='{evidencePath}'.");

                exitCode = allPassed ? 0 : 1;
            }
            catch (Exception exception)
            {
                errors.Add(exception.ToString());
                evidence.errorCount = errors.Count;
                evidence.warningCount = warnings.Count;
                evidence.errors = errors.ToArray();
                evidence.warnings = warnings.ToArray();

                try
                {
                    var projectRoot = ProjectRoot();
                    var evidencePath = OptionalArgument(EvidenceArg) ?? DefaultEvidencePath;
                    WriteEvidence(projectRoot, evidencePath, evidence);
                }
                catch (Exception writeException)
                {
                    Debug.LogError("Project Oen audio premerge evidence write also failed: " + writeException);
                }

                Debug.LogError("Project Oen audio Unity premerge batch failed: " + exception);
                exitCode = 1;
            }
            finally
            {
                Application.logMessageReceived -= CaptureLog;
            }

            EditorApplication.Exit(exitCode);

            void CaptureLog(string condition, string stackTrace, LogType type)
            {
                var entry = string.IsNullOrWhiteSpace(stackTrace)
                    ? condition
                    : condition + "\n" + stackTrace;
                if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert)
                    errors.Add(entry);
                else if (type == LogType.Warning)
                    warnings.Add(entry);
            }
        }

        private static int CountGeneratedRuntimeMissingScripts()
        {
            var count = 0;
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(RuntimePrefabPath);
            if (prefab != null)
                count += CountMissingScriptsRecursive(prefab);

            var scene = SceneManager.GetActiveScene();
            if (!scene.IsValid() || !scene.isLoaded)
                return count;

            var serviceRoots = new HashSet<GameObject>();
            foreach (var root in scene.GetRootGameObjects())
            {
                foreach (var service in root.GetComponentsInChildren<AudioService>(true))
                {
                    if (service == null)
                        continue;
                    var prefabRoot = PrefabUtility.GetOutermostPrefabInstanceRoot(service.gameObject);
                    serviceRoots.Add(prefabRoot != null ? prefabRoot : service.gameObject);
                }
            }

            foreach (var root in serviceRoots)
                count += CountMissingScriptsRecursive(root);
            return count;
        }

        private static int CountMissingScriptsRecursive(GameObject root)
        {
            if (root == null)
                return 0;

            var count = GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(root);
            for (var index = 0; index < root.transform.childCount; index++)
                count += CountMissingScriptsRecursive(root.transform.GetChild(index).gameObject);
            return count;
        }

        private static string RequiredArgument(string name)
        {
            var value = OptionalArgument(name);
            if (string.IsNullOrWhiteSpace(value))
                throw new InvalidOperationException($"missing required command-line argument {name} <value>.");
            return value;
        }

        private static string OptionalArgument(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (var index = 0; index < args.Length - 1; index++)
            {
                if (string.Equals(args[index], name, StringComparison.Ordinal))
                    return args[index + 1];
            }
            return null;
        }

        private static string ProjectRoot()
        {
            var assets = new DirectoryInfo(Application.dataPath);
            if (assets.Parent == null)
                throw new InvalidOperationException("unable to resolve Unity project root from Application.dataPath.");
            return assets.Parent.FullName;
        }

        private static void WriteEvidence(string projectRoot, string requestedPath, Evidence evidence)
        {
            var absolutePath = Path.IsPathRooted(requestedPath)
                ? requestedPath
                : Path.Combine(projectRoot, requestedPath.Replace('/', Path.DirectorySeparatorChar));
            var directory = Path.GetDirectoryName(absolutePath);
            if (!string.IsNullOrWhiteSpace(directory))
                Directory.CreateDirectory(directory);

            File.WriteAllText(
                absolutePath,
                JsonUtility.ToJson(evidence, true) + Environment.NewLine,
                new UTF8Encoding(false));
        }

        private static string Sha256(string path)
        {
            using var stream = File.OpenRead(path);
            using var sha = SHA256.Create();
            var digest = sha.ComputeHash(stream);
            var builder = new StringBuilder(digest.Length * 2);
            foreach (var value in digest)
                builder.Append(value.ToString("x2", CultureInfo.InvariantCulture));
            return builder.ToString();
        }
    }
}
