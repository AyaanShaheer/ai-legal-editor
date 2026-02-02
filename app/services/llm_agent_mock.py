from typing import List, Dict, Any
from app.core.logging import logger
import re


class MockLegalDocumentAgent:
    """Mock agent for testing without Azure OpenAI"""
    
    def __init__(self):
        """Initialize mock agent"""
        logger.info("Using MOCK LLM Agent (no Azure OpenAI)")
    
    def generate_edits(
        self,
        document_paragraphs: List[Dict[str, Any]],
        instruction: str
    ) -> List[Dict[str, Any]]:
        """
        Generate mock edits based on simple pattern matching
        
        Args:
            document_paragraphs: Parsed document paragraphs
            instruction: User's edit instruction
            
        Returns:
            List of mock edits
        """
        
        logger.info(f"[MOCK] Generating edits for: {instruction[:100]}...")
        
        edits = []
        
        # Parse instruction for patterns
        instruction_lower = instruction.lower()
        
        for para in document_paragraphs:
            if para.get("is_empty", True):
                continue
            
            para_id = para.get("id")
            text = para.get("text", "")
            modified = False
            new_text = text
            reasoning = ""
            
            # Pattern 1: Change company name
            if "acme corporation" in instruction_lower:
                if "Acme Corporation" in text:
                    new_text = text.replace("Acme Corporation", "TechCorp Industries")
                    reasoning = "Updated company name from Acme Corporation to TechCorp Industries"
                    modified = True
            
            # Pattern 2: Change salary
            if "salary" in instruction_lower and ("120" in instruction_lower or "150" in instruction_lower):
                if "$120,000" in text:
                    new_text = new_text.replace("$120,000", "$150,000")
                    reasoning = "Updated annual salary from $120,000 to $150,000"
                    modified = True
            
            # Pattern 3: Change bonus percentage
            if "bonus" in instruction_lower and ("15%" in text or "20%" in instruction_lower):
                if "15%" in text:
                    new_text = new_text.replace("15%", "20%")
                    if reasoning:
                        reasoning += " and bonus percentage from 15% to 20%"
                    else:
                        reasoning = "Updated bonus percentage from 15% to 20%"
                    modified = True
            
            # Pattern 4: Change job title
            if "senior software engineer" in instruction_lower or "principal software architect" in instruction_lower:
                if "Senior Software Engineer" in text:
                    new_text = text.replace("Senior Software Engineer", "Principal Software Architect")
                    reasoning = "Updated job title from Senior Software Engineer to Principal Software Architect"
                    modified = True
            
            # Pattern 5: Change employee/person names
            if "john doe" in instruction_lower or "jane smith" in instruction_lower:
                if "John Doe" in text:
                    new_text = text.replace("John Doe", "Jane Smith")
                    reasoning = "Updated employee name from John Doe to Jane Smith"
                    modified = True
            
            # Pattern 6: Date changes
            date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
            if re.search(date_pattern, instruction, re.IGNORECASE):
                # Extract dates from instruction and text
                matches = re.findall(date_pattern, text)
                if matches:
                    new_text = text  # Keep as is for now
                    reasoning = "Date change detected (mock implementation)"
                    modified = True
            
            if modified:
                edits.append({
                    "paragraph_id": para_id,
                    "paragraph_index": para_id,
                    "original_text": text,
                    "replacement_text": new_text,
                    "reasoning": reasoning
                })
        
        logger.info(f"[MOCK] Generated {len(edits)} edits")
        return edits
    
    def analyze_document(self, paragraphs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock document analysis"""
        
        # Extract some basic info
        all_text = " ".join([p.get("text", "") for p in paragraphs if not p.get("is_empty", True)])
        
        entities = {}
        if "Acme Corporation" in all_text:
            entities["employer"] = "Acme Corporation"
        if "John Doe" in all_text:
            entities["employee"] = "John Doe"
        if "Senior Software Engineer" in all_text:
            entities["position"] = "Senior Software Engineer"
        if "$120,000" in all_text:
            entities["salary"] = "$120,000"
        
        return {
            "document_type": "Employment Agreement (Mock Analysis)",
            "sections": ["Title", "Introduction", "Position and Duties", "Compensation", "Confidentiality", "Signatures"],
            "entities": entities,
            "quality_notes": "This is a mock analysis. Real analysis requires Azure OpenAI connection.",
            "paragraph_count": len([p for p in paragraphs if not p.get("is_empty", True)])
        }
