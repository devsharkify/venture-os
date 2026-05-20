# Test Guest Mode, Reporter Login, and Admin OTP flow
# Mint Street - Iteration 9 Tests

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Basic API health check"""
    
    def test_api_root(self):
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        assert "NewsPulse" in response.json().get("message", "")
        print("PASS: API root endpoint working")


class TestGuestModeAPIs:
    """Test that news feed APIs work without authentication (guest mode)"""
    
    def test_news_feed_no_auth(self):
        """Guest users can access news feed without login"""
        response = requests.get(f"{BASE_URL}/api/news/feed")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: News feed accessible without auth, {len(data)} articles")
    
    def test_news_categories_no_auth(self):
        """Guest users can access categories without login"""
        response = requests.get(f"{BASE_URL}/api/news/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 10
        print(f"PASS: Categories accessible without auth, {len(data['categories'])} categories")
    
    def test_news_by_category_no_auth(self):
        """Guest users can filter news by category"""
        response = requests.get(f"{BASE_URL}/api/news/category/national")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("PASS: Category filter accessible without auth")


class TestAdminMockOTP:
    """Test admin phone 9876543210 with mock OTP 123456"""
    
    def test_send_otp_admin_phone(self):
        """Send OTP to admin phone returns success"""
        response = requests.post(f"{BASE_URL}/api/auth/send-otp", json={
            "mobile": "9876543210",
            "country_code": "91"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "otp_sent"
        # Admin phone should NOT return debug_otp (it's hardcoded)
        print("PASS: Send OTP to admin phone (9876543210) successful")
    
    def test_verify_otp_admin_correct(self):
        """Verify admin with correct OTP 123456 returns is_admin=true"""
        # First send OTP
        requests.post(f"{BASE_URL}/api/auth/send-otp", json={
            "mobile": "9876543210",
            "country_code": "91"
        })
        
        # Verify with correct OTP
        response = requests.post(f"{BASE_URL}/api/auth/verify-otp", json={
            "mobile": "9876543210",
            "otp": "123456",
            "country_code": "91"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "verified"
        assert data["is_admin"] == True
        assert "user" in data
        print("PASS: Admin verified with OTP 123456, is_admin=true")
    
    def test_verify_otp_admin_wrong(self):
        """Wrong OTP for admin fails"""
        # First send OTP
        requests.post(f"{BASE_URL}/api/auth/send-otp", json={
            "mobile": "9876543210",
            "country_code": "91"
        })
        
        # Verify with wrong OTP
        response = requests.post(f"{BASE_URL}/api/auth/verify-otp", json={
            "mobile": "9876543210",
            "otp": "999999",
            "country_code": "91"
        })
        assert response.status_code == 400
        print("PASS: Wrong OTP for admin rejected")
    
    def test_non_admin_user_is_admin_false(self):
        """Regular user returns is_admin=false"""
        test_phone = "1234567890"
        
        # Send OTP
        send_response = requests.post(f"{BASE_URL}/api/auth/send-otp", json={
            "mobile": test_phone,
            "country_code": "91"
        })
        assert send_response.status_code == 200
        
        # Get debug OTP for non-admin
        debug_otp = send_response.json().get("debug_otp")
        if not debug_otp:
            pytest.skip("No debug OTP returned - real SMS mode")
        
        # Verify
        response = requests.post(f"{BASE_URL}/api/auth/verify-otp", json={
            "mobile": test_phone,
            "otp": debug_otp,
            "country_code": "91"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] == False
        print("PASS: Non-admin user gets is_admin=false")


class TestReporterCheckAPI:
    """Test reporter check endpoint used after OTP verification"""
    
    def test_reporter_check_unregistered(self):
        """Check reporter status for unregistered phone"""
        response = requests.get(f"{BASE_URL}/api/reporter/check/0000000000")
        assert response.status_code == 200
        data = response.json()
        assert data["registered"] == False
        print("PASS: Unregistered phone returns registered=false")


class TestBreakingNewsNotifications:
    """Test breaking news notification endpoint"""
    
    def test_breaking_news_endpoint(self):
        """GET /api/notifications/breaking returns breaking articles"""
        response = requests.get(f"{BASE_URL}/api/notifications/breaking")
        assert response.status_code == 200
        data = response.json()
        assert "breaking" in data
        assert "count" in data
        assert isinstance(data["breaking"], list)
        print(f"PASS: Breaking news endpoint working, {data['count']} breaking articles")


class TestServiceWorkerAccess:
    """Test service worker file accessibility"""
    
    def test_sw_js_accessible(self):
        """Service worker file is accessible at /sw.js"""
        response = requests.get(f"{BASE_URL}/sw.js")
        # Should be 200 or served by frontend
        assert response.status_code in [200, 304]
        # Check if it contains service worker code
        if response.status_code == 200:
            content = response.text
            assert "addEventListener" in content or "serviceWorker" in content.lower() or "self" in content
        print("PASS: Service worker file accessible at /sw.js")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
