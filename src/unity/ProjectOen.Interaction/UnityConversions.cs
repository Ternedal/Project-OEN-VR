// UNVERIFIED-IN-SANDBOX
// Ikke kompileret. Ingen Unity Editor i skrivemiljøet.
// Antagelser om API: UnityEngine.Vector3 har (float x, float y, float z)-konstruktør.
// Det er stabilt på tværs af alle Unity-versioner og er den mindst risikable fil her.

using ProjectOen.Core.Numerics;
using UnityEngine;

namespace ProjectOen.Interaction
{
    /// <summary>
    /// Det eneste sted i kodebasen, hvor Core's Vec3 møder UnityEngine.Vector3.
    ///
    /// Grunden til at Core overhovedet har sin egen vektortype: uden den kan
    /// coop-solverens opførsel ikke testes uden headset - og det var netop en
    /// solvertest, der afslørede, at hastighedsloftet gjorde én-hånds- og
    /// to-hånds-tilstanden identiske. Se docs/33.
    /// </summary>
    public static class UnityConversions
    {
        public static Vector3 ToUnity(this Vec3 v) => new Vector3((float)v.X, (float)v.Y, (float)v.Z);

        public static Vec3 ToCore(this Vector3 v) => new Vec3(v.x, v.y, v.z);
    }
}
