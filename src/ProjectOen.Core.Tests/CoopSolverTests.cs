using ProjectOen.Core.Interaction;
using ProjectOen.Core.Numerics;
using Xunit;
using Xunit.Abstractions;

namespace ProjectOen.Core.Tests
{
    /// <summary>
    /// NET-002 i docs/13 kraever, at den tunge kasse giver identisk resultat paa begge
    /// klienter. Det kan kun bevises paa hardware - men solverens opfoersel kan bevises her:
    /// konvergens, hastighedsloft mod jitter, og gradvist kvalitetsfald frem for nulstilling.
    /// </summary>
    public class CoopSolverTests
    {
        readonly ITestOutputHelper _out;
        public CoopSolverTests(ITestOutputHelper output) => _out = output;

        const double Dt = 1.0 / 72.0;   // 72 Hz, releasekravet paa Quest 2

        static CoopSolver Held(out Vec3 left, out Vec3 right, CoopSolverConfig? cfg = null)
        {
            var solver = new CoopSolver(cfg);
            solver.Reset(Vec3.Zero);
            left = new Vec3(-0.4, 1.0, 0.5);
            right = new Vec3(0.4, 1.0, 0.5);
            return solver;
        }

        [Fact]
        public void Converges_toward_the_midpoint_of_two_hands()
        {
            var solver = Held(out var left, out var right);
            var target = Vec3.Midpoint(left, right);

            for (var i = 0; i < 120; i++) solver.Step(left, right, Dt);

            Assert.True(Vec3.Distance(solver.Position, target) < 0.01,
                $"Kom kun til {solver.Position}, maalet var {target}.");
            Assert.Equal(CoopObjectPhase.HeldByBoth, solver.Phase);
        }

        /// <summary>
        /// Hastighedsloftet er det, der holder to klienters jitter ude af resultatet.
        /// Uden det ville en enkelt daarlig pose-pakke teleportere kassen.
        /// </summary>
        [Fact]
        public void Never_exceeds_the_speed_ceiling_even_on_a_teleporting_hand()
        {
            var cfg = new CoopSolverConfig { MaxLinearSpeed = 2.0 };
            var solver = Held(out var left, out var right, cfg);

            var previous = solver.Position;
            var maxStep = 0.0;
            for (var i = 0; i < 60; i++)
            {
                // Simulerer en pakke, hvor haanden hopper 50 meter vaek.
                var glitched = i == 30 ? new Vec3(50, 50, 50) : right;
                var step = solver.Step(left, glitched, Dt);
                var moved = Vec3.Distance(step.Position, previous);
                if (moved > maxStep) maxStep = moved;
                previous = step.Position;
            }

            _out.WriteLine($"stoerste enkeltskridt: {maxStep:0.0000} m (loft {cfg.MaxLinearSpeed * Dt:0.0000} m)");
            Assert.True(maxStep <= cfg.MaxLinearSpeed * Dt + 1e-9);
        }

        /// <summary>docs/04 afsnit 7: kvalitet falder gradvist frem for at nulstille.</summary>
        [Fact]
        public void Losing_the_grip_degrades_quality_gradually_and_never_instantly()
        {
            var solver = Held(out var left, out var right);
            for (var i = 0; i < 30; i++) solver.Step(left, right, Dt);
            Assert.Equal(1.0, solver.Quality, 3);

            // Spiller A traekker haanden langt vaek - gribeafstanden sprænges.
            var strained = new Vec3(3.0, 1.0, 0.5);
            var afterOneFrame = solver.Step(left, strained, Dt);

            Assert.True(afterOneFrame.Quality > 0.9,
                $"Ét frame kostede {1 - afterOneFrame.Quality:0.###} kvalitet - det er en nulstilling, ikke et fald.");

            for (var i = 0; i < 200; i++) solver.Step(left, strained, Dt);
            _out.WriteLine($"kvalitet efter ~2,8 s daarligt greb: {solver.Quality:0.###}");
            Assert.True(solver.Quality < 0.5, "Vedvarende daarligt greb skal koste maerkbart.");
        }

        [Fact]
        public void Quality_recovers_when_the_grip_is_restored()
        {
            var solver = Held(out var left, out var right);
            var strained = new Vec3(3.0, 1.0, 0.5);
            for (var i = 0; i < 100; i++) solver.Step(left, strained, Dt);
            var low = solver.Quality;

            for (var i = 0; i < 100; i++) solver.Step(left, right, Dt);

            Assert.True(solver.Quality > low, "Kvaliteten skal kunne genvindes - ellers er en fejl permanent.");
        }

        /// <summary>Med \u00e9n haand er objektet tungere. Det er selve begrundelsen for coop-mekanikken.</summary>
        [Fact]
        public void One_hand_moves_the_object_more_slowly_than_two()
        {
            var target = new Vec3(0, 1.0, 0.5);

            var two = new CoopSolver(); two.Reset(Vec3.Zero);
            var one = new CoopSolver(); one.Reset(Vec3.Zero);

            for (var i = 0; i < 20; i++)
            {
                two.Step(new Vec3(-0.4, 1.0, 0.5), new Vec3(0.4, 1.0, 0.5), Dt);
                one.Step(target, null, Dt);
            }

            Assert.True(Vec3.Distance(two.Position, target) < Vec3.Distance(one.Position, target));
            Assert.Equal(CoopObjectPhase.HeldByOne, one.Phase);
        }

        [Fact]
        public void Releasing_both_hands_leaves_the_object_where_it_was()
        {
            var solver = Held(out var left, out var right);
            for (var i = 0; i < 50; i++) solver.Step(left, right, Dt);
            var resting = solver.Position;

            var step = solver.Step(null, null, Dt);

            Assert.Equal(CoopObjectPhase.Released, solver.Phase);
            Assert.Equal(resting, step.Position);
        }

        /// <summary>Kvaliteten er det, der bliver til PhysicalExecution i udfaldsformlen.</summary>
        [Fact]
        public void Quality_stays_within_zero_and_one()
        {
            var solver = Held(out var left, out _);
            var wild = new Vec3(9, -4, 12);
            for (var i = 0; i < 500; i++)
            {
                var step = solver.Step(left, i % 3 == 0 ? wild : (Vec3?)null, Dt);
                Assert.InRange(step.Quality, 0.0, 1.0);
            }
        }
    }
}
