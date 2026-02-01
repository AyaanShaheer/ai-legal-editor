from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import ResourceNotFoundError, AzureError
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from io import BytesIO
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import DocumentProcessingException


class AzureStorageService:
    """Service for managing document storage in Azure Blob Storage"""
    
    def __init__(self):
        """Initialize Azure Blob Storage client"""
        try:
            if settings.AZURE_STORAGE_CONNECTION_STRING:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING
                )
                self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
                self._ensure_container_exists()
                logger.info("Azure Blob Storage initialized successfully")
            else:
                logger.warning("Azure Storage connection string not configured, using local fallback")
                self.blob_service_client = None
                self.container_name = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage: {str(e)}")
            self.blob_service_client = None
            self.container_name = None
    
    def _ensure_container_exists(self):
        """Create container if it doesn't exist"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
        except Exception as e:
            logger.error(f"Failed to ensure container exists: {str(e)}")
    
    def upload_document(
        self, 
        file_content: bytes, 
        user_id: str, 
        document_id: int,
        filename: str,
        version: int = 1
    ) -> str:
        """
        Upload document to blob storage
        
        Args:
            file_content: Document bytes
            user_id: User ID
            document_id: Document ID
            filename: Original filename
            version: Version number
            
        Returns:
            Blob path (URL or relative path)
        """
        try:
            # Generate blob name: user_id/document_id/v{version}_filename
            blob_name = f"{user_id}/{document_id}/v{version}_{filename}"
            
            if self.blob_service_client:
                # Upload to Azure
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob_name
                )
                
                blob_client.upload_blob(
                    file_content, 
                    overwrite=True,
                    metadata={
                        "user_id": user_id,
                        "document_id": str(document_id),
                        "version": str(version),
                        "original_filename": filename,
                        "upload_timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                blob_path = blob_client.url
                logger.info(f"Uploaded to Azure Blob: {blob_name}")
            else:
                # Fallback to local storage
                blob_path = self._save_to_local_storage(
                    file_content, user_id, document_id, filename, version
                )
                logger.info(f"Saved to local storage: {blob_path}")
            
            return blob_path
            
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise DocumentProcessingException(f"Failed to upload document: {str(e)}")
    
    def download_document(self, blob_path: str) -> bytes:
        """
        Download document from blob storage
        
        Args:
            blob_path: Blob path or URL
            
        Returns:
            Document bytes
        """
        try:
            if self.blob_service_client and blob_path.startswith("http"):
                # Download from Azure
                blob_client = BlobClient.from_blob_url(blob_path)
                downloader = blob_client.download_blob()
                content = downloader.readall()
                logger.info(f"Downloaded from Azure: {blob_path}")
            else:
                # Download from local storage
                content = self._load_from_local_storage(blob_path)
                logger.info(f"Loaded from local storage: {blob_path}")
            
            return content
            
        except ResourceNotFoundError:
            logger.error(f"Document not found: {blob_path}")
            raise DocumentProcessingException(f"Document not found: {blob_path}")
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            raise DocumentProcessingException(f"Failed to download document: {str(e)}")
    
    def delete_document(self, blob_path: str) -> bool:
        """
        Delete document from blob storage
        
        Args:
            blob_path: Blob path or URL
            
        Returns:
            True if successful
        """
        try:
            if self.blob_service_client and blob_path.startswith("http"):
                blob_client = BlobClient.from_blob_url(blob_path)
                blob_client.delete_blob()
                logger.info(f"Deleted from Azure: {blob_path}")
            else:
                self._delete_from_local_storage(blob_path)
                logger.info(f"Deleted from local storage: {blob_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Delete failed: {str(e)}")
            return False
    
    def generate_download_url(
        self, 
        blob_path: str, 
        expiry_hours: int = 1
    ) -> str:
        """
        Generate temporary download URL with SAS token
        
        Args:
            blob_path: Blob path or URL
            expiry_hours: URL expiry time in hours
            
        Returns:
            Temporary download URL
        """
        try:
            if self.blob_service_client and blob_path.startswith("http"):
                blob_client = BlobClient.from_blob_url(blob_path)
                
                # Generate SAS token
                sas_token = generate_blob_sas(
                    account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
                    container_name=self.container_name,
                    blob_name=blob_client.blob_name,
                    account_key=self._get_account_key(),
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
                )
                
                download_url = f"{blob_path}?{sas_token}"
                logger.info(f"Generated SAS URL (expires in {expiry_hours}h)")
                return download_url
            else:
                # For local storage, return the path as-is
                return blob_path
                
        except Exception as e:
            logger.error(f"Failed to generate download URL: {str(e)}")
            return blob_path
    
    def _get_account_key(self) -> str:
        """Extract account key from connection string"""
        try:
            parts = settings.AZURE_STORAGE_CONNECTION_STRING.split(';')
            for part in parts:
                if part.startswith('AccountKey='):
                    return part.replace('AccountKey=', '')
            return ""
        except:
            return ""
    
    def list_document_versions(
        self, 
        user_id: str, 
        document_id: int
    ) -> List[Dict[str, Any]]:
        """
        List all versions of a document
        
        Args:
            user_id: User ID
            document_id: Document ID
            
        Returns:
            List of version metadata
        """
        try:
            prefix = f"{user_id}/{document_id}/"
            versions = []
            
            if self.blob_service_client:
                container_client = self.blob_service_client.get_container_client(
                    self.container_name
                )
                
                blobs = container_client.list_blobs(name_starts_with=prefix)
                
                for blob in blobs:
                    versions.append({
                        "name": blob.name,
                        "url": f"{container_client.url}/{blob.name}",
                        "size": blob.size,
                        "created": blob.creation_time,
                        "metadata": blob.metadata
                    })
            else:
                # For local storage
                versions = self._list_local_versions(user_id, document_id)
            
            logger.info(f"Found {len(versions)} versions for document {document_id}")
            return versions
            
        except Exception as e:
            logger.error(f"Failed to list versions: {str(e)}")
            return []
    
    # Local storage fallback methods
    
    def _save_to_local_storage(
        self, 
        content: bytes, 
        user_id: str, 
        document_id: int,
        filename: str, 
        version: int
    ) -> str:
        """Save file to local storage (for development)"""
        import os
        
        # Create directory structure
        base_dir = "data/documents"
        user_dir = os.path.join(base_dir, user_id)
        doc_dir = os.path.join(user_dir, str(document_id))
        
        os.makedirs(doc_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(doc_dir, f"v{version}_{filename}")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path
    
    def _load_from_local_storage(self, file_path: str) -> bytes:
        """Load file from local storage"""
        with open(file_path, "rb") as f:
            return f.read()
    
    def _delete_from_local_storage(self, file_path: str):
        """Delete file from local storage"""
        import os
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def _list_local_versions(
        self, 
        user_id: str, 
        document_id: int
    ) -> List[Dict[str, Any]]:
        """List versions from local storage"""
        import os
        
        doc_dir = os.path.join("data/documents", user_id, str(document_id))
        versions = []
        
        if os.path.exists(doc_dir):
            for filename in os.listdir(doc_dir):
                file_path = os.path.join(doc_dir, filename)
                stat = os.stat(file_path)
                
                versions.append({
                    "name": filename,
                    "url": file_path,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "metadata": {}
                })
        
        return versions
