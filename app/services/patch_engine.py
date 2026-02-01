from diff_match_patch import diff_match_patch
from typing import List, Dict, Any, Tuple
from app.core.logging import logger


class PatchEngine:
    """Generate structured patches using diff-match-patch"""
    
    def __init__(self):
        """Initialize diff-match-patch engine"""
        self.dmp = diff_match_patch()
        # Configure for better semantic diffs
        self.dmp.Diff_Timeout = 2.0
        self.dmp.Diff_EditCost = 4
    
    def generate_diff(
        self, 
        original_text: str, 
        replacement_text: str
    ) -> List[Tuple[int, str]]:
        """
        Generate character-level diff between original and replacement text
        
        Args:
            original_text: Original text
            replacement_text: New text
            
        Returns:
            List of diff tuples: (operation, text)
            Operations: -1 (delete), 0 (equal), 1 (insert)
        """
        diffs = self.dmp.diff_main(original_text, replacement_text)
        
        # Clean up for semantic meaning
        self.dmp.diff_cleanupSemantic(diffs)
        
        logger.info(f"Generated {len(diffs)} diff operations")
        return diffs
    
    def generate_patch(
        self, 
        original_text: str, 
        replacement_text: str
    ) -> Dict[str, Any]:
        """
        Generate structured patch with operations
        
        Args:
            original_text: Original text
            replacement_text: New text
            
        Returns:
            Dictionary with patch operations
        """
        diffs = self.generate_diff(original_text, replacement_text)
        
        operations = []
        position = 0
        
        for op, text in diffs:
            operation_type = self._get_operation_type(op)
            
            operations.append({
                "type": operation_type,
                "text": text,
                "position": position,
                "length": len(text)
            })
            
            # Update position (only for delete and equal operations)
            if op in [-1, 0]:
                position += len(text)
        
        patch_data = {
            "original_text": original_text,
            "replacement_text": replacement_text,
            "operations": operations,
            "total_operations": len(operations),
            "has_changes": any(op["type"] in ["insert", "delete"] for op in operations)
        }
        
        logger.info(
            f"Patch generated: {len(operations)} operations, "
            f"has_changes={patch_data['has_changes']}"
        )
        
        return patch_data
    
    def _get_operation_type(self, op: int) -> str:
        """Convert numeric operation to string type"""
        operation_map = {
            -1: "delete",
            0: "equal",
            1: "insert"
        }
        return operation_map.get(op, "unknown")
    
    def calculate_similarity(
        self, 
        original_text: str, 
        replacement_text: str
    ) -> float:
        """
        Calculate similarity percentage between two texts
        
        Args:
            original_text: Original text
            replacement_text: New text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        diffs = self.generate_diff(original_text, replacement_text)
        
        total_chars = max(len(original_text), len(replacement_text))
        if total_chars == 0:
            return 1.0
        
        equal_chars = sum(len(text) for op, text in diffs if op == 0)
        similarity = equal_chars / total_chars
        
        logger.info(f"Similarity: {similarity:.2%}")
        return similarity
    
    def get_change_summary(self, patch_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Get summary of changes in a patch
        
        Args:
            patch_data: Patch dictionary
            
        Returns:
            Summary with counts
        """
        operations = patch_data.get("operations", [])
        
        summary = {
            "total_operations": len(operations),
            "insertions": sum(1 for op in operations if op["type"] == "insert"),
            "deletions": sum(1 for op in operations if op["type"] == "delete"),
            "equal": sum(1 for op in operations if op["type"] == "equal"),
            "chars_inserted": sum(op["length"] for op in operations if op["type"] == "insert"),
            "chars_deleted": sum(op["length"] for op in operations if op["type"] == "delete")
        }
        
        return summary
    
    def apply_patch_preview(self, patch_data: Dict[str, Any]) -> str:
        """
        Generate preview of what text would look like after patch
        
        Args:
            patch_data: Patch dictionary
            
        Returns:
            Resulting text after applying patch
        """
        result = []
        
        for op in patch_data.get("operations", []):
            if op["type"] in ["insert", "equal"]:
                result.append(op["text"])
        
        return "".join(result)
    
    def validate_patch(self, patch_data: Dict[str, Any]) -> bool:
        """
        Validate that patch can be applied correctly
        
        Args:
            patch_data: Patch dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if applying patch gives us the replacement text
            preview = self.apply_patch_preview(patch_data)
            expected = patch_data.get("replacement_text", "")
            
            is_valid = preview == expected
            
            if not is_valid:
                logger.error(f"Patch validation failed: preview != expected")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Patch validation error: {str(e)}")
            return False


class ParagraphPatchGenerator:
    """Generate patches for multiple paragraphs"""
    
    def __init__(self):
        """Initialize patch generator"""
        self.engine = PatchEngine()
    
    def generate_paragraph_patches(
        self,
        paragraph_changes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate patches for multiple paragraphs
        
        Args:
            paragraph_changes: List of dicts with paragraph_id, original_text, replacement_text, reasoning
            
        Returns:
            List of paragraph patch dictionaries
        """
        patches = []
        
        for change in paragraph_changes:
            paragraph_id = change.get("paragraph_id")
            original_text = change.get("original_text", "")
            replacement_text = change.get("replacement_text", "")
            reasoning = change.get("reasoning", "")
            
            # Generate patch
            patch_data = self.engine.generate_patch(original_text, replacement_text)
            
            # Create paragraph patch
            para_patch = {
                "paragraph_id": paragraph_id,
                "paragraph_index": change.get("paragraph_index", paragraph_id),
                "original_text": original_text,
                "replacement_text": replacement_text,
                "operations": patch_data["operations"],
                "reasoning": reasoning,
                "has_changes": patch_data["has_changes"],
                "change_summary": self.engine.get_change_summary(patch_data)
            }
            
            patches.append(para_patch)
            
            logger.info(
                f"Generated patch for paragraph {paragraph_id}: "
                f"{para_patch['change_summary']['insertions']} insertions, "
                f"{para_patch['change_summary']['deletions']} deletions"
            )
        
        return patches
    
    def validate_all_patches(self, patches: List[Dict[str, Any]]) -> bool:
        """
        Validate all paragraph patches
        
        Args:
            patches: List of paragraph patches
            
        Returns:
            True if all valid, False otherwise
        """
        for patch in patches:
            patch_data = {
                "original_text": patch["original_text"],
                "replacement_text": patch["replacement_text"],
                "operations": patch["operations"]
            }
            
            if not self.engine.validate_patch(patch_data):
                logger.error(f"Invalid patch for paragraph {patch['paragraph_id']}")
                return False
        
        return True
