from typing import List, Dict, Any


class PatchStatistics:
    """Generate statistics about patch applications"""
    
    @staticmethod
    def calculate_statistics(patches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for patches
        
        Args:
            patches: List of paragraph patches
            
        Returns:
            Statistics dictionary
        """
        total_patches = len(patches)
        total_insertions = 0
        total_deletions = 0
        total_chars_inserted = 0
        total_chars_deleted = 0
        
        paragraphs_modified = []
        
        for patch in patches:
            if patch.get("has_changes", False):
                paragraphs_modified.append(patch["paragraph_id"])
                
                summary = patch.get("change_summary", {})
                total_insertions += summary.get("insertions", 0)
                total_deletions += summary.get("deletions", 0)
                total_chars_inserted += summary.get("chars_inserted", 0)
                total_chars_deleted += summary.get("chars_deleted", 0)
        
        return {
            "total_patches": total_patches,
            "paragraphs_modified": len(paragraphs_modified),
            "paragraph_ids": paragraphs_modified,
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "total_chars_inserted": total_chars_inserted,
            "total_chars_deleted": total_chars_deleted,
            "net_char_change": total_chars_inserted - total_chars_deleted
        }
    
    @staticmethod
    def generate_report(patches: List[Dict[str, Any]]) -> str:
        """
        Generate human-readable report
        
        Args:
            patches: List of paragraph patches
            
        Returns:
            Formatted report string
        """
        stats = PatchStatistics.calculate_statistics(patches)
        
        report = []
        report.append("\n" + "="*60)
        report.append("PATCH APPLICATION REPORT")
        report.append("="*60)
        report.append(f"\nTotal patches: {stats['total_patches']}")
        report.append(f"Paragraphs modified: {stats['paragraphs_modified']}")
        report.append(f"Paragraph IDs: {stats['paragraph_ids']}")
        report.append(f"\nOperations:")
        report.append(f"  Insertions: {stats['total_insertions']} ({stats['total_chars_inserted']} chars)")
        report.append(f"  Deletions:  {stats['total_deletions']} ({stats['total_chars_deleted']} chars)")
        report.append(f"  Net change: {stats['net_char_change']:+d} chars")
        report.append("="*60 + "\n")
        
        return "\n".join(report)
