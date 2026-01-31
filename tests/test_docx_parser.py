import pytest
from app.services.docx_parser import DOCXParser
from app.core.exceptions import DocumentProcessingException


def test_parser_with_invalid_content():
    """Test parser with invalid DOCX content"""
    invalid_content = b"This is not a DOCX file"
    
    with pytest.raises(DocumentProcessingException):
        parser = DOCXParser(invalid_content)


def test_parser_initialization():
    """Test parser can be initialized (requires valid DOCX)"""
    # This is a placeholder - we'll test with real DOCX files later
    pass
