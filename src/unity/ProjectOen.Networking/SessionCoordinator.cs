// UNVERIFIED-IN-SANDBOX
// Ikke kompileret. Intet Fusion 2 SDK i skrivemiljøet.
//
// Antagelser om Fusion 2's API, som SKAL efterprøves mod den installerede SDK-version:
//   - Fusion.NetworkRunner med StartGame(StartGameArgs)
//   - StartGameArgs { GameMode, SessionName, PlayerCount, SceneManager }
//   - Fusion.GameMode.Shared
//   - Fusion.INetworkRunnerCallbacks med OnPlayerJoined/OnPlayerLeft/OnDisconnectedFromServer
//   - runner.LocalPlayer, runner.ActivePlayers, runner.IsSharedModeMasterClient
// Meld straks hvis en signatur afviger - jeg har et alternativ klar for hver af dem.

using System;
using System.Threading.Tasks;
using Fusion;
using ProjectOen.Core.Networking;
using UnityEngine;

namespace ProjectOen.Networking
{
    public enum SessionRole { None, Coordinator, Peer }

    /// <summary>
    /// docs/07 §2-3. Fusion 2 Shared Mode, to klienter, privat session med join code.
    ///
    /// ADR-020: der er INGEN live coordinator-handover. Med to spillere findes der ingen
    /// tredje klient at overdrage til - hvis coordinator forsvinder, er sessionen enten
    /// slut, eller den anden klient er per definition ny coordinator. Ved tab: pause,
    /// checkpoint-resume, ny session. Én kodesti i stedet for to, og checkpoint-stien
    /// skal bygges og testes alligevel.
    /// </summary>
    public sealed class SessionCoordinator : MonoBehaviour, INetworkRunnerCallbacks
    {
        [SerializeField] NetworkRunner _runnerPrefab = null!;

        NetworkRunner? _runner;
        readonly System.Random _random = new System.Random();

        public SessionRole Role { get; private set; } = SessionRole.None;
        public string JoinCodeInUse { get; private set; } = "";

        public event Action<string>? SessionFailed;
        public event Action? PeerJoined;
        public event Action? PeerLost;

        public async Task<bool> CreateSessionAsync()
        {
            var code = JoinCode.Generate(_random);
            var ok = await StartAsync(code);
            if (ok) Role = SessionRole.Coordinator;
            return ok;
        }

        public async Task<bool> JoinSessionAsync(string typedCode)
        {
            // Normaliseringen ligger i Core og er testet: små bogstaver, mellemrum,
            // bindestreger og forvekslingstegn rettes; alt andet afvises tydeligt
            // frem for at gætte og joine en fremmed session.
            if (!JoinCode.TryNormalize(typedCode, out var code))
            {
                SessionFailed?.Invoke("Koden er ikke gyldig. Tjek den og prøv igen.");
                return false;
            }

            var ok = await StartAsync(code);
            if (ok) Role = SessionRole.Peer;
            return ok;
        }

        async Task<bool> StartAsync(string code)
        {
            _runner = Instantiate(_runnerPrefab);
            _runner.ProvideInput = true;
            _runner.AddCallbacks(this);

            var result = await _runner.StartGame(new StartGameArgs
            {
                GameMode = GameMode.Shared,
                SessionName = code,
                PlayerCount = 2,          // ADR-002: præcis to spillere
            });

            if (!result.Ok)
            {
                SessionFailed?.Invoke($"Kunne ikke starte session: {result.ShutdownReason}");
                return false;
            }

            JoinCodeInUse = code;
            return true;
        }

        public void OnPlayerJoined(NetworkRunner runner, PlayerRef player)
        {
            if (player != runner.LocalPlayer) PeerJoined?.Invoke();
        }

        public void OnPlayerLeft(NetworkRunner runner, PlayerRef player)
        {
            if (player == runner.LocalPlayer) return;

            // ADR-020. Ingen overdragelse - pause og checkpoint-resume.
            // docs/07 §10 foreslår 90 sekunders reconnect-vindue, men CR-009 kræver,
            // at tallet MÅLES på Quest 2/3 i M2 frem for at gættes: Quest går i standby
            // få sekunder efter aftagning, så den hyppigste virkelige afbrydelse
            // ("jeg tog headsettet af") kan overskride vinduet.
            PeerLost?.Invoke();
        }

        public void OnDisconnectedFromServer(NetworkRunner runner, NetDisconnectReason reason) => PeerLost?.Invoke();

        // Resten af INetworkRunnerCallbacks: tomme med vilje. Fusion kræver dem,
        // men projektet bruger dem ikke, og tomme metoder med en kommentar er
        // ærligere end metoder der lader som om de gør noget.
        public void OnInput(NetworkRunner runner, NetworkInput input) { }
        public void OnInputMissing(NetworkRunner runner, PlayerRef player, NetworkInput input) { }
        public void OnShutdown(NetworkRunner runner, ShutdownReason shutdownReason) { }
        public void OnConnectedToServer(NetworkRunner runner) { }
        public void OnSceneLoadDone(NetworkRunner runner) { }
        public void OnSceneLoadStart(NetworkRunner runner) { }
    }
}
