"""Tests for reporter + admin reporter endpoints (P0 fix: datetime/schema)."""
import os
import random
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or "https://kaizer-newsbot.preview.emergentagent.com"

REQUIRED_REPORTER_FIELDS = {"id", "reporter_id", "name", "phone", "email", "photo",
                            "location", "bio", "status", "created_at",
                            "news_submitted", "news_approved"}
REQUIRED_NEWS_FIELDS = {"id", "reporter_id", "reporter_name", "title", "summary",
                        "news_type", "status", "created_at", "image", "video_url",
                        "reporter_video_url"}


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def test_phone():
    return f"9999{random.randint(100000, 999999)}"


class TestAdminReporters:
    def test_get_admin_reporters_200(self, session):
        r = session.get(f"{BASE_URL}/api/admin/reporters", timeout=30)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:400]}"
        data = r.json()
        assert isinstance(data, list)
        if data:
            missing = REQUIRED_REPORTER_FIELDS - set(data[0].keys())
            assert not missing, f"Missing fields in reporter: {missing}"

    def test_get_admin_reporter_news_200(self, session):
        r = session.get(f"{BASE_URL}/api/admin/reporter-news", timeout=30)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:400]}"
        data = r.json()
        assert isinstance(data, list)
        if data:
            missing = REQUIRED_NEWS_FIELDS - set(data[0].keys())
            assert not missing, f"Missing fields in reporter news: {missing}"


class TestReporterRegistration:
    def test_register_reporter(self, session, test_phone):
        payload = {
            "name": "TEST_Reporter",
            "phone": test_phone,
            "email": "test@example.com",
            "photo": "",
            "location": "Hyderabad",
            "bio": "Testing",
        }
        r = session.post(f"{BASE_URL}/api/reporter/register", json=payload, timeout=30)
        assert r.status_code == 200, f"{r.status_code}: {r.text[:400]}"
        data = r.json()
        assert data["status"] == "pending"
        assert data["phone"] == test_phone
        assert data["reporter_id"].startswith("NP-")

    def test_check_after_register(self, session, test_phone):
        r = session.get(f"{BASE_URL}/api/reporter/check/{test_phone}", timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert data["registered"] is True
        assert data["status"] == "pending"

    def test_approve_reporter(self, session, test_phone):
        chk = session.get(f"{BASE_URL}/api/reporter/check/{test_phone}", timeout=30).json()
        rid = chk["id"]
        r = session.post(f"{BASE_URL}/api/admin/reporters/{rid}/approve", timeout=30)
        assert r.status_code == 200, r.text[:400]
        data = r.json()
        assert data["reporter"]["status"] == "approved"
        assert data["reporter"]["approved_at"]

    def test_reject_reporter(self, session):
        # Register another, then reject
        phone = f"9998{random.randint(100000, 999999)}"
        reg = session.post(f"{BASE_URL}/api/reporter/register",
                          json={"name": "TEST_Rej", "phone": phone, "location": "Hyd"},
                          timeout=30).json()
        rid = reg["id"]
        r = session.post(f"{BASE_URL}/api/admin/reporters/{rid}/reject?reason=test",
                        timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert data["reporter"]["status"] == "rejected"
        assert data["reporter"]["rejection_reason"] == "test"


class TestRegression:
    def test_news_feed_still_works(self, session):
        r = session.get(f"{BASE_URL}/api/news/feed?limit=5", timeout=30)
        assert r.status_code == 200, r.text[:400]
        data = r.json()
        assert isinstance(data, list)
