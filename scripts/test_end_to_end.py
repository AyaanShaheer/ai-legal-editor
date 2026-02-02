import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_full_workflow():
    """Test complete workflow from upload to patch application"""
    
    print("\n" + "="*60)
    print("END-TO-END WORKFLOW TEST")
    print("="*60)
    
    # Step 1: Upload document
    print("\n1️⃣  Uploading document...")
    
    sample_path = "tests/fixtures/sample_employment_agreement.docx"
    
    with open(sample_path, "rb") as f:
        files = {"file": ("contract.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 201:
        upload_data = response.json()
        document_id = upload_data["document_id"]
        print(f"   ✅ Document uploaded: ID {document_id}")
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(response.text)
        return
    
    # Step 2: Submit edit instruction
    print("\n2️⃣  Submitting edit instruction...")
    
    instruction = {
        "instruction": "Change the company name from Acme Corporation to TechCorp Industries and update the salary to $150,000"
    }
    
    response = requests.post(
        f"{BASE_URL}/documents/{document_id}/edit",
        json=instruction
    )
    
    if response.status_code == 201:
        job_data = response.json()
        job_id = job_data["job_id"]
        print(f"   ✅ Job created: ID {job_id}")
    else:
        print(f"   ❌ Job creation failed: {response.status_code}")
        print(response.text)
        return
    
    # Step 3: Poll job status
    print("\n3️⃣  Polling job status...")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        
        if response.status_code == 200:
            status_data = response.json()
            status = status_data["status"]
            
            print(f"   Attempt {attempt + 1}: Status = {status}")
            
            if status == "completed":
                print(f"   ✅ Job completed!")
                break
            elif status == "failed":
                print(f"   ❌ Job failed: {status_data.get('error_message')}")
                return
            
            time.sleep(2)
            attempt += 1
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            return
    
    if attempt >= max_attempts:
        print("   ⏱️  Timeout waiting for job completion")
        return
    
    # Step 4: Get patch preview
    print("\n4️⃣  Getting patch preview...")
    
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/patch")
    
    if response.status_code == 200:
        patch_data = response.json()
        patches = patch_data["patches"]
        print(f"   ✅ Retrieved {len(patches)} patches")
        
        for i, patch in enumerate(patches):
            print(f"\n   Patch {i+1}:")
            print(f"   Paragraph: {patch['paragraph_id']}")
            print(f"   Reasoning: {patch['reasoning']}")
    else:
        print(f"   ❌ Patch retrieval failed: {response.status_code}")
        return
    
    # Step 5: Apply patch
    print("\n5️⃣  Applying patch...")
    
    response = requests.post(
        f"{BASE_URL}/jobs/{job_id}/apply",
        json={"description": "Applied AI-generated changes"}
    )
    
    if response.status_code == 200:
        apply_data = response.json()
        version_number = apply_data["version_number"]
        print(f"   ✅ Patch applied! New version: {version_number}")
    else:
        print(f"   ❌ Patch application failed: {response.status_code}")
        print(response.text)
        return
    
    # Step 6: List versions
    print("\n6️⃣  Listing document versions...")
    
    response = requests.get(f"{BASE_URL}/documents/{document_id}/versions")
    
    if response.status_code == 200:
        versions_data = response.json()
        versions = versions_data["versions"]
        print(f"   ✅ Document has {len(versions)} versions")
        
        for v in versions:
            print(f"   - Version {v['version_number']}: {v['description']}")
    else:
        print(f"   ❌ Version listing failed: {response.status_code}")
    
    print("\n" + "="*60)
    print("WORKFLOW TEST COMPLETED SUCCESSFULLY")
    print("="*60)


if __name__ == "__main__":
    print("⚠️  Make sure these are running:")
    print("   1. Docker containers (PostgreSQL, Redis)")
    print("   2. Celery worker")
    print("   3. FastAPI server")
    print("\nPress Enter to continue...")
    input()
    
    test_full_workflow()
