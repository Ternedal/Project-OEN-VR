#nullable enable

using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

namespace ProjectOen.Core.Persistence
{
    /// <summary>
    /// Kanonisk JSON efter checksum-definitionen i docs/10: sorterede noegler,
    /// ingen whitespace, UTF-8. Findes kun for at goere checksummen reproducerbar
    /// paa tvaers af Unity, valideringsvaerktoejet og eventuel tooling.
    ///
    /// Bevidst minimal: den serialiserer det save-modellen faktisk indeholder
    /// (dictionaries, lister, string, bool, heltal, decimaltal, null) og intet andet.
    /// </summary>
    public static class CanonicalJson
    {
        public static string Serialize(object? value)
        {
            var sb = new StringBuilder();
            Write(sb, value);
            return sb.ToString();
        }

        static void Write(StringBuilder sb, object? value)
        {
            switch (value)
            {
                case null:
                    sb.Append("null");
                    return;
                case string s:
                    WriteString(sb, s);
                    return;
                case bool b:
                    sb.Append(b ? "true" : "false");
                    return;
                case IDictionary<string, object?> map:
                    WriteObject(sb, map);
                    return;
                case IDictionary dict:
                    WriteObject(sb, ToStringKeyed(dict));
                    return;
                case IEnumerable list when !(value is string):
                    WriteArray(sb, list);
                    return;
                default:
                    WriteNumber(sb, value);
                    return;
            }
        }

        static IDictionary<string, object?> ToStringKeyed(IDictionary dict)
        {
            var result = new Dictionary<string, object?>();
            foreach (DictionaryEntry entry in dict)
            {
                var key = entry.Key as string
                          ?? throw new InvalidOperationException("Kanonisk JSON kraever string-noegler.");
                result[key] = entry.Value;
            }
            return result;
        }

        static void WriteObject(StringBuilder sb, IDictionary<string, object?> map)
        {
            sb.Append('{');
            var first = true;
            // Ordinal sortering. Samme regel som Pythons json.dumps(sort_keys=True),
            // saa tooling og runtime giver samme checksum.
            foreach (var key in map.Keys.OrderBy(k => k, StringComparer.Ordinal))
            {
                if (!first) sb.Append(',');
                first = false;
                WriteString(sb, key);
                sb.Append(':');
                Write(sb, map[key]);
            }
            sb.Append('}');
        }

        static void WriteArray(StringBuilder sb, IEnumerable list)
        {
            sb.Append('[');
            var first = true;
            foreach (var item in list)
            {
                if (!first) sb.Append(',');
                first = false;
                Write(sb, item);
            }
            sb.Append(']');
        }

        static void WriteNumber(StringBuilder sb, object value)
        {
            switch (value)
            {
                case sbyte or byte or short or ushort or int or uint or long or ulong:
                    sb.Append(Convert.ToString(value, CultureInfo.InvariantCulture));
                    return;
                case float f:
                    AppendDouble(sb, f);
                    return;
                case double d:
                    AppendDouble(sb, d);
                    return;
                case decimal m:
                    sb.Append(m.ToString(CultureInfo.InvariantCulture));
                    return;
                default:
                    throw new InvalidOperationException(
                        $"Typen {value.GetType().Name} kan ikke serialiseres kanonisk. " +
                        "Udvid CanonicalJson bevidst frem for at improvisere i kaldstedet.");
            }
        }

        static void AppendDouble(StringBuilder sb, double d)
        {
            if (double.IsNaN(d) || double.IsInfinity(d))
                throw new InvalidOperationException("NaN og Infinity kan ikke repraesenteres i JSON.");
            // Heltalsvaerdier skrives uden decimaler, saa 1.0 og 1 giver samme checksum.
            if (Math.Abs(d % 1) < double.Epsilon && Math.Abs(d) < 1e15)
            {
                sb.Append(((long)d).ToString(CultureInfo.InvariantCulture));
                return;
            }
            sb.Append(d.ToString("R", CultureInfo.InvariantCulture));
        }

        static void WriteString(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (var c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    case '\b': sb.Append("\\b"); break;
                    case '\f': sb.Append("\\f"); break;
                    default:
                        if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
        }
    }
}
