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
from app.services.azure_storage import AzureStorageService
from app.services.storage_helpers import (
    parse_blob_path,
    generate_blob_name,
    get_latest_version_number,
    format_file_size
)
from app.services.agent_factory import get_legal_agent

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
    "BatchPatchApplier",
    "AzureStorageService",
    "parse_blob_path",
    "generate_blob_name",
    "get_latest_version_number",
    "format_file_size",
    "get_legal_agent"
]
