import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.agent_factory import get_legal_agent
from app.services.docx_parser import DOCXParser
from app.core.logging import logger
import json


def test_document_analysis():
    """Test document analysis"""
    
    print("\n" + "="*60)
    print("DOCUMENT ANALYSIS TEST")
    print("="*60)
    
    # Load sample document
    sample_path = "tests/fixtures/sample_employment_agreement.docx"
    
    if not Path(sample_path).exists():
        print(f"❌ Sample document not found: {sample_path}")
        return None
    
    with open(sample_path, "rb") as f:
        content = f.read()
    
    # Parse document
    parser = DOCXParser(content)
    parsed_data = parser.parse()
    
    print(f"\n📄 Parsed document: {parsed_data['total_paragraphs']} paragraphs")
    
    # Initialize agent (will auto-select real or mock)
    print("\n🤖 Initializing agent...")
    agent = get_legal_agent()
    
    # Analyze document
    print("\n🔍 Analyzing document...")
    analysis = agent.analyze_document(parsed_data["paragraphs"])
    
    print("\n📊 Analysis Results:")
    print(json.dumps(analysis, indent=2))
    
    return parsed_data


def test_edit_generation(parsed_data):
    """Test edit generation"""
    
    print("\n" + "="*60)
    print("EDIT GENERATION TEST")
    print("="*60)
    
    agent = get_legal_agent()
    
    # Test instruction 1: Change company name
    print("\n1️⃣  Instruction: Change company name")
    instruction1 = "Change all references to 'Acme Corporation' to 'TechCorp Industries'"
    
    edits1 = agent.generate_edits(
        document_paragraphs=parsed_data["paragraphs"],
        instruction=instruction1
    )
    
    print(f"   ✅ Generated {len(edits1)} edits")
    for i, edit in enumerate(edits1):
        print(f"\n   Edit {i+1}:")
        print(f"   Paragraph: {edit['paragraph_id']}")
        print(f"   Original:  {edit['original_text'][:60]}...")
        print(f"   New:       {edit['replacement_text'][:60]}...")
        print(f"   Reason:    {edit['reasoning']}")
    
    # Test instruction 2: Update salary
    print("\n\n2️⃣  Instruction: Update salary")
    instruction2 = "Change the annual salary from $120,000 to $150,000 and the bonus percentage from 15% to 20%"
    
    edits2 = agent.generate_edits(
        document_paragraphs=parsed_data["paragraphs"],
        instruction=instruction2
    )
    
    print(f"   ✅ Generated {len(edits2)} edits")
    for i, edit in enumerate(edits2):
        print(f"\n   Edit {i+1}:")
        print(f"   Paragraph: {edit['paragraph_id']}")
        print(f"   Reasoning: {edit['reasoning']}")
    
    # Test instruction 3: Update job title
    print("\n\n3️⃣  Instruction: Update job title")
    instruction3 = "Change the position from Senior Software Engineer to Principal Software Architect"
    
    edits3 = agent.generate_edits(
        document_paragraphs=parsed_data["paragraphs"],
        instruction=instruction3
    )
    
    print(f"   ✅ Generated {len(edits3)} edits")
    for i, edit in enumerate(edits3):
        print(f"\n   Edit {i+1}:")
        print(f"   Paragraph: {edit['paragraph_id']}")
        print(f"   Reasoning: {edit['reasoning']}")
    
    # Save edits to file
    all_edits = {
        "instruction_1": {"instruction": instruction1, "edits": edits1},
        "instruction_2": {"instruction": instruction2, "edits": edits2},
        "instruction_3": {"instruction": instruction3, "edits": edits3}
    }
    
    output_path = "tests/fixtures/llm_generated_edits.json"
    with open(output_path, "w") as f:
        json.dump(all_edits, f, indent=2)
    
    print(f"\n💾 Edits saved to: {output_path}")
    
    return edits1


if __name__ == "__main__":
    try:
        parsed_data = test_document_analysis()
        
        if parsed_data:
            test_edit_generation(parsed_data)
        
        print("\n" + "="*60)
        print("ALL LLM TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
