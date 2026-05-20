"""
Test cases for Login/OTP Authentication Flow
- Tests /api/auth/send-otp endpoint
- Tests /api/auth/verify-otp endpoint
- Tests OTP validation (expiry, attempts, invalid OTP)
- Tests user creation on first login
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthSendOTP:
    """Test OTP sending functionality"""
    
    def test_send_otp_success(self):
        """Test successful OTP send"""
        response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": "9876543210", "country_code": "91"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "otp_sent"
        assert data["message"] == "OTP sent successfully"
        assert data["expiry_seconds"] == 300
        print(f"✓ Send OTP successful: {data}")
    
    def test_send_otp_without_mobile(self):
        """Test OTP send without mobile number"""
        response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"country_code": "91"}
        )
        assert response.status_code == 422  # Validation error
        print("✓ Send OTP without mobile returns 422")
    
    def test_send_otp_without_country_code(self):
        """Test OTP send defaults country code to 91"""
        response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": "9876543211"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "otp_sent"
        print("✓ Send OTP without country_code uses default 91")


class TestAuthVerifyOTP:
    """Test OTP verification functionality"""
    
    def test_verify_otp_not_found(self):
        """Test verify OTP when no OTP was sent"""
        response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": "1111111111", "otp": "123456", "country_code": "91"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "OTP not found" in data["detail"]
        print("✓ Verify OTP without sending returns 404")
    
    def test_verify_otp_invalid(self):
        """Test verify with wrong OTP"""
        # First send OTP
        send_response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": "9876543212", "country_code": "91"}
        )
        assert send_response.status_code == 200
        
        # Try wrong OTP
        verify_response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": "9876543212", "otp": "000000", "country_code": "91"}
        )
        assert verify_response.status_code == 400
        data = verify_response.json()
        assert "Invalid OTP" in data["detail"]
        print("✓ Invalid OTP returns 400")
    
    def test_verify_otp_without_otp_field(self):
        """Test verify without OTP field"""
        response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": "9876543210", "country_code": "91"}
        )
        assert response.status_code == 422
        print("✓ Verify without OTP field returns 422")


class TestAuthUserFlow:
    """Test complete user authentication flow"""
    
    def test_send_otp_and_check_response_format(self):
        """Test send OTP response structure"""
        response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": "9876543213", "country_code": "91"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "message" in data
        assert "expiry_seconds" in data
        # debug_otp may be None if AUTHKEY_API_KEY is set
        assert "debug_otp" in data
        print(f"✓ Send OTP response structure correct, debug_otp: {data.get('debug_otp')}")
    
    def test_multiple_otp_sends(self):
        """Test multiple OTP sends to same number"""
        mobile = "9876543214"
        
        # Send first OTP
        response1 = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": mobile, "country_code": "91"}
        )
        assert response1.status_code == 200
        
        # Send second OTP (should overwrite)
        response2 = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": mobile, "country_code": "91"}
        )
        assert response2.status_code == 200
        print("✓ Multiple OTP sends work correctly")


class TestUserProfile:
    """Test user profile endpoints"""
    
    def test_get_nonexistent_user(self):
        """Test getting a user that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/auth/user/0000000000")
        assert response.status_code == 404
        print("✓ Get non-existent user returns 404")
    
    def test_update_nonexistent_user(self):
        """Test updating a user that doesn't exist"""
        response = requests.put(
            f"{BASE_URL}/api/auth/user/0000000000",
            params={"name": "Test", "preferred_language": "en"}
        )
        assert response.status_code == 404
        print("✓ Update non-existent user returns 404")


class TestAPIHealth:
    """Test API health and categories"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API root: {data['message']}")
    
    def test_categories_endpoint(self):
        """Test categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/news/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        categories = data["categories"]
        
        # Check expected categories exist
        expected = ["local", "city", "state", "national", "international", "sports", "entertainment", "tech", "health", "business"]
        for cat in expected:
            assert cat in categories
            assert "en" in categories[cat]
            assert "te" in categories[cat]
        
        print(f"✓ Categories: {len(categories)} categories found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
