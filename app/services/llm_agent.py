from openai import AzureOpenAI
from typing import List, Dict, Any, Optional
import json
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import DocumentProcessingException


class AzureOpenAIClient:
    """Client for Azure OpenAI API"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        try:
            # Updated initialization without deprecated parameters
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
            logger.info("Azure OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI: {str(e)}")
            # Re-raise to trigger mock fallback in factory
            raise
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate completion from Azure OpenAI
        
        Args:
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            response_format: Response format (e.g., {"type": "json_object"})
            
        Returns:
            Generated text
        """
        try:
            params = {
                "model": self.deployment_name,
                "messages": messages,
                "temperature": temperature or settings.LLM_TEMPERATURE,
                "max_tokens": max_tokens or settings.LLM_MAX_TOKENS
            }
            
            if response_format:
                params["response_format"] = response_format
            
            response = self.client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            
            logger.info(
                f"OpenAI completion: {response.usage.prompt_tokens} prompt tokens, "
                f"{response.usage.completion_tokens} completion tokens"
            )
            
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise DocumentProcessingException(f"LLM generation failed: {str(e)}")


class LegalDocumentAgent:
    """AI Agent for legal document editing"""
    
    def __init__(self):
        """Initialize agent"""
        self.client = AzureOpenAIClient()
    
    def generate_edits(
        self,
        document_paragraphs: List[Dict[str, Any]],
        instruction: str
    ) -> List[Dict[str, Any]]:
        """
        Generate document edits based on instruction
        
        Args:
            document_paragraphs: Parsed document paragraphs
            instruction: User's edit instruction
            
        Returns:
            List of edits with paragraph_id, original_text, replacement_text, reasoning
        """
        
        logger.info(f"Generating edits for instruction: {instruction[:100]}...")
        
        # Build context
        document_text = self._build_document_context(document_paragraphs)
        
        # Create prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(document_text, instruction)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Get completion with JSON response format
        try:
            response_text = self.client.generate_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            response_data = json.loads(response_text)
            edits = response_data.get("edits", [])
            
            logger.info(f"Generated {len(edits)} edits")
            
            # Validate and enrich edits
            validated_edits = self._validate_edits(edits, document_paragraphs)
            
            return validated_edits
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise DocumentProcessingException("Invalid LLM response format")
        except Exception as e:
            logger.error(f"Edit generation failed: {str(e)}")
            raise DocumentProcessingException(f"Edit generation failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        return """You are an expert legal document editor AI assistant. Your role is to:

1. Carefully analyze legal documents
2. Generate precise, safe edits based on user instructions
3. Preserve legal language and formatting
4. Ensure consistency across the document
5. Only modify what is explicitly requested

CRITICAL RULES:
- Return edits in valid JSON format
- Each edit must specify: paragraph_id, original_text, replacement_text, reasoning
- Only edit paragraphs that are directly affected by the instruction
- Preserve all formatting, capitalization, and punctuation unless explicitly asked to change
- Never add or remove legal clauses unless explicitly instructed
- Be conservative - when in doubt, don't edit

Response format:
{
  "edits": [
    {
      "paragraph_id": <number>,
      "original_text": "<exact original text>",
      "replacement_text": "<new text>",
      "reasoning": "<brief explanation>"
    }
  ]
}"""
    
    def _build_user_prompt(self, document_text: str, instruction: str) -> str:
        """Build user prompt with document and instruction"""
        return f"""Document:
{document_text}

Instruction: {instruction}

Analyze the document and generate precise edits to fulfill the instruction. Return only valid JSON with the edits array."""
    
    def _build_document_context(self, paragraphs: List[Dict[str, Any]]) -> str:
        """Build readable document context for LLM"""
        lines = []
        
        for para in paragraphs:
            if not para.get("is_empty", True):
                para_id = para.get("id")
                text = para.get("text", "")
                lines.append(f"[Paragraph {para_id}] {text}")
        
        return "\n\n".join(lines)
    
    def _validate_edits(
        self,
        edits: List[Dict[str, Any]],
        paragraphs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate and enrich edits
        
        Args:
            edits: Raw edits from LLM
            paragraphs: Document paragraphs
            
        Returns:
            Validated edits
        """
        validated = []
        
        paragraph_map = {p["id"]: p for p in paragraphs}
        
        for edit in edits:
            para_id = edit.get("paragraph_id")
            
            # Validate paragraph ID
            if para_id not in paragraph_map:
                logger.warning(f"Invalid paragraph_id {para_id}, skipping")
                continue
            
            # Validate required fields
            if not all(k in edit for k in ["original_text", "replacement_text", "reasoning"]):
                logger.warning(f"Missing required fields in edit for paragraph {para_id}")
                continue
            
            # Enrich with paragraph index
            validated_edit = {
                "paragraph_id": para_id,
                "paragraph_index": para_id,
                "original_text": edit["original_text"],
                "replacement_text": edit["replacement_text"],
                "reasoning": edit["reasoning"]
            }
            
            validated.append(validated_edit)
        
        return validated
    
    def analyze_document(self, paragraphs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze document structure and content
        
        Args:
            paragraphs: Document paragraphs
            
        Returns:
            Analysis summary
        """
        
        non_empty = [p for p in paragraphs if not p.get("is_empty", True)]
        
        system_prompt = """You are a legal document analyzer. Analyze the document and provide:
1. Document type (e.g., Employment Agreement, NDA, Contract)
2. Key sections identified
3. Important entities (parties, dates, amounts)
4. Overall document quality assessment

Return valid JSON format."""
        
        document_text = self._build_document_context(paragraphs)
        
        user_prompt = f"""Analyze this legal document:

{document_text}

Provide analysis in JSON format with keys: document_type, sections, entities, quality_notes"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.generate_completion(
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response)
            return analysis
            
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            return {
                "document_type": "Unknown",
                "sections": [],
                "entities": {},
                "quality_notes": "Analysis failed"
            }
