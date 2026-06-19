import sys
import os
import random
from unittest.mock import patch
import requests
import threading
import uvicorn
import time

# Adjust path to find app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.config.database import SessionLocal
from app.models.users import User
from app.models.uploaded_file import UploadedFile, FileStatus
from app.models.processed_dataset import ProcessedDataset
from app.models.forecast_result import ForecastResult
from app.models.segment_result import SegmentResult
from app.models.ai_insight import AiInsight
from app.models.organizations import Organization
from app.models.subscriptions import Subscription

# Mock Pinecone index
class MockPineconeIndex:
    def upsert(self, vectors):
        return {}
    def query(self, vector, top_k, include_metadata, filter):
        file_ids = filter.get("file_id", {}).get("$in", [])
        if not file_ids:
            eq_val = filter.get("file_id", {}).get("$eq")
            if eq_val:
                file_ids = [eq_val]
        matches = []
        for fid in file_ids:
            matches.append({
                "score": 0.95,
                "id": f"file_{fid}_kpi_overall",
                "metadata": {
                    "chunk_type": "kpi_overall",
                    "file_id": fid,
                    "user_id": filter.get("user_id", {}).get("$eq", 1)
                }
            })
        return {"matches": matches}

def mock_get_pinecone_index():
    return MockPineconeIndex()

def mock_call_grok(prompt: str, max_tokens: int = 1000) -> str:
    return "Mocked Grok AI response: The business shows strong growth in sales and consistent customer segment distributions across the merged datasets."

# Helper to mock requests.get for Google Login
real_requests_get = requests.get

def mock_requests_get(url, *args, **kwargs):
    if "127.0.0.1:8001" in url or "localhost:8001" in url:
        return real_requests_get(url, *args, **kwargs)
    
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
        def json(self):
            return self.json_data
        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(f"Error {self.status_code}")
    
    if "oauth2.googleapis.com/tokeninfo" in url:
        return MockResponse({
            "email": "google_test_user@example.com",
            "name": "Google Test User",
            "aud": "mock-client-id"
        }, 200)
    return MockResponse({}, 404)

@patch("app.services.pinecone_service.get_pinecone_index", mock_get_pinecone_index)
@patch("app.services.ai_service.call_grok", mock_call_grok)
@patch("requests.get", mock_requests_get)
def run_tests():
    # Start the local uvicorn server on port 8001
    def start_server():
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")
        
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2.0)  # Give the server time to start up
    
    base_url = "http://127.0.0.1:8001"
    db = SessionLocal()
    
    print("\n--- Starting Subscription, Multi-Tenancy & RBAC Integration Tests ---")
    
    # Generate unique emails
    rand = random.randint(1000, 9999)
    email_admin = f"admin_{rand}@example.com"
    email_analyst = f"analyst_{rand}@example.com"
    email_viewer = f"viewer_{rand}@example.com"
    password = "SecurePassword123!"

    # Override settings to whitelist the dynamic admin email used in this test
    from app.config.settings import settings
    settings.PREDEFINED_ADMIN_EMAILS = f"admin@example.com,admin@insightforge.com,{email_admin}"
    
    # Clean up any existing test records
    cleanup_emails = [email_admin, email_analyst, email_viewer]
    for email in cleanup_emails:
        db.query(User).filter(User.email == email).delete()
    db.commit()
    
    # Helper to register and verify user
    def register_and_activate(email, name, role):
        reg = requests.post(f"{base_url}/auth/register", json={
            "email": email,
            "password": password,
            "name": name,
            "role": role
        })
        assert reg.status_code == 201, f"Failed registration for {email}"
        # Retrieve activation code from DB
        user = db.query(User).filter(User.email == email).first()
        verify = requests.post(f"{base_url}/auth/verify", json={
            "email": email,
            "code": user.verification_code
        })
        assert verify.status_code == 200, f"Failed verification for {email}"
        
        # Direct DB promotion for test admin (as public registration restricts it)
        if role == "admin":
            user.role = "admin"
            db.commit()
            db.refresh(user)

        # Log in
        login = requests.post(f"{base_url}/auth/login", json={
            "email": email,
            "password": password
        })
        assert login.status_code == 200, f"Failed login for {email}"
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # 1. Register users for different roles
    print("\n[TC1] Registering and activating Admin, Analyst, and Viewer...")
    admin_headers = register_and_activate(email_admin, "Admin User", "admin")
    analyst_headers = register_and_activate(email_analyst, "Analyst User", "analyst")
    viewer_headers = register_and_activate(email_viewer, "Viewer User", "viewer")
    
    # Get user objects
    admin_user = db.query(User).filter(User.email == email_admin).first()
    analyst_user = db.query(User).filter(User.email == email_analyst).first()
    viewer_user = db.query(User).filter(User.email == email_viewer).first()
    
    # 2. Put all users in the Admin's Organization (simulate team workspace)
    print("-> Mapping Analyst and Viewer to the Admin's Organization...")
    org_id = admin_user.organization_id
    assert org_id is not None, "Admin workspace was not auto-created"
    
    analyst_user.organization_id = org_id
    viewer_user.organization_id = org_id
    db.commit()
    print(f"-> Successfully mapped all users to Workspace ID: {org_id}")

    # 3. Test RBAC: Viewer is restricted from writing
    print("\n[TC2] Testing RBAC restrictions on Viewer...")
    
    csv_data = "order_date,sales_amount,customer_id,store_id,order_id\n2026-01-01,100.0,CUST1,S1,1\n"
    
    # Viewer tries to upload -> expects 403
    upload_fail = requests.post(
        f"{base_url}/upload/",
        files={"file": ("sales.csv", csv_data, "text/csv")},
        data={"file_type": "sales"},
        headers=viewer_headers
    )
    assert upload_fail.status_code == 403, f"Expected 403, got {upload_fail.status_code}"
    print("-> Viewer upload blocked successfully (403 Forbidden).")
    
    # Viewer tries to forecast -> expects 403
    forecast_fail = requests.post(
        f"{base_url}/forecast/",
        json={"file_ids": [1], "steps": 3},
        headers=viewer_headers
    )
    assert forecast_fail.status_code == 403, f"Expected 403, got {forecast_fail.status_code}"
    print("-> Viewer forecasting blocked successfully (403 Forbidden).")

    # 4. Test Subscription Limits (Free Tier quota = max 3 files)
    print("\n[TC3] Testing Free Tier file upload limits (max 3 files)...")
    
    # Upload 3 files using Analyst
    file_ids = []
    for i in range(1, 4):
        res = requests.post(
            f"{base_url}/upload/",
            files={"file": (f"sales_{i}.csv", csv_data, "text/csv")},
            data={"file_type": "sales"},
            headers=analyst_headers
        )
        assert res.status_code == 201, f"Upload {i} failed: {res.text}"
        file_id = res.json()["file_id"]
        file_ids.append(file_id)
        # Wait for background task to finish processing
        for _ in range(40):
            status_res = requests.get(f"{base_url}/upload/{file_id}", headers=analyst_headers)
            if status_res.status_code == 200 and status_res.json().get("status") in ["processed", "failed"]:
                break
            time.sleep(0.2)
        # Manually preprocess
        requests.post(f"{base_url}/upload/preprocess/{file_id}", headers=analyst_headers)
        requests.post(f"{base_url}/upload/embed/{file_id}", headers=analyst_headers)
    print(f"-> Successfully uploaded and preprocessed 3 files: {file_ids}")
    
    # Upload 4th file -> expects 402 Payment Required
    upload_limit_res = requests.post(
        f"{base_url}/upload/",
        files={"file": ("sales_4.csv", csv_data, "text/csv")},
        data={"file_type": "sales"},
        headers=analyst_headers
    )
    assert upload_limit_res.status_code == 402, f"Expected 402, got {upload_limit_res.status_code}"
    print("-> 4th File upload correctly blocked under Free Tier (402 Payment Required).")

    # 5. Test AI Chat Gate (Free Tier AI disabled)
    print("\n[TC4] Testing Free Tier AI Chat Gate...")
    ai_fail_res = requests.post(
        f"{base_url}/ai/ask",
        json={"file_ids": file_ids[:2], "question": "Analyze these files"},
        headers=analyst_headers
    )
    assert ai_fail_res.status_code == 402, f"Expected 402, got {ai_fail_res.status_code}"
    print("-> AI Chat correctly blocked under Free Tier (402 Payment Required).")

    # 6. Test Billing Upgrades
    print("\n[TC5] Testing Billing Upgrade authorization...")
    # Analyst tries to upgrade -> expects 403
    upgrade_fail = requests.post(
        f"{base_url}/billing/test-upgrade",
        json={"plan_tier": "pro"},
        headers=analyst_headers
    )
    assert upgrade_fail.status_code == 403, f"Expected 403, got {upgrade_fail.status_code}"
    print("-> Non-admin upgrade blocked successfully.")

    # Admin upgrades workspace to Pro -> expects 200
    upgrade_success = requests.post(
        f"{base_url}/billing/test-upgrade",
        json={"plan_tier": "pro"},
        headers=admin_headers
    )
    assert upgrade_success.status_code == 200, f"Upgrade failed: {upgrade_success.text}"
    print("-> Workspace successfully upgraded to Pro by Admin.")

    # 7. Test unlocked limits on Pro Tier
    print("\n[TC6] Testing Pro Tier unlocked capabilities...")
    # Analyst can now upload 4th file
    upload_4th_success = requests.post(
        f"{base_url}/upload/",
        files={"file": ("sales_4.csv", csv_data, "text/csv")},
        data={"file_type": "sales"},
        headers=analyst_headers
    )
    assert upload_4th_success.status_code == 201, f"Expected 201 on Pro tier, got {upload_4th_success.status_code}"
    file_id_4 = upload_4th_success.json()["file_id"]
    file_ids.append(file_id_4)
    # Wait for background task to finish processing
    for _ in range(40):
        status_res = requests.get(f"{base_url}/upload/{file_id_4}", headers=analyst_headers)
        if status_res.status_code == 200 and status_res.json().get("status") in ["processed", "failed"]:
            break
        time.sleep(0.2)
    # Preprocess 4th file
    requests.post(f"{base_url}/upload/preprocess/{file_id_4}", headers=analyst_headers)
    requests.post(f"{base_url}/upload/embed/{file_id_4}", headers=analyst_headers)
    print(f"-> Successfully uploaded 4th file on Pro tier (File ID: {file_id_4}).")

    # Analyst can now call AI RAG Chat
    ai_success_res = requests.post(
        f"{base_url}/ai/ask",
        json={"file_ids": file_ids, "question": "Analyze all sales trend"},
        headers=analyst_headers
    )
    assert ai_success_res.status_code == 200, f"AI ask failed: {ai_success_res.text}"
    print("-> AI Chat successfully unlocked and completed on Pro Tier.")

    # 8. Test Team Workspace File Sharing
    print("\n[TC7] Testing Workspace history sharing...")
    # Viewer lists files -> should see all 4 files uploaded by the Analyst
    viewer_files_res = requests.get(f"{base_url}/upload/", headers=viewer_headers)
    assert viewer_files_res.status_code == 200
    viewer_files = viewer_files_res.json()
    assert len(viewer_files) == 4, f"Viewer expected 4 files, saw {len(viewer_files)}"
    print("-> Workspace team members successfully share identical file history lists.")

    # ────────────────────────────────────────────────────────────────
    # Clean Up Test Records
    # ────────────────────────────────────────────────────────────────
    print("\n[TC8] Cleaning up database test records...")
    try:
        # Delete dependent tables
        db.query(SegmentResult).filter(SegmentResult.file_id.in_(file_ids)).delete(synchronize_session=False)
        db.query(ForecastResult).filter(ForecastResult.file_id.in_(file_ids)).delete(synchronize_session=False)
        db.query(ProcessedDataset).filter(ProcessedDataset.file_id.in_(file_ids)).delete(synchronize_session=False)
        
        # Clean raw data rows
        from app.models.raw_data_row import RawDataRow
        db.query(RawDataRow).filter(RawDataRow.file_id.in_(file_ids)).delete(synchronize_session=False)
        
        db.query(UploadedFile).filter(UploadedFile.organization_id == org_id).delete(synchronize_session=False)
        
        # Delete users, sub, org
        db.query(Subscription).filter(Subscription.organization_id == org_id).delete(synchronize_session=False)
        db.query(User).filter(User.organization_id == org_id).delete(synchronize_session=False)
        db.query(Organization).filter(Organization.id == org_id).delete(synchronize_session=False)
        
        db.commit()
        print("-> Clean up completed successfully.")
    except Exception as cleanup_err:
        db.rollback()
        print(f"-> Cleanup failed: {str(cleanup_err)}")
    finally:
        db.close()

    print("\n--- All tests completed successfully! ---")

if __name__ == "__main__":
    run_tests()
