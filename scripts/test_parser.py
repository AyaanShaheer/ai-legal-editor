import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.docx_parser import DOCXParser
from app.core.logging import logger


def test_parser():
    """Test DOCX parser with sample document"""
    
    sample_path = "tests/fixtures/sample_employment_agreement.docx"
    
    if not Path(sample_path).exists():
        print(f"❌ Sample document not found: {sample_path}")
        print("Run: python scripts/create_sample_docx.py")
        return
    
    print(f"📄 Loading document: {sample_path}")
    
    # Read file
    with open(sample_path, "rb") as f:
        content = f.read()
    
    print(f"✅ File loaded: {len(content)} bytes")
    
    # Parse document
    parser = DOCXParser(content)
    parsed_data = parser.parse()
    
    # Display results
    print("\n" + "="*60)
    print("DOCUMENT METADATA")
    print("="*60)
    print(json.dumps(parsed_data["metadata"], indent=2))
    
    print("\n" + "="*60)
    print(f"DOCUMENT STRUCTURE")
    print("="*60)
    print(f"Total Paragraphs: {parsed_data['total_paragraphs']}")
    print(f"Total Runs: {parsed_data['total_runs']}")
    
    print("\n" + "="*60)
    print("PARAGRAPHS PREVIEW (First 5)")
    print("="*60)
    
    for i, para in enumerate(parsed_data["paragraphs"][:5]):
        print(f"\n--- Paragraph {para['id']} ---")
        print(f"Text: {para['text'][:100]}{'...' if len(para['text']) > 100 else ''}")
        print(f"Style: {para['style']}")
        print(f"Alignment: {para['alignment']}")
        print(f"Runs: {len(para['runs'])}")
        
        if para['runs']:
            print(f"First run formatting:")
            first_run = para['runs'][0]
            print(f"  - Bold: {first_run['bold']}")
            print(f"  - Italic: {first_run['italic']}")
            print(f"  - Font: {first_run['font_name']} {first_run['font_size']}pt")
    
    print("\n" + "="*60)
    print("FULL TEXT CONTENT")
    print("="*60)
    full_text = parser.get_text_content()
    print(full_text)
    
    # Save parsed JSON
    output_path = "tests/fixtures/parsed_document.json"
    with open(output_path, "w") as f:
        json.dump(parsed_data, f, indent=2)
    
    print(f"\n✅ Parsed data saved to: {output_path}")


if __name__ == "__main__":
    test_parser()
