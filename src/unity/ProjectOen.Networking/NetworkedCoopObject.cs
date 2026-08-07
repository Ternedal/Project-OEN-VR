// UNVERIFIED-IN-SANDBOX
// Ikke kompileret. Intet Fusion 2 SDK i skrivemiljøet.
//
// Antagelser om Fusion 2's API, som SKAL efterprøves:
//   - Fusion.NetworkBehaviour med FixedUpdateNetwork() og Spawned()
//   - [Networked] properties med automatisk change detection
//   - Object.HasStateAuthority / Object.StateAuthority
//   - [Networked, Capacity(2)] NetworkArray<T> til per-spiller data
//   - Runner.DeltaTime i FixedUpdateNetwork
// Bemærk især NetworkArray: hvis signaturen afviger, kan de to hand targets
// i stedet ligge som to separate [Networked]-properties. Det er en trivial ændring.

using Fusion;
using ProjectOen.Core.Interaction;
using ProjectOen.Core.Numerics;
using ProjectOen.Interaction;
using UnityEngine;

namespace ProjectOen.Networking
{
    /// <summary>
    /// docs/07 §8 og ADR-012: den tunge fælles kasse. Netværket sender hand targets
    /// og quality samples - ikke kræfter, ikke rigidbody-streams.
    ///
    /// Denne klasse indeholder INGEN solvermatematik. Den ligger i
    /// ProjectOen.Core.Interaction.CoopSolver, hvor den er testet uden headset -
    /// og hvor en test afslørede, at hastighedsloftet gjorde én-hånds- og
    /// to-hånds-tilstanden identiske ud over få centimeter. Se docs/33.
    ///
    /// Ansvarsfordelingen er hele grunden til, at den fejl blev fundet før hardware.
    /// </summary>
    public sealed class NetworkedCoopObject : NetworkBehaviour
    {
        [SerializeField] float _gripSpan = 0.8f;
        [SerializeField] float _maxLinearSpeed = 2.0f;

        readonly CoopSolver _solver = new CoopSolver();

        /// <summary>Hver spiller ejer sit eget hand target. Ingen ejer resultatet.</summary>
        [Networked, Capacity(2)] NetworkArray<Vector3> HandTargets { get; }
        [Networked, Capacity(2)] NetworkArray<bool> HandGripping { get; }

        /// <summary>Løst af state authority. De øvrige klienter læser og interpolerer.</summary>
        [Networked] Vector3 SolvedPosition { get; set; }
        [Networked] float Quality { get; set; }
        [Networked] int SolverPhase { get; set; }

        public CoopObjectPhase Phase => (CoopObjectPhase)SolverPhase;
        public float CurrentQuality => Quality;

        public override void Spawned()
        {
            _solver.Reset(transform.position.ToCore());
            if (Object.HasStateAuthority)
            {
                SolvedPosition = transform.position;
                Quality = 1f;
            }
        }

        /// <summary>Kaldes lokalt af interaktionslaget, når spilleren griber eller slipper.</summary>
        public void SubmitHandTarget(int playerSlot, Vector3 worldPosition, bool gripping)
        {
            if (playerSlot < 0 || playerSlot > 1) return;
            HandTargets.Set(playerSlot, worldPosition);
            HandGripping.Set(playerSlot, gripping);
        }

        public override void FixedUpdateNetwork()
        {
            if (Object.HasStateAuthority)
            {
                Vec3? left = HandGripping[0] ? HandTargets[0].ToCore() : (Vec3?)null;
                Vec3? right = HandGripping[1] ? HandTargets[1].ToCore() : (Vec3?)null;

                var step = _solver.Step(left, right, Runner.DeltaTime);

                SolvedPosition = step.Position.ToUnity();
                Quality = (float)step.Quality;
                SolverPhase = (int)_solver.Phase;
            }

            // Alle klienter - inkl. authority - viser den samme replikerede værdi.
            // Ingen lokal ekstrapolation af objektet: den ville netop genindføre
            // den divergens, ADR-012 er skrevet for at undgå.
            transform.position = SolvedPosition;
        }

        /// <summary>
        /// Kvaliteten er dét, der bliver PhysicalExecution i udfaldsformlen.
        /// Se docs/33: modstand kan højst trække udfaldet ét trin ned fra det,
        /// præstationen fortjente - en perfekt udført sekvens kan koste dyrt,
        /// men kan aldrig blive "fejl med fremdrift".
        /// </summary>
        public double SampleForOutcome() => Quality;
    }
}
