import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.patch_engine import PatchEngine, ParagraphPatchGenerator
from app.core.logging import logger
import json


def test_basic_patch():
    """Test basic patch generation"""
    print("\n" + "="*60)
    print("TEST 1: Basic Text Replacement")
    print("="*60)
    
    engine = PatchEngine()
    
    original = "The employee shall report to the Manager."
    replacement = "The employee shall report to the Chief Technology Officer."
    
    patch = engine.generate_patch(original, replacement)
    
    print(f"\nOriginal:  {original}")
    print(f"Replacement: {replacement}")
    print(f"\nOperations: {patch['total_operations']}")
    print(f"Has changes: {patch['has_changes']}")
    
    print("\nDetailed operations:")
    for i, op in enumerate(patch['operations']):
        print(f"  {i+1}. {op['type']:8s} | {repr(op['text'][:50])}")
    
    # Validate
    is_valid = engine.validate_patch(patch)
    print(f"\n✅ Patch valid: {is_valid}")
    
    # Similarity
    similarity = engine.calculate_similarity(original, replacement)
    print(f"Similarity: {similarity:.2%}")


def test_multiple_changes():
    """Test patch with multiple changes"""
    print("\n" + "="*60)
    print("TEST 2: Multiple Changes")
    print("="*60)
    
    engine = PatchEngine()
    
    original = "This Agreement is between Acme Corporation and John Doe, dated January 1, 2026."
    replacement = "This Agreement is between TechCorp Industries and Jane Smith, dated February 15, 2026."
    
    patch = engine.generate_patch(original, replacement)
    summary = engine.get_change_summary(patch)
    
    print(f"\nOriginal:  {original}")
    print(f"Replacement: {replacement}")
    
    print(f"\nChange Summary:")
    print(f"  Total operations: {summary['total_operations']}")
    print(f"  Insertions: {summary['insertions']} ({summary['chars_inserted']} chars)")
    print(f"  Deletions: {summary['deletions']} ({summary['chars_deleted']} chars)")
    print(f"  Unchanged: {summary['equal']}")
    
    # Preview
    preview = engine.apply_patch_preview(patch)
    print(f"\nPreview matches replacement: {preview == replacement}")


def test_paragraph_patches():
    """Test paragraph patch generator"""
    print("\n" + "="*60)
    print("TEST 3: Multiple Paragraph Patches")
    print("="*60)
    
    generator = ParagraphPatchGenerator()
    
    changes = [
        {
            "paragraph_id": 5,
            "paragraph_index": 5,
            "original_text": "The Employee shall serve as Senior Software Engineer.",
            "replacement_text": "The Employee shall serve as Principal Software Architect.",
            "reasoning": "Update job title to reflect promotion"
        },
        {
            "paragraph_id": 8,
            "paragraph_index": 8,
            "original_text": "The Employee shall receive an annual base salary of $120,000.",
            "replacement_text": "The Employee shall receive an annual base salary of $150,000.",
            "reasoning": "Salary adjustment for new role"
        }
    ]
    
    patches = generator.generate_paragraph_patches(changes)
    
    print(f"\nGenerated {len(patches)} paragraph patches\n")
    
    for i, patch in enumerate(patches):
        print(f"--- Patch {i+1} ---")
        print(f"Paragraph ID: {patch['paragraph_id']}")
        print(f"Original:  {patch['original_text']}")
        print(f"Replacement: {patch['replacement_text']}")
        print(f"Reasoning: {patch['reasoning']}")
        print(f"Changes: {patch['change_summary']['insertions']} insertions, "
              f"{patch['change_summary']['deletions']} deletions")
        print()
    
    # Validate all
    all_valid = generator.validate_all_patches(patches)
    print(f"✅ All patches valid: {all_valid}")
    
    # Save to JSON
    output_path = "tests/fixtures/sample_patches.json"
    with open(output_path, "w") as f:
        json.dump(patches, f, indent=2)
    print(f"\n✅ Patches saved to: {output_path}")


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*60)
    print("TEST 4: Edge Cases")
    print("="*60)
    
    engine = PatchEngine()
    
    # Same text
    print("\n1. Identical text:")
    patch1 = engine.generate_patch("Same text", "Same text")
    print(f"   Has changes: {patch1['has_changes']}")
    
    # Empty strings
    print("\n2. Empty original:")
    patch2 = engine.generate_patch("", "New text")
    print(f"   Has changes: {patch2['has_changes']}")
    print(f"   Operations: {len(patch2['operations'])}")
    
    # Complete replacement
    print("\n3. Complete replacement:")
    patch3 = engine.generate_patch("Old content", "Completely different")
    summary3 = engine.get_change_summary(patch3)
    print(f"   Deletions: {summary3['deletions']}")
    print(f"   Insertions: {summary3['insertions']}")


if __name__ == "__main__":
    test_basic_patch()
    test_multiple_changes()
    test_paragraph_patches()
    test_edge_cases()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
