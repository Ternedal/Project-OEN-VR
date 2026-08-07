using ProjectOen.Core.Networking;
using Xunit;

namespace ProjectOen.Core.Tests
{
    public class CompatibilityHandshakeTests
    {
        static BuildIdentity Build(string profile, int protocol = 1, string content = "stormnatten-1.0",
                                   int schema = 1, string version = "0.4.0", params string[] flags) =>
            new BuildIdentity(version, protocol, content, schema, profile, flags);

        /// <summary>COMPAT-001: Q1 legacy joiner Q3 enhanced med samme protocol/content/schema.</summary>
        [Fact]
        public void Quest_1_legacy_may_play_with_Quest_3_enhanced()
        {
            var q1 = Build("Q1_LEGACY");
            var q3 = Build("Q3_ENHANCED");
            Assert.True(CompatibilityHandshake.Evaluate(q1, q3).Accepted);
        }

        [Fact]
        public void Different_game_version_string_alone_does_not_block()
        {
            var a = Build("Q2_BASE", version: "0.4.0");
            var b = Build("Q3_ENHANCED", version: "0.4.1");
            Assert.True(CompatibilityHandshake.Evaluate(a, b).Accepted);
        }

        [Fact]
        public void Protocol_mismatch_is_rejected()
        {
            var result = CompatibilityHandshake.Evaluate(Build("Q2_BASE", protocol: 1), Build("Q3_ENHANCED", protocol: 2));
            Assert.False(result.Accepted);
            Assert.Equal("PROTOCOL_MISMATCH", result.Code);
        }

        /// <summary>COMPAT-002: klokkeskaevt content hash afvises foer spawn.</summary>
        [Fact]
        public void Content_hash_mismatch_is_rejected()
        {
            var result = CompatibilityHandshake.Evaluate(
                Build("Q1_LEGACY", content: "stormnatten-1.0"),
                Build("Q3_ENHANCED", content: "stormnatten-1.1"));
            Assert.False(result.Accepted);
            Assert.Equal("CONTENT_MISMATCH", result.Code);
        }

        [Fact]
        public void Save_schema_mismatch_is_rejected()
        {
            var result = CompatibilityHandshake.Evaluate(Build("Q2_BASE", schema: 1), Build("Q2_BASE", schema: 2));
            Assert.False(result.Accepted);
            Assert.Equal("SAVE_SCHEMA_MISMATCH", result.Code);
        }

        [Fact]
        public void A_feature_flag_present_on_only_one_side_is_rejected_both_ways()
        {
            var withFlag = Build("Q2_BASE", flags: new[] { "COOP_ROPE_V2" });
            var without = Build("Q1_LEGACY");

            Assert.Equal("FEATURE_MISSING", CompatibilityHandshake.Evaluate(withFlag, without).Code);
            Assert.Equal("FEATURE_MISSING", CompatibilityHandshake.Evaluate(without, withFlag).Code);
        }

        [Fact]
        public void Rejection_carries_a_message_a_player_can_act_on()
        {
            var result = CompatibilityHandshake.Evaluate(Build("Q2_BASE", protocol: 1), Build("Q2_BASE", protocol: 3));
            Assert.False(string.IsNullOrWhiteSpace(result.Message));
            Assert.Contains("opdatere", result.Message);
        }
    }
}
