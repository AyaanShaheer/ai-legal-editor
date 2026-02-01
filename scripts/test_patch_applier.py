import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.docx_parser import DOCXParser
from app.services.patch_engine import ParagraphPatchGenerator
from app.services.patch_applier import PatchApplier, BatchPatchApplier
from app.core.logging import logger
import json


def test_end_to_end_patch_application():
    """Test complete workflow: parse -> generate patches -> apply patches"""
    
    print("\n" + "="*60)
    print("END-TO-END PATCH APPLICATION TEST")
    print("="*60)
    
    # Step 1: Load original document
    input_path = "tests/fixtures/sample_employment_agreement.docx"
    
    if not Path(input_path).exists():
        print(f"❌ Sample document not found: {input_path}")
        return
    
    print(f"\n📄 Loading document: {input_path}")
    
    with open(input_path, "rb") as f:
        original_bytes = f.read()
    
    # Step 2: Parse document
    print("\n🔍 Parsing document...")
    parser = DOCXParser(original_bytes)
    parsed_data = parser.parse()
    
    print(f"   Total paragraphs: {parsed_data['total_paragraphs']}")
    
    # Step 3: Define changes
    print("\n✏️  Defining changes...")
    
    changes = [
        {
            "paragraph_id": 2,  # Introduction paragraph
            "paragraph_index": 2,
            "original_text": parsed_data["paragraphs"][2]["text"],
            "replacement_text": "This Employment Agreement (the 'Agreement') is entered into on February 1, 2026, between TechCorp Industries ('Employer') and Jane Smith ('Employee').",
            "reasoning": "Update company name, employee name, and date"
        },
        {
            "paragraph_id": 5,  # Position paragraph
            "paragraph_index": 5,
            "original_text": parsed_data["paragraphs"][5]["text"],
            "replacement_text": "The Employee shall serve as Principal Software Architect and shall perform such duties as are customarily associated with such position. The Employee shall report directly to the Chief Technology Officer.",
            "reasoning": "Update job title from Senior Software Engineer to Principal Software Architect"
        },
        {
            "paragraph_id": 8,  # Compensation paragraph
            "paragraph_index": 8,
            "original_text": parsed_data["paragraphs"][8]["text"],
            "replacement_text": "The Employee shall receive an annual base salary of $150,000, payable in accordance with the Employer's standard payroll practices. The Employee shall be eligible for an annual performance bonus of up to 20% of base salary.",
            "reasoning": "Increase salary to $150,000 and bonus to 20%"
        }
    ]
    
    for i, change in enumerate(changes):
        print(f"\n   Change {i+1}:")
        print(f"   Paragraph: {change['paragraph_id']}")
        print(f"   Original:  {change['original_text'][:60]}...")
        print(f"   New:       {change['replacement_text'][:60]}...")
        print(f"   Reason:    {change['reasoning']}")
    
    # Step 4: Generate patches
    print("\n🔧 Generating patches...")
    patch_generator = ParagraphPatchGenerator()
    patches = patch_generator.generate_paragraph_patches(changes)
    
    print(f"   Generated {len(patches)} patches")
    
    # Validate patches
    all_valid = patch_generator.validate_all_patches(patches)
    print(f"   Validation: {'✅ PASSED' if all_valid else '❌ FAILED'}")
    
    if not all_valid:
        print("❌ Patch validation failed. Aborting.")
        return
    
    # Step 5: Apply patches
    print("\n📝 Applying patches with tracked changes...")
    
    modified_bytes = BatchPatchApplier.apply_patches_to_document(
        original_bytes,
        patches,
        author="AI Legal Assistant"
    )
    
    print(f"   ✅ Patches applied successfully")
    print(f"   Modified document size: {len(modified_bytes)} bytes")
    
    # Step 6: Save modified document
    output_path = "tests/fixtures/sample_employment_agreement_modified.docx"
    
    with open(output_path, "wb") as f:
        f.write(modified_bytes)
    
    print(f"\n💾 Modified document saved: {output_path}")
    
    # Step 7: Verify by parsing modified document
    print("\n🔍 Verifying modified document...")
    
    modified_parser = DOCXParser(modified_bytes)
    modified_parsed = modified_parser.parse()
    
    print(f"   Paragraphs in modified: {modified_parsed['total_paragraphs']}")
    
    # Check if changes are present
    print("\n📊 Verification:")
    for change in changes:
        para_id = change["paragraph_id"]
        modified_para = modified_parsed["paragraphs"][para_id]
        
        # Check if modified text contains markers (red/green text)
        contains_change = len(modified_para["text"]) > 0
        print(f"   Paragraph {para_id}: {'✅ Modified' if contains_change else '⚠️  No change detected'}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60)
    print(f"\n📂 Open this file in Microsoft Word to see tracked changes:")
    print(f"   {Path(output_path).absolute()}")
    print("\n💡 Tip: In Word, go to Review > Tracking to see all changes highlighted")


def test_simple_replacement():
    """Test simple replacement without tracked changes"""
    
    print("\n" + "="*60)
    print("SIMPLE REPLACEMENT TEST (No Tracked Changes)")
    print("="*60)
    
    input_path = "tests/fixtures/sample_employment_agreement.docx"
    
    with open(input_path, "rb") as f:
        original_bytes = f.read()
    
    applier = PatchApplier(original_bytes)
    
    # Replace paragraph 0 (title)
    success = applier.apply_simple_replacement(0, "UPDATED EMPLOYMENT AGREEMENT")
    
    print(f"\nSimple replacement: {'✅ Success' if success else '❌ Failed'}")
    
    # Save
    output_path = "tests/fixtures/sample_simple_replacement.docx"
    applier.save_to_file(output_path)
    
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    test_end_to_end_patch_application()
    print("\n\n")
    test_simple_replacement()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
