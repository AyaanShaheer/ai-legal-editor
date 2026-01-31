from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatusEnum(str, Enum):
    """Job status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============= Document Upload =============

class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: int
    filename: str
    blob_path: str
    user_id: str
    created_at: datetime
    message: str = "Document uploaded successfully"
    
    class Config:
        from_attributes = True


# ============= Document Metadata =============

class DocumentMetadata(BaseModel):
    """Document metadata"""
    id: int
    user_id: str
    original_filename: str
    blob_path: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    version_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """List of documents"""
    documents: List[DocumentMetadata]
    total: int
    page: int = 1
    page_size: int = 10


# ============= Document Versions =============

class DocumentVersionCreate(BaseModel):
    """Schema for creating a new document version"""
    document_id: int
    description: Optional[str] = None


class DocumentVersionResponse(BaseModel):
    """Document version response"""
    id: int
    document_id: int
    version_number: int
    blob_path: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentVersionList(BaseModel):
    """List of document versions"""
    versions: List[DocumentVersionResponse]
    total: int


# ============= Edit Instructions =============

class EditInstructionRequest(BaseModel):
    """Request to edit a document"""
    instruction: str = Field(..., min_length=10, max_length=5000)
    
    @validator('instruction')
    def validate_instruction(cls, v):
        if not v.strip():
            raise ValueError("Instruction cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "instruction": "Change all instances of 'Party A' to 'Acme Corporation' and update the contract date to January 31, 2026"
            }
        }


class EditInstructionResponse(BaseModel):
    """Response after submitting edit instruction"""
    job_id: int
    document_id: int
    status: JobStatusEnum
    instruction: str
    created_at: datetime
    message: str = "Edit job created successfully. Use job_id to poll status."
    
    class Config:
        from_attributes = True


# ============= Job Status =============

class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: int
    document_id: int
    status: JobStatusEnum
    instruction: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    patch_available: bool = False
    
    class Config:
        from_attributes = True


# ============= Patch Details =============

class PatchOperation(BaseModel):
    """Single patch operation"""
    type: str = Field(..., description="Operation type: 'insert', 'delete', or 'equal'")
    text: str = Field(..., description="Text content for this operation")
    position: Optional[int] = None


class ParagraphPatch(BaseModel):
    """Patch for a single paragraph"""
    paragraph_id: int
    paragraph_index: int
    original_text: str
    replacement_text: str
    operations: List[PatchOperation]
    reasoning: Optional[str] = None


class PatchPreviewResponse(BaseModel):
    """Patch preview response"""
    job_id: int
    document_id: int
    patches: List[ParagraphPatch]
    total_changes: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Apply Patch =============

class ApplyPatchRequest(BaseModel):
    """Request to apply a patch"""
    description: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Applied AI-suggested changes for party name updates"
            }
        }


class ApplyPatchResponse(BaseModel):
    """Response after applying patch"""
    document_id: int
    new_version_id: int
    version_number: int
    blob_path: str
    description: Optional[str] = None
    message: str = "Patch applied successfully with tracked changes"
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Document Download =============

class DocumentDownloadResponse(BaseModel):
    """Document download response"""
    document_id: int
    version_id: Optional[int] = None
    filename: str
    download_url: str
    expires_in_seconds: int = 3600
    
    class Config:
        from_attributes = True


# ============= Error Response =============

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
