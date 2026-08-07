using System;

namespace ProjectOen.Core.Numerics
{
    /// <summary>
    /// Minimal vektortype, saa coop-solverens matematik kan testes uden UnityEngine.
    /// Unity-bindingen konverterer til og fra UnityEngine.Vector3 i \u00e9t punkt.
    /// docs/06 afsnit 1: "Gameplay-state ... kan testes uden headset, hvor det er muligt."
    /// </summary>
    public readonly struct Vec3 : IEquatable<Vec3>
    {
        public Vec3(double x, double y, double z) { X = x; Y = y; Z = z; }

        public double X { get; }
        public double Y { get; }
        public double Z { get; }

        public static readonly Vec3 Zero = new Vec3(0, 0, 0);
        public static readonly Vec3 Up = new Vec3(0, 1, 0);

        public static Vec3 operator +(Vec3 a, Vec3 b) => new Vec3(a.X + b.X, a.Y + b.Y, a.Z + b.Z);
        public static Vec3 operator -(Vec3 a, Vec3 b) => new Vec3(a.X - b.X, a.Y - b.Y, a.Z - b.Z);
        public static Vec3 operator *(Vec3 a, double s) => new Vec3(a.X * s, a.Y * s, a.Z * s);
        public static Vec3 operator /(Vec3 a, double s) => new Vec3(a.X / s, a.Y / s, a.Z / s);

        public double SqrMagnitude => X * X + Y * Y + Z * Z;
        public double Magnitude => Math.Sqrt(SqrMagnitude);

        public Vec3 Normalized
        {
            get
            {
                var m = Magnitude;
                return m < 1e-9 ? Zero : this / m;
            }
        }

        public static double Distance(Vec3 a, Vec3 b) => (a - b).Magnitude;
        public static Vec3 Lerp(Vec3 a, Vec3 b, double t) => a + (b - a) * Clamp01(t);
        public static Vec3 Midpoint(Vec3 a, Vec3 b) => (a + b) * 0.5;
        public static double Dot(Vec3 a, Vec3 b) => a.X * b.X + a.Y * b.Y + a.Z * b.Z;

        /// <summary>Begraenser laengden. Grundlaget for max velocity i solveren.</summary>
        public Vec3 ClampMagnitude(double max)
        {
            var m = Magnitude;
            return m <= max || m < 1e-9 ? this : this / m * max;
        }

        static double Clamp01(double v) => v < 0 ? 0 : v > 1 ? 1 : v;

        public bool Equals(Vec3 other) =>
            Math.Abs(X - other.X) < 1e-9 && Math.Abs(Y - other.Y) < 1e-9 && Math.Abs(Z - other.Z) < 1e-9;

        public override bool Equals(object? obj) => obj is Vec3 v && Equals(v);
        public override int GetHashCode() => (X, Y, Z).GetHashCode();
        public override string ToString() => $"({X:0.###},{Y:0.###},{Z:0.###})";
    }
}
