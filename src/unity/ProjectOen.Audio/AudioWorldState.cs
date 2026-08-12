namespace ProjectOen.Audio
{
    public enum AudioBiome : byte
    {
        Beach = 0,
        Jungle = 1,
        Ridge = 2,
        Camp = 3,
    }

    public enum AudioDayPhase : byte
    {
        Day = 0,
        Night = 1,
    }

    /// <summary>
    /// Release-1 storm progression: calm setup, wind, rain/fire pressure, signal finale.
    /// </summary>
    public enum AudioStormPhase : byte
    {
        Calm = 0,
        Wind = 1,
        RainFire = 2,
        Signal = 3,
    }
}
