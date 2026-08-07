using System;
using System.Linq;
using ProjectOen.Core.Networking;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    public class JoinCodeTests
    {
        readonly ITestOutputHelper _out;
        public JoinCodeTests(ITestOutputHelper output) => _out = output;

        /// <summary>
        /// Koden læses højt tværs gennem en stue af en person med headset på.
        /// Forvekslingspar er derfor ikke kosmetik - de er den hyppigste årsag til
        /// "jeg kan ikke joine".
        /// </summary>
        [Theory]
        [InlineData('O')] [InlineData('0')]
        [InlineData('I')] [InlineData('1')] [InlineData('L')]
        [InlineData('S')] [InlineData('5')]
        [InlineData('B')] [InlineData('8')]
        [InlineData('Z')] [InlineData('2')]
        public void The_alphabet_excludes_every_confusable_character(char c) =>
            Assert.DoesNotContain(c, JoinCode.Alphabet);

        [Fact]
        public void Generates_codes_of_the_requested_length_from_the_alphabet()
        {
            var rng = new Random(2026);
            for (var i = 0; i < 200; i++)
            {
                var code = JoinCode.Generate(rng);
                Assert.Equal(JoinCode.DefaultLength, code.Length);
                Assert.All(code, c => Assert.Contains(c, JoinCode.Alphabet));
                Assert.True(JoinCode.IsValid(code));
            }
        }

        [Fact]
        public void Lowercase_spaces_and_dashes_are_accepted()
        {
            Assert.True(JoinCode.TryNormalize(" ac-de fg ", out var n));
            Assert.Equal("ACDEFG", n);
        }

        [Theory]
        [InlineData("ACDEFO", "ACDEFQ")]   // O -> Q
        [InlineData("ACDEF1", "ACDEFJ")]   // 1 -> J
        [InlineData("ACDEF5", "ACDEFX")]   // 5 -> X
        public void Confusable_input_is_mapped_rather_than_rejected(string typed, string expected)
        {
            Assert.True(JoinCode.TryNormalize(typed, out var n));
            Assert.Equal(expected, n);
        }

        [Fact]
        public void Garbage_is_rejected_instead_of_guessed()
        {
            // En forkert kode skal fejle tydeligt. Et gæt kunne joine en fremmed session.
            Assert.False(JoinCode.TryNormalize("AC#DEF", out _));
            Assert.False(JoinCode.TryNormalize("", out _));
            Assert.False(JoinCode.TryNormalize("AB", out _));
            Assert.False(JoinCode.TryNormalize("ACDEFGHJKM", out _));
        }

        /// <summary>
        /// Med to spillere og en privat session er kollisionsrisikoen ikke sikkerhed,
        /// men irritation. Tallet er alligevel værd at kende.
        /// </summary>
        [Fact]
        public void Keyspace_is_large_enough_that_a_collision_is_not_a_practical_concern()
        {
            var keyspace = System.Math.Pow(JoinCode.Alphabet.Length, JoinCode.DefaultLength);
            _out.WriteLine($"alfabet {JoinCode.Alphabet.Length} tegn, længde {JoinCode.DefaultLength} => {keyspace:N0} kombinationer");
            Assert.True(keyspace > 100_000_000);
        }

        [Fact]
        public void Generated_codes_survive_a_round_trip_through_normalization()
        {
            var rng = new Random(7);
            for (var i = 0; i < 100; i++)
            {
                var code = JoinCode.Generate(rng);
                Assert.True(JoinCode.TryNormalize(code.ToLowerInvariant(), out var n));
                Assert.Equal(code, n);
            }
        }
    }
}
