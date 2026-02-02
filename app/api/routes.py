from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
from app.api.dependencies import (
    get_document_repository,
    get_version_repository,
    get_job_repository,
    get_storage_service,
    get_current_user_id
)
from app.repositories import DocumentRepository, DocumentVersionRepository, JobRepository
from app.services import AzureStorageService
from app.schemas import (
    DocumentUploadResponse,
    DocumentMetadata,
    DocumentList,
    DocumentVersionResponse,
    DocumentVersionList,
    EditInstructionRequest,
    EditInstructionResponse,
    JobStatusResponse,
    PatchPreviewResponse,
    ApplyPatchRequest,
    ApplyPatchResponse,
    DocumentDownloadResponse,
    ErrorResponse
)
from app.core.validators import validate_file_upload, validate_file_size
from app.core.exceptions import DocumentNotFoundException, JobNotFoundException
from app.core.logging import logger
from app.models.database import JobStatus

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
    description="Upload a DOCX document to the system"
)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    doc_repo: DocumentRepository = Depends(get_document_repository),
    version_repo: DocumentVersionRepository = Depends(get_version_repository),
    storage: AzureStorageService = Depends(get_storage_service)
):
    """Upload a new DOCX document"""
    
    # Validate file
    validate_file_upload(file)
    
    # Read and validate size
    file_content = await validate_file_size(file)
    
    logger.info(f"Uploading document: {file.filename} ({len(file_content)} bytes)")
    
    try:
        # Create document record
        document = await doc_repo.create(
            user_id=user_id,
            original_filename=file.filename,
            blob_path="temp"  # Temporary, will update after storage
        )
        
        # Upload to storage
        blob_path = storage.upload_document(
            file_content=file_content,
            user_id=user_id,
            document_id=document.id,
            filename=file.filename,
            version=1
        )
        
        # Update document with real blob path
        document = await doc_repo.update(document.id, blob_path=blob_path)
        
        # Create initial version
        await version_repo.create(
            document_id=document.id,
            version_number=1,
            blob_path=blob_path,
            description="Initial upload"
        )
        
        logger.info(f"Document uploaded successfully: {document.id}")
        
        return DocumentUploadResponse(
            document_id=document.id,
            filename=document.original_filename,
            blob_path=document.blob_path,
            user_id=document.user_id,
            created_at=document.created_at
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get(
    "/documents",
    response_model=DocumentList,
    summary="List all documents",
    description="Get all documents for the current user"
)
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    doc_repo: DocumentRepository = Depends(get_document_repository),
    version_repo: DocumentVersionRepository = Depends(get_version_repository)
):
    """List all documents for current user"""
    
    documents = await doc_repo.get_by_user(user_id, skip=skip, limit=limit)
    total = await doc_repo.count_by_user(user_id)
    
    # Enrich with version count
    doc_list = []
    for doc in documents:
        version_count = await version_repo.count_by_document(doc.id)
        doc_list.append(
            DocumentMetadata(
                id=doc.id,
                user_id=doc.user_id,
                original_filename=doc.original_filename,
                blob_path=doc.blob_path,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                version_count=version_count
            )
        )
    
    return DocumentList(
        documents=doc_list,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentMetadata,
    summary="Get document details",
    description="Get detailed information about a specific document"
)
async def get_document(
    document_id: int,
    user_id: str = Depends(get_current_user_id),
    doc_repo: DocumentRepository = Depends(get_document_repository),
    version_repo: DocumentVersionRepository = Depends(get_version_repository)
):
    """Get document details"""
    
    document = await doc_repo.get_by_id(document_id)
    
    if not document or document.user_id != user_id:
        raise DocumentNotFoundException(document_id)
    
    version_count = await version_repo.count_by_document(document_id)
    
    return DocumentMetadata(
        id=document.id,
        user_id=document.user_id,
        original_filename=document.original_filename,
        blob_path=document.blob_path,
        created_at=document.created_at,
        updated_at=document.updated_at,
        version_count=version_count
    )


@router.get(
    "/documents/{document_id}/versions",
    response_model=DocumentVersionList,
    summary="List document versions",
    description="Get all versions of a document"
)
async def list_versions(
    document_id: int,
    user_id: str = Depends(get_current_user_id),
    doc_repo: DocumentRepository = Depends(get_document_repository),
    version_repo: DocumentVersionRepository = Depends(get_version_repository)
):
    """List all versions of a document"""
    
    # Check document ownership
    document = await doc_repo.get_by_id(document_id)
    if not document or document.user_id != user_id:
        raise DocumentNotFoundException(document_id)
    
    versions = await version_repo.get_by_document(document_id)
    
    version_list = [
        DocumentVersionResponse(
            id=v.id,
            document_id=v.document_id,
            version_number=v.version_number,
            blob_path=v.blob_path,
            description=v.description,
            created_at=v.created_at
        )
        for v in versions
    ]
    
    return DocumentVersionList(
        versions=version_list,
        total=len(version_list)
    )


@router.post(
    "/documents/{document_id}/edit",
    response_model=EditInstructionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit edit instruction",
    description="Submit an instruction to edit the document using AI"
)
async def submit_edit_instruction(
    document_id: int,
    request: EditInstructionRequest,
    user_id: str = Depends(get_current_user_id),
    doc_repo: DocumentRepository = Depends(get_document_repository),
    job_repo: JobRepository = Depends(get_job_repository)
):
    """Submit an edit instruction for AI processing"""
    
    # Check document ownership
    document = await doc_repo.get_by_id(document_id)
    if not document or document.user_id != user_id:
        raise DocumentNotFoundException(document_id)
    
    # Create job
    job = await job_repo.create(
        document_id=document_id,
        instruction=request.instruction,
        status=JobStatus.PENDING
    )
    
    logger.info(f"Created edit job {job.id} for document {document_id}")
    
    # TODO: Trigger Celery task here (Step 11)
    
    return EditInstructionResponse(
        job_id=job.id,
        document_id=document_id,
        status=job.status,
        instruction=job.instruction,
        created_at=job.created_at
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get job status",
    description="Poll the status of an edit job"
)
async def get_job_status(
    job_id: int,
    user_id: str = Depends(get_current_user_id),
    job_repo: JobRepository = Depends(get_job_repository),
    doc_repo: DocumentRepository = Depends(get_document_repository)
):
    """Get job status"""
    
    job = await job_repo.get_by_id(job_id)
    
    if not job:
        raise JobNotFoundException(job_id)
    
    # Check document ownership
    document = await doc_repo.get_by_id(job.document_id)
    if not document or document.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return JobStatusResponse(
        job_id=job.id,
        document_id=job.document_id,
        status=job.status,
        instruction=job.instruction,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        patch_available=(job.status == JobStatus.COMPLETED and job.patch_json is not None)
    )


@router.get(
    "/jobs/{job_id}/patch",
    response_model=PatchPreviewResponse,
    summary="Get patch preview",
    description="Get the generated patch for review"
)
async def get_patch_preview(
    job_id: int,
    user_id: str = Depends(get_current_user_id),
    job_repo: JobRepository = Depends(get_job_repository),
    doc_repo: DocumentRepository = Depends(get_document_repository)
):
    """Get patch preview"""
    
    job = await job_repo.get_by_id(job_id)
    
    if not job:
        raise JobNotFoundException(job_id)
    
    # Check document ownership
    document = await doc_repo.get_by_id(job.document_id)
    if not document or document.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if patch is ready
    if job.status != JobStatus.COMPLETED or not job.patch_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patch not ready. Current status: {job.status}"
        )
    
    # Parse patch JSON
    import json
    patch_data = json.loads(job.patch_json)
    
    return PatchPreviewResponse(
        job_id=job.id,
        document_id=job.document_id,
        patches=patch_data.get("patches", []),
        total_changes=len(patch_data.get("patches", [])),
        created_at=job.completed_at or job.created_at
    )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete a document and all its versions"
)
async def delete_document(
    document_id: int,
    user_id: str = Depends(get_current_user_id),
    doc_repo: DocumentRepository = Depends(get_document_repository),
    storage: AzureStorageService = Depends(get_storage_service)
):
    """Delete document"""
    
    # Check document ownership
    document = await doc_repo.get_by_id(document_id)
    if not document or document.user_id != user_id:
        raise DocumentNotFoundException(document_id)
    
    # Delete from storage (best effort)
    try:
        storage.delete_document(document.blob_path)
    except Exception as e:
        logger.warning(f"Failed to delete from storage: {str(e)}")
    
    # Delete from database (cascade will delete versions and jobs)
    await doc_repo.delete(document_id)
    
    logger.info(f"Deleted document {document_id}")
