#nullable enable

using System;
using System.Text.RegularExpressions;

namespace ProjectOen.Core.Ids
{
    /// <summary>
    /// docs/16: "Ingen string-baserede IDs i spredt kode; brug typed IDs/wrappers."
    /// Moenstrene kommer fra docs/10 og er de samme, som JSON-skemaerne haandhaever.
    /// </summary>
    public abstract class TypedId : IEquatable<TypedId>
    {
        public string Value { get; }

        protected TypedId(string value, string prefix, Regex pattern)
        {
            if (string.IsNullOrWhiteSpace(value))
                throw new ArgumentException($"{prefix} id maa ikke vaere tomt.", nameof(value));
            if (!pattern.IsMatch(value))
                throw new FormatException($"'{value}' matcher ikke moenstret for {prefix} ({pattern}).");
            Value = value;
        }

        public override string ToString() => Value;
        public bool Equals(TypedId? other) => other is object && GetType() == other.GetType() && Value == other.Value;
        public override bool Equals(object? obj) => Equals(obj as TypedId);
        public override int GetHashCode() => (GetType().GetHashCode() * 397) ^ Value.GetHashCode();
    }

    public sealed class ScenarioId : TypedId
    {
        static readonly Regex Pattern = new Regex(@"^SCN_[A-Z0-9_]+_\d{3}$", RegexOptions.Compiled);
        public ScenarioId(string value) : base(value, "SCN", Pattern) { }
    }

    public sealed class EventId : TypedId
    {
        static readonly Regex Pattern = new Regex(@"^EVT_[A-Z0-9_]+_\d{3}$", RegexOptions.Compiled);
        public EventId(string value) : base(value, "EVT", Pattern) { }
    }

    public sealed class ItemId : TypedId
    {
        static readonly Regex Pattern = new Regex(@"^ITM_[A-Z0-9_]+_\d{3}$", RegexOptions.Compiled);
        public ItemId(string value) : base(value, "ITM", Pattern) { }
    }

    public sealed class RecipeId : TypedId
    {
        static readonly Regex Pattern = new Regex(@"^RCP_[A-Z0-9_]+_\d{3}$", RegexOptions.Compiled);
        public RecipeId(string value) : base(value, "RCP", Pattern) { }
    }

    public sealed class InteractionId : TypedId
    {
        static readonly Regex Pattern = new Regex(@"^INT_[A-Z0-9_]+_\d{3}$", RegexOptions.Compiled);
        public InteractionId(string value) : base(value, "INT", Pattern) { }
    }
}
