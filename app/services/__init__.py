from app.services.docx_parser import DOCXParser
from app.services.document_helpers import (
    filter_non_empty_paragraphs,
    get_paragraphs_by_style,
    extract_paragraph_texts_only,
    find_paragraph_by_text,
    get_document_summary
)
from app.services.patch_engine import PatchEngine, ParagraphPatchGenerator
from app.services.patch_applier import PatchApplier, BatchPatchApplier

__all__ = [
    "DOCXParser",
    "filter_non_empty_paragraphs",
    "get_paragraphs_by_style",
    "extract_paragraph_texts_only",
    "find_paragraph_by_text",
    "get_document_summary",
    "PatchEngine",
    "ParagraphPatchGenerator",
    "PatchApplier",
    "BatchPatchApplier"
]
