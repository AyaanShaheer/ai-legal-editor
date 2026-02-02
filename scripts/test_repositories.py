import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import async_session_maker
from app.repositories import DocumentRepository, DocumentVersionRepository, JobRepository
from app.models.database import JobStatus


async def test_document_repository():
    """Test document repository operations"""
    
    print("\n" + "="*60)
    print("DOCUMENT REPOSITORY TEST")
    print("="*60)
    
    async with async_session_maker() as db:
        repo = DocumentRepository(db)
        
        # Create documents
        print("\n1️⃣  Creating documents...")
        doc1 = await repo.create(
            user_id="user_001",
            original_filename="contract.docx",
            blob_path="/storage/user_001/1/v1_contract.docx"
        )
        print(f"   ✅ Created document {doc1.id}: {doc1.original_filename}")
        
        doc2 = await repo.create(
            user_id="user_001",
            original_filename="agreement.docx",
            blob_path="/storage/user_001/2/v1_agreement.docx"
        )
        print(f"   ✅ Created document {doc2.id}: {doc2.original_filename}")
        
        doc3 = await repo.create(
            user_id="user_002",
            original_filename="policy.docx",
            blob_path="/storage/user_002/3/v1_policy.docx"
        )
        print(f"   ✅ Created document {doc3.id}: {doc3.original_filename}")
        
        # Get by user
        print("\n2️⃣  Retrieving user documents...")
        user1_docs = await repo.get_by_user("user_001")
        print(f"   ✅ User 001 has {len(user1_docs)} documents")
        
        user2_docs = await repo.get_by_user("user_002")
        print(f"   ✅ User 002 has {len(user2_docs)} documents")
        
        # Search by filename
        print("\n3️⃣  Searching by filename...")
        search_results = await repo.search_by_filename("user_001", "contract")
        print(f"   ✅ Found {len(search_results)} documents matching 'contract'")
        
        # Count by user
        print("\n4️⃣  Counting user documents...")
        count = await repo.count_by_user("user_001")
        print(f"   ✅ User 001 has {count} total documents")
        
        # Update document
        print("\n5️⃣  Updating document...")
        updated = await repo.update(doc1.id, original_filename="updated_contract.docx")
        print(f"   ✅ Updated: {updated.original_filename}")
        
        await db.commit()
        
        return doc1.id, doc2.id


async def test_version_repository(document_id: int):
    """Test version repository operations"""
    
    print("\n" + "="*60)
    print("VERSION REPOSITORY TEST")
    print("="*60)
    
    async with async_session_maker() as db:
        repo = DocumentVersionRepository(db)
        
        # Create versions
        print("\n1️⃣  Creating versions...")
        v1 = await repo.create(
            document_id=document_id,
            version_number=1,
            blob_path=f"/storage/user_001/{document_id}/v1_contract.docx",
            description="Initial version"
        )
        print(f"   ✅ Created version {v1.version_number}")
        
        v2 = await repo.create(
            document_id=document_id,
            version_number=2,
            blob_path=f"/storage/user_001/{document_id}/v2_contract.docx",
            description="Updated with AI changes"
        )
        print(f"   ✅ Created version {v2.version_number}")
        
        # Get all versions
        print("\n2️⃣  Retrieving versions...")
        versions = await repo.get_by_document(document_id)
        print(f"   ✅ Found {len(versions)} versions")
        
        # Get latest version
        print("\n3️⃣  Getting latest version...")
        latest = await repo.get_latest_version(document_id)
        print(f"   ✅ Latest version: {latest.version_number}")
        
        # Get next version number
        print("\n4️⃣  Calculating next version number...")
        next_version = await repo.get_next_version_number(document_id)
        print(f"   ✅ Next version will be: {next_version}")
        
        # Get specific version
        print("\n5️⃣  Getting specific version...")
        specific = await repo.get_version_by_number(document_id, 1)
        print(f"   ✅ Version 1 description: {specific.description}")
        
        await db.commit()


async def test_job_repository(document_id: int):
    """Test job repository operations"""
    
    print("\n" + "="*60)
    print("JOB REPOSITORY TEST")
    print("="*60)
    
    async with async_session_maker() as db:
        repo = JobRepository(db)
        
        # Create jobs
        print("\n1️⃣  Creating jobs...")
        job1 = await repo.create(
            document_id=document_id,
            instruction="Change company name to TechCorp",
            status=JobStatus.PENDING
        )
        print(f"   ✅ Created job {job1.id}: {job1.status}")
        
        job2 = await repo.create(
            document_id=document_id,
            instruction="Update salary figures",
            status=JobStatus.PENDING
        )
        print(f"   ✅ Created job {job2.id}: {job2.status}")
        
        # Get pending jobs
        print("\n2️⃣  Getting pending jobs...")
        pending = await repo.get_pending_jobs()
        print(f"   ✅ Found {len(pending)} pending jobs")
        
        # Update status
        print("\n3️⃣  Updating job status...")
        updated = await repo.update_status(job1.id, JobStatus.PROCESSING)
        print(f"   ✅ Job {job1.id} status: {updated.status}")
        print(f"   Started at: {updated.started_at}")
        
        # Save patch
        print("\n4️⃣  Saving patch data...")
        patch_json = '{"patches": [{"paragraph_id": 1, "text": "new text"}]}'
        completed = await repo.save_patch(job1.id, patch_json)
        print(f"   ✅ Job {job1.id} completed with patch data")
        print(f"   Status: {completed.status}")
        print(f"   Completed at: {completed.completed_at}")
        
        # Get by document
        print("\n5️⃣  Getting document jobs...")
        doc_jobs = await repo.get_by_document(document_id)
        print(f"   ✅ Found {len(doc_jobs)} jobs for document")
        
        # Count by status
        print("\n6️⃣  Counting by status...")
        pending_count = await repo.count_by_status(JobStatus.PENDING)
        completed_count = await repo.count_by_status(JobStatus.COMPLETED)
        print(f"   Pending: {pending_count}")
        print(f"   Completed: {completed_count}")
        
        await db.commit()


async def main():
    """Run all repository tests"""
    
    # Test documents
    doc1_id, doc2_id = await test_document_repository()
    
    # Test versions
    await test_version_repository(doc1_id)
    
    # Test jobs
    await test_job_repository(doc1_id)
    
    print("\n" + "="*60)
    print("ALL REPOSITORY TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
