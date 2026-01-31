from typing import Dict, List, Any
from app.core.logging import logger


def filter_non_empty_paragraphs(parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter out empty paragraphs from parsed data
    
    Args:
        parsed_data: Parsed document data
        
    Returns:
        List of non-empty paragraphs
    """
    paragraphs = parsed_data.get("paragraphs", [])
    non_empty = [p for p in paragraphs if not p.get("is_empty", True)]
    
    logger.info(f"Filtered {len(paragraphs) - len(non_empty)} empty paragraphs")
    return non_empty


def get_paragraphs_by_style(parsed_data: Dict[str, Any], style: str) -> List[Dict[str, Any]]:
    """
    Get paragraphs matching a specific style
    
    Args:
        parsed_data: Parsed document data
        style: Style name to filter by
        
    Returns:
        List of matching paragraphs
    """
    paragraphs = parsed_data.get("paragraphs", [])
    matching = [p for p in paragraphs if p.get("style", "") == style]
    
    logger.info(f"Found {len(matching)} paragraphs with style '{style}'")
    return matching


def extract_paragraph_texts_only(parsed_data: Dict[str, Any]) -> List[str]:
    """
    Extract only text content from paragraphs
    
    Args:
        parsed_data: Parsed document data
        
    Returns:
        List of paragraph text strings
    """
    paragraphs = parsed_data.get("paragraphs", [])
    texts = [p.get("text", "") for p in paragraphs if not p.get("is_empty", True)]
    
    return texts


def find_paragraph_by_text(parsed_data: Dict[str, Any], search_text: str) -> List[Dict[str, Any]]:
    """
    Find paragraphs containing specific text
    
    Args:
        parsed_data: Parsed document data
        search_text: Text to search for
        
    Returns:
        List of matching paragraphs
    """
    paragraphs = parsed_data.get("paragraphs", [])
    matches = [
        p for p in paragraphs 
        if search_text.lower() in p.get("text", "").lower()
    ]
    
    logger.info(f"Found {len(matches)} paragraphs containing '{search_text}'")
    return matches


def get_document_summary(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary statistics for document
    
    Args:
        parsed_data: Parsed document data
        
    Returns:
        Summary dictionary
    """
    paragraphs = parsed_data.get("paragraphs", [])
    non_empty = [p for p in paragraphs if not p.get("is_empty", True)]
    
    total_chars = sum(len(p.get("text", "")) for p in non_empty)
    total_words = sum(len(p.get("text", "").split()) for p in non_empty)
    
    return {
        "total_paragraphs": len(paragraphs),
        "non_empty_paragraphs": len(non_empty),
        "total_runs": parsed_data.get("total_runs", 0),
        "total_characters": total_chars,
        "total_words": total_words,
        "metadata": parsed_data.get("metadata", {})
    }
