"""Startup application backend tests"""
import os
import io
import random
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://kaizer-newsbot.preview.emergentagent.com").rstrip("/")


def _mob():
    return "9" + "".join([str(random.randint(0, 9)) for _ in range(9)])


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    return s


@pytest.fixture(scope="module")
def created_app(session):
    payload = {
        "name": "TEST Founder",
        "mobile": _mob(),
        "email": "test_founder@example.com",
        "idea": "AI-driven hyperlocal news verification platform for Hyderabad youth founders",
        "age": 24,
        "colony": "Banjara Hills",
        "area": "Jubilee Hills",
        "city": "Hyderabad",
        "is_woman_founder": True,
    }
    r = session.post(f"{BASE_URL}/api/startup/apply", json=payload, timeout=20)
    assert r.status_code == 200, r.text
    return r.json(), payload


# --- Submit tests ---
def test_submit_valid_payload_with_location_fields(created_app):
    data, payload = created_app
    assert data["status"] == "submitted"
    assert "id" in data and len(data["id"]) > 0
    assert "created_at" in data
    assert data["mobile"] == payload["mobile"]
    assert data["email"] == payload["email"].lower()
    assert data["is_woman_founder"] is True
    # NEW: structured location fields
    assert data["colony"] == "Banjara Hills"
    assert data["area"] == "Jubilee Hills"
    assert data["city"] == "Hyderabad"
    # 'location' must NOT exist anymore
    assert "location" not in data


def test_admin_list_returns_new_location_fields(session, created_app):
    data, _ = created_app
    r = session.get(f"{BASE_URL}/api/admin/startup-applications", timeout=15)
    assert r.status_code == 200
    arr = r.json()
    found = next((a for a in arr if a["id"] == data["id"]), None)
    assert found is not None
    assert found["colony"] == "Banjara Hills"
    assert found["area"] == "Jubilee Hills"
    assert found["city"] == "Hyderabad"
    assert "location" not in found


# --- CSV export tests ---
EXPECTED_COLS = "id,name,mobile,email,age,colony,area,city,is_woman_founder,idea,status,rejection_reason,pitch_pdf_url,pitch_video_url,created_at,updated_at"


def test_csv_export_default(session, created_app):
    r = session.get(f"{BASE_URL}/api/admin/startup-applications/export", timeout=20)
    assert r.status_code == 200
    ctype = r.headers.get("content-type", "").lower()
    assert "text/csv" in ctype
    assert "charset=utf-8" in ctype
    raw = r.content
    # UTF-8 BOM
    assert raw[:3] == b"\xef\xbb\xbf", f"missing BOM, got: {raw[:8]!r}"
    body = raw.decode("utf-8-sig")
    first_line = body.splitlines()[0]
    cols_in_csv = [c.strip('"') for c in first_line.split(",")]
    assert cols_in_csv == EXPECTED_COLS.split(","), f"columns mismatch: {cols_in_csv}"


def test_csv_export_status_filter(session):
    # Create a dedicated app and promote it to shortlisted (don't mutate shared fixture)
    payload = {
        "name": "TEST CSV Filter",
        "mobile": _mob(),
        "email": "csv_filter@example.com",
        "idea": "Idea for csv export filter status verification more than thirty chars",
        "age": 25,
        "colony": "X", "area": "Y", "city": "Hyderabad",
    }
    cr = session.post(f"{BASE_URL}/api/startup/apply", json=payload, timeout=15)
    assert cr.status_code == 200
    new_id = cr.json()["id"]
    session.post(
        f"{BASE_URL}/api/admin/startup-applications/{new_id}/update-status",
        params={"status": "shortlisted"},
        timeout=15,
    )
    r = session.get(f"{BASE_URL}/api/admin/startup-applications/export?status=submitted", timeout=20)
    assert r.status_code == 200
    body = r.content.decode("utf-8-sig")
    rows = body.splitlines()
    # Header + only rows with status submitted
    for row in rows[1:]:
        # status is the 11th column (after id,name,mobile,email,age,colony,area,city,is_woman_founder,idea,status...)
        # csv has QUOTE_ALL so split safely with csv reader
        import csv as _csv
        reader = _csv.reader([row])
        cells = next(reader)
        assert cells[10] == "submitted", f"unexpected status row: {cells[10]}"


def test_submit_invalid_mobile_short(session):
    r = session.post(f"{BASE_URL}/api/startup/apply", json={
        "name": "X User", "mobile": "123", "email": "x@y.com",
        "idea": "A" * 35,
    }, timeout=15)
    assert r.status_code == 422
    assert "Mobile must be exactly 10 digits" in r.text


def test_submit_invalid_mobile_alphanum(session):
    r = session.post(f"{BASE_URL}/api/startup/apply", json={
        "name": "X User", "mobile": "abcd123456", "email": "x@y.com",
        "idea": "A" * 35,
    }, timeout=15)
    assert r.status_code == 422


def test_submit_short_idea(session):
    r = session.post(f"{BASE_URL}/api/startup/apply", json={
        "name": "X User", "mobile": _mob(), "email": "x@y.com",
        "idea": "too short",
    }, timeout=15)
    assert r.status_code == 422
    assert "30 characters" in r.text or "30" in r.text


def test_submit_malformed_email(session):
    r = session.post(f"{BASE_URL}/api/startup/apply", json={
        "name": "X User", "mobile": _mob(), "email": "not-an-email",
        "idea": "A valid description of an idea more than 30 chars",
    }, timeout=15)
    assert r.status_code == 422


def test_submit_duplicate_mobile(session, created_app):
    _, payload = created_app
    r = session.post(f"{BASE_URL}/api/startup/apply", json=payload, timeout=15)
    assert r.status_code == 400
    assert "mobile" in r.text.lower()


# --- Check ---
def test_check_existing(session, created_app):
    _, payload = created_app
    r = session.get(f"{BASE_URL}/api/startup/check/{payload['mobile']}", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["applied"] is True
    assert data["status"] == "submitted"
    assert "id" in data


def test_check_new(session):
    r = session.get(f"{BASE_URL}/api/startup/check/{_mob()}", timeout=10)
    assert r.status_code == 200
    assert r.json()["applied"] is False


# --- Admin list ---
def test_admin_list(session, created_app):
    r = session.get(f"{BASE_URL}/api/admin/startup-applications", timeout=15)
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list)
    assert len(arr) > 0
    item = arr[0]
    for k in ["id", "name", "mobile", "email", "idea", "status", "is_woman_founder", "created_at"]:
        assert k in item, f"Missing {k}"


# --- Update status ---
def test_update_status_valid(session, created_app):
    data, _ = created_app
    r = session.post(
        f"{BASE_URL}/api/admin/startup-applications/{data['id']}/update-status",
        params={"status": "shortlisted"},
        timeout=15,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["application"]["status"] == "shortlisted"


def test_update_status_invalid(session, created_app):
    data, _ = created_app
    r = session.post(
        f"{BASE_URL}/api/admin/startup-applications/{data['id']}/update-status",
        params={"status": "bogus"},
        timeout=15,
    )
    assert r.status_code == 400


# --- Upload document ---
def test_upload_document_pdf(session):
    pdf = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
    files = {"file": ("test.pdf", io.BytesIO(pdf), "application/pdf")}
    try:
        r = session.post(f"{BASE_URL}/api/upload/document", files=files, timeout=60)
    except requests.exceptions.ReadTimeout:
        pytest.skip("ImageKit upload timed out")
    if r.status_code == 500 and "Upload failed" in r.text:
        pytest.skip(f"ImageKit issue: {r.text[:120]}")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "url" in data
    assert "file_id" in data


def test_upload_document_invalid_ext(session):
    files = {"file": ("evil.exe", io.BytesIO(b"MZ"), "application/octet-stream")}
    r = session.post(f"{BASE_URL}/api/upload/document", files=files, timeout=15)
    assert r.status_code == 400
    assert "PDF" in r.text or "DOC" in r.text


# --- Regression ---
def test_regression_admin_reporters(session):
    r = session.get(f"{BASE_URL}/api/admin/reporters", timeout=15)
    assert r.status_code == 200


def test_regression_news_feed(session):
    r = session.get(f"{BASE_URL}/api/news/feed?limit=5", timeout=15)
    assert r.status_code == 200
