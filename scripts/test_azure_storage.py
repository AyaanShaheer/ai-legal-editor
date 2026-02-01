import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.azure_storage import AzureStorageService
from app.core.logging import logger


def test_local_storage():
    """Test local storage fallback (when Azure not configured)"""
    
    print("\n" + "="*60)
    print("AZURE STORAGE SERVICE TEST (Local Fallback)")
    print("="*60)
    
    storage = AzureStorageService()
    
    # Test data
    user_id = "test_user_001"
    document_id = 1
    filename = "test_document.docx"
    
    # Load sample document
    sample_path = "tests/fixtures/sample_employment_agreement.docx"
    
    if not Path(sample_path).exists():
        print(f"❌ Sample document not found: {sample_path}")
        return
    
    with open(sample_path, "rb") as f:
        content = f.read()
    
    print(f"\n📄 Loaded test document: {len(content)} bytes")
    
    # Test 1: Upload
    print("\n1️⃣  Testing upload...")
    blob_path_v1 = storage.upload_document(
        content, user_id, document_id, filename, version=1
    )
    print(f"   ✅ Uploaded v1: {blob_path_v1}")
    
    # Test 2: Upload another version
    print("\n2️⃣  Testing second version upload...")
    blob_path_v2 = storage.upload_document(
        content, user_id, document_id, filename, version=2
    )
    print(f"   ✅ Uploaded v2: {blob_path_v2}")
    
    # Test 3: Download
    print("\n3️⃣  Testing download...")
    downloaded = storage.download_document(blob_path_v1)
    print(f"   ✅ Downloaded: {len(downloaded)} bytes")
    print(f"   Content matches: {downloaded == content}")
    
    # Test 4: List versions
    print("\n4️⃣  Testing version listing...")
    versions = storage.list_document_versions(user_id, document_id)
    print(f"   ✅ Found {len(versions)} versions:")
    for v in versions:
        print(f"      - {v['name']} ({v['size']} bytes)")
    
    # Test 5: Generate download URL
    print("\n5️⃣  Testing download URL generation...")
    download_url = storage.generate_download_url(blob_path_v1, expiry_hours=2)
    print(f"   ✅ Download URL: {download_url[:80]}...")
    
    # Test 6: Upload with different user
    print("\n6️⃣  Testing multi-user isolation...")
    user2_id = "test_user_002"
    blob_path_user2 = storage.upload_document(
        content, user2_id, document_id, filename, version=1
    )
    print(f"   ✅ User 2 upload: {blob_path_user2}")
    
    versions_user1 = storage.list_document_versions(user_id, document_id)
    versions_user2 = storage.list_document_versions(user2_id, document_id)
    
    print(f"   User 1 versions: {len(versions_user1)}")
    print(f"   User 2 versions: {len(versions_user2)}")
    print(f"   ✅ Users isolated: {len(versions_user1) != len(versions_user2) or versions_user1[0]['name'] != versions_user2[0]['name']}")
    
    # Test 7: Delete
    print("\n7️⃣  Testing deletion...")
    deleted = storage.delete_document(blob_path_v2)
    print(f"   ✅ Deleted v2: {deleted}")
    
    versions_after = storage.list_document_versions(user_id, document_id)
    print(f"   Versions after delete: {len(versions_after)}")
    
    print("\n" + "="*60)
    print("LOCAL STORAGE TEST COMPLETED")
    print("="*60)
    print(f"\n💾 Files stored in: data/documents/")


def test_storage_error_handling():
    """Test error handling"""
    
    print("\n" + "="*60)
    print("ERROR HANDLING TEST")
    print("="*60)
    
    storage = AzureStorageService()
    
    # Test 1: Download non-existent file
    print("\n1️⃣  Testing download of non-existent file...")
    try:
        storage.download_document("non_existent_path.docx")
        print("   ❌ Should have raised exception")
    except Exception as e:
        print(f"   ✅ Caught exception: {type(e).__name__}")
    
    # Test 2: Delete non-existent file
    print("\n2️⃣  Testing delete of non-existent file...")
    result = storage.delete_document("non_existent_path.docx")
    print(f"   Result: {result}")
    
    print("\n" + "="*60)
    print("ERROR HANDLING TEST COMPLETED")
    print("="*60)


if __name__ == "__main__":
    test_local_storage()
    print("\n\n")
    test_storage_error_handling()
    
    print("\n" + "="*60)
    print("ALL STORAGE TESTS COMPLETED")
    print("="*60)
