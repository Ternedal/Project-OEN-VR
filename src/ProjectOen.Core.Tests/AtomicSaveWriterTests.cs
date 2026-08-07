using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using ProjectOen.Core.Persistence;
using Xunit;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// DEV-003 i docs/13: en afbrudt checkpoint-skrivning skal efterlade
    /// det forrige checkpoint intakt og indlaeseligt.
    /// </summary>
    public class AtomicSaveWriterTests
    {
        sealed class FakeFileSystem : IFileSystem
        {
            public readonly Dictionary<string, string> Files = new();
            public Func<string, string, bool>? FailWriteWhen;

            public bool Exists(string path) => Files.ContainsKey(path);
            public string ReadAllText(string path) => Files.TryGetValue(path, out var v)
                ? v : throw new FileNotFoundException(path);

            public void WriteAllText(string path, string contents)
            {
                if (FailWriteWhen != null && FailWriteWhen(path, contents))
                {
                    // Simulerer strømsvigt midt i skrivningen: halvdelen naar disken.
                    Files[path] = contents.Substring(0, contents.Length / 2);
                    return;
                }
                Files[path] = contents;
            }

            public void Move(string from, string to)
            {
                Files[to] = Files[from];
                Files.Remove(from);
            }

            public void Delete(string path) => Files.Remove(path);
        }

        static Dictionary<string, object?> Save(int revision) => new()
        {
            ["schemaVersion"] = 1L,
            ["revision"] = (long)revision,
            ["phase"] = "DAY2_PLANNING",
        };

        static IDictionary<string, object?> Parse(string json)
        {
            using var doc = JsonDocument.Parse(json);
            var map = new Dictionary<string, object?>();
            foreach (var p in doc.RootElement.EnumerateObject())
            {
                map[p.Name] = p.Value.ValueKind switch
                {
                    JsonValueKind.String => p.Value.GetString(),
                    JsonValueKind.Number => p.Value.GetInt64(),
                    _ => throw new InvalidOperationException("Testens parser er bevidst minimal.")
                };
            }
            return map;
        }

        [Fact]
        public void Writes_and_reads_back_a_verified_checkpoint()
        {
            var fs = new FakeFileSystem();
            var writer = new AtomicSaveWriter(fs);

            writer.Write("save.json", Save(1));
            var loaded = writer.Load("save.json", Parse);

            Assert.True(loaded.Ok);
            Assert.False(loaded.FromBackup);
            Assert.Equal(1L, loaded.Save!["revision"]);
        }

        [Fact]
        public void Keeps_the_previous_checkpoint_as_backup()
        {
            var fs = new FakeFileSystem();
            var writer = new AtomicSaveWriter(fs);

            writer.Write("save.json", Save(1));
            writer.Write("save.json", Save(2));

            Assert.True(fs.Exists("save.json.bak"));
            Assert.Equal(2L, writer.Load("save.json", Parse).Save!["revision"]);
        }

        [Fact]
        public void An_interrupted_write_leaves_the_previous_checkpoint_intact()
        {
            var fs = new FakeFileSystem();
            var writer = new AtomicSaveWriter(fs);
            writer.Write("save.json", Save(1));

            fs.FailWriteWhen = (path, _) => path.EndsWith(".tmp", StringComparison.Ordinal);

            Assert.Throws<IOException>(() => writer.Write("save.json", Save(2)));

            // Det aktive checkpoint er uroert, og temp-filen er ryddet op.
            Assert.False(fs.Exists("save.json.tmp"));
            var loaded = writer.Load("save.json", Parse);
            Assert.True(loaded.Ok);
            Assert.Equal(1L, loaded.Save!["revision"]);
        }

        [Fact]
        public void Falls_back_to_the_backup_when_the_active_file_is_corrupt()
        {
            var fs = new FakeFileSystem();
            var writer = new AtomicSaveWriter(fs);
            writer.Write("save.json", Save(1));
            writer.Write("save.json", Save(2));

            fs.Files["save.json"] = "{\"schemaVersion\":1,\"revision\":2,\"phase\":\"DAY2_PLANNING\",\"checksum\":\"deadbeef\"}";

            var loaded = writer.Load("save.json", Parse);
            Assert.True(loaded.Ok);
            Assert.True(loaded.FromBackup);
            Assert.Equal(1L, loaded.Save!["revision"]);
        }
    }
}
