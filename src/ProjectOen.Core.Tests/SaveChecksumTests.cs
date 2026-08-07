using System.Collections.Generic;
using ProjectOen.Core.Persistence;
using Xunit;

namespace ProjectOen.Core.Tests
{
    public class SaveChecksumTests
    {
        /// <summary>
        /// Den vigtigste test i suiten. examples/savegame.example.json indeholder en
        /// checksum beregnet af tools/validate_handoff.py. Hvis runtime-implementeringen
        /// her giver et andet svar, er kontrakten i docs/10 ikke én regel men to -
        /// og save-filer ville blive afvist paa tvaers af tooling og spil.
        /// </summary>
        [Fact]
        public void Matches_the_checksum_in_the_repository_test_vector()
        {
            var save = TestVector.LoadSavegameExample();
            var stored = (string)save["checksum"]!;

            Assert.Equal(stored, SaveChecksum.Compute(save));
            Assert.True(SaveChecksum.Verify(save));
        }

        [Fact]
        public void Detects_a_tampered_field()
        {
            var save = TestVector.LoadSavegameExample();
            save["seed"] = 999999;
            Assert.False(SaveChecksum.Verify(save));
        }

        [Fact]
        public void Key_order_does_not_change_the_checksum()
        {
            var a = new Dictionary<string, object?> { ["b"] = 2, ["a"] = 1, ["c"] = "x" };
            var b = new Dictionary<string, object?> { ["c"] = "x", ["a"] = 1, ["b"] = 2 };
            Assert.Equal(SaveChecksum.Compute(a), SaveChecksum.Compute(b));
        }

        [Fact]
        public void Stamp_makes_the_save_verify()
        {
            var save = new Dictionary<string, object?> { ["schemaVersion"] = 1, ["phase"] = "DAY1_NIGHT" };
            SaveChecksum.Stamp(save);
            Assert.True(SaveChecksum.Verify(save));
            Assert.Matches("^[0-9a-f]{64}$", (string)save["checksum"]!);
        }

        [Fact]
        public void Missing_checksum_does_not_verify()
        {
            var save = new Dictionary<string, object?> { ["schemaVersion"] = 1 };
            Assert.False(SaveChecksum.Verify(save));
        }
    }
}
