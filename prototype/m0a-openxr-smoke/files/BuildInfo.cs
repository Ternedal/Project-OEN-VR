// M0a smoke test — PROJECT ØEN
// Minimal buildmetadata. Den rigtige BuildInfo bygges i M0b som del af
// ProjectOen.Platform; denne findes kun, så logcat-outputtet kan spores
// til en konkret build under testen.
//
// Verifikationsstatus: ikke kompileret i sandbox.

using UnityEngine;

public static class BuildInfo
{
    public const string Milestone = "M0a";
    public const string Profile   = "SMOKE";

    public static string Describe() =>
        $"{Milestone}/{Profile} unity={Application.unityVersion} " +
        $"device={SystemInfo.deviceModel} gfx={SystemInfo.graphicsDeviceType}";

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    static void LogAtStartup() => Debug.Log($"[OenM0a] BuildInfo: {Describe()}");
}
