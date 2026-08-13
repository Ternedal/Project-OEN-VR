using UnityEditor;

namespace ProjectOen.Art.Editor
{
    public static class ProductionArtBatchVerification
    {
        [MenuItem("Project OEN/Art/Run Full On-Machine Verification")]
        public static void RunAll()
        {
            ProductionArtShowcaseAudit.AuditShowcase();
        }
    }
}
