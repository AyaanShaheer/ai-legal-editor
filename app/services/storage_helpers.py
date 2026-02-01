from typing import Tuple
from app.core.logging import logger


def parse_blob_path(blob_path: str) -> Tuple[str, int, int, str]:
    """
    Parse blob path to extract components
    
    Args:
        blob_path: Blob path (e.g., "user123/456/v3_document.docx")
        
    Returns:
        Tuple of (user_id, document_id, version, filename)
    """
    try:
        parts = blob_path.split('/')
        
        if len(parts) >= 3:
            user_id = parts[0]
            document_id = int(parts[1])
            
            # Extract version and filename
            version_filename = parts[2]
            version_str = version_filename.split('_')[0].replace('v', '')
            version = int(version_str)
            filename = '_'.join(version_filename.split('_')[1:])
            
            return user_id, document_id, version, filename
        else:
            raise ValueError("Invalid blob path format")
            
    except Exception as e:
        logger.error(f"Failed to parse blob path: {str(e)}")
        return "", 0, 0, ""


def generate_blob_name(user_id: str, document_id: int, filename: str, version: int) -> str:
    """
    Generate standardized blob name
    
    Args:
        user_id: User ID
        document_id: Document ID
        filename: Original filename
        version: Version number
        
    Returns:
        Blob name
    """
    return f"{user_id}/{document_id}/v{version}_{filename}"


def get_latest_version_number(versions: list) -> int:
    """
    Get the latest version number from version list
    
    Args:
        versions: List of version dictionaries
        
    Returns:
        Latest version number
    """
    if not versions:
        return 0
    
    max_version = 0
    
    for v in versions:
        try:
            name = v.get('name', '')
            version_str = name.split('/')[2].split('_')[0].replace('v', '')
            version = int(version_str)
            max_version = max(max_version, version)
        except:
            continue
    
    return max_version


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
