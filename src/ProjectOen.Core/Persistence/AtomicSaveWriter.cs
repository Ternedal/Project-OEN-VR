using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace ProjectOen.Core.Persistence
{
    /// <summary>
    /// Skriveflowet fra docs/06 afsnit 9: serialisér til temp, validér checksum,
    /// omdoeb atomisk, behold forrige checkpoint som backup.
    ///
    /// DEV-003 i docs/13 kraever, at en afbrudt skrivning efterlader det forrige
    /// checkpoint intakt. Derfor sker der aldrig en destruktiv operation paa den
    /// aktive fil, foer den nye er skrevet OG verificeret.
    /// </summary>
    public sealed class AtomicSaveWriter
    {
        readonly IFileSystem _fs;

        public AtomicSaveWriter(IFileSystem? fileSystem = null) => _fs = fileSystem ?? new PhysicalFileSystem();

        public void Write(string activePath, IDictionary<string, object?> save)
        {
            if (string.IsNullOrWhiteSpace(activePath)) throw new ArgumentException(nameof(activePath));

            SaveChecksum.Stamp(save);
            var payload = CanonicalJson.Serialize(save);

            var tempPath = activePath + ".tmp";
            var backupPath = activePath + ".bak";

            _fs.WriteAllText(tempPath, payload);

            // Laes tilbage og verificér, foer noget som helst roeres. Fanger
            // afbrudt eller delvis skrivning, som er hele pointen med DEV-003.
            var readBack = _fs.ReadAllText(tempPath);
            if (readBack != payload)
            {
                _fs.Delete(tempPath);
                throw new IOException("Temp-filen matcher ikke det skrevne payload. Skrivningen er afbrudt.");
            }

            if (_fs.Exists(activePath))
            {
                if (_fs.Exists(backupPath)) _fs.Delete(backupPath);
                _fs.Move(activePath, backupPath);
            }

            _fs.Move(tempPath, activePath);
        }

        /// <summary>Indlaeser aktivt checkpoint. Falder tilbage til backup, hvis det aktive er korrupt.</summary>
        public LoadResult Load(string activePath, Func<string, IDictionary<string, object?>> parse)
        {
            var backupPath = activePath + ".bak";

            if (_fs.Exists(activePath))
            {
                var candidate = TryParse(activePath, parse);
                if (candidate != null) return new LoadResult(candidate, false);
            }

            if (_fs.Exists(backupPath))
            {
                var candidate = TryParse(backupPath, parse);
                if (candidate != null) return new LoadResult(candidate, true);
            }

            return new LoadResult(null, false);
        }

        IDictionary<string, object?>? TryParse(string path, Func<string, IDictionary<string, object?>> parse)
        {
            try
            {
                var parsed = parse(_fs.ReadAllText(path));
                return SaveChecksum.Verify(parsed) ? parsed : null;
            }
            catch
            {
                return null;
            }
        }

        public sealed class LoadResult
        {
            public LoadResult(IDictionary<string, object?>? save, bool fromBackup)
            {
                Save = save;
                FromBackup = fromBackup;
            }

            public IDictionary<string, object?>? Save { get; }
            public bool FromBackup { get; }
            public bool Ok => Save != null;
        }
    }

    /// <summary>Filsystemet bag en grænseflade, saa afbrudte skrivninger kan testes uden headset.</summary>
    public interface IFileSystem
    {
        bool Exists(string path);
        string ReadAllText(string path);
        void WriteAllText(string path, string contents);
        void Move(string from, string to);
        void Delete(string path);
    }

    public sealed class PhysicalFileSystem : IFileSystem
    {
        public bool Exists(string path) => File.Exists(path);
        public string ReadAllText(string path) => File.ReadAllText(path, Encoding.UTF8);
        public void WriteAllText(string path, string contents) => File.WriteAllText(path, contents, new UTF8Encoding(false));
        public void Move(string from, string to) => File.Move(from, to);
        public void Delete(string path) => File.Delete(path);
    }
}
