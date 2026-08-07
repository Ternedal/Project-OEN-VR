# Manifest-patch til M0a

**Erstat ikke manifestet.** Unity genererer `Assets/Plugins/Android/AndroidManifest.xml`, når du sætter flueben i *Custom Main Manifest*. Activity-klassen i den fil afhænger af Unity-version og *Application Entry Point* (`UnityPlayerActivity` vs. `UnityPlayerGameActivity`). Skriver du den forkerte ind, starter appen ikke — og du vil fejlagtigt tro, det er Quest 1's skyld.

Åbn den fil Unity lavede, og tilføj kun dette.

## 1. VR-launchkategori

Find `<intent-filter>` inde i `<activity>` — den med `MAIN` og `LAUNCHER`. Tilføj én linje:

```xml
<category android:name="com.oculus.intent.category.VR" />
```

Uden den starter appen som et fladt panel i Quest-hjemmet i stedet for immersivt. Det er den hyppigste årsag til "den virker ikke i VR".

## 2. Headtracking-feature

Inde i `<manifest>`, uden for `<application>`:

```xml
<uses-feature android:name="android.hardware.vr.headtracking" android:version="1" android:required="true" />
```

## 3. Internet (til M0b, ikke M0a)

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

Photon skal bruge den. Tag den med nu, så du ikke skal bygge om.

## 4. Focus aware

Inde i `<activity>`:

```xml
<meta-data android:name="com.oculus.vr.focusaware" android:value="true" />
```

## Sådan ser resultatet ud

Skelet — din faktiske activity-linje kan afvige, og **det er din der gælder**:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <uses-permission android:name="android.permission.INTERNET" />
  <uses-feature android:name="android.hardware.vr.headtracking"
                android:version="1" android:required="true" />
  <application>
    <activity android:name="<DEN UNITY SELV SKREV>"
              android:theme="@style/UnityThemeSelector"
              android:exported="true">
      <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
        <category android:name="com.oculus.intent.category.VR" />
      </intent-filter>
      <meta-data android:name="unityplayer.UnityActivity" android:value="true" />
      <meta-data android:name="com.oculus.vr.focusaware" android:value="true" />
    </activity>
  </application>
</manifest>
```

## Om `com.oculus.supportedDevices`

Du vil støde på `<meta-data android:name="com.oculus.supportedDevices" android:value="quest|quest2|..." />` i ældre vejledninger.

**[ANTAGELSE — bekræft ved test]** Det felt er butiksmetadata og bør ikke blokere sideload. Tilføj det ikke i M0a: det introducerer en ekstra fejlkilde i præcis den test, der skal isolere én ting. Bliver det relevant i M0b, håndteres det pr. buildprofil, som `config/UNITY_PROJECT_SETTINGS_CHECKLIST.md` allerede foreskriver.
