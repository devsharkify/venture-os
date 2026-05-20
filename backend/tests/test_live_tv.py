"""
Test Live TV API Endpoints:
- GET /api/live-tv - List live channels
- POST /api/live-tv - Add new channel
- DELETE /api/live-tv/{channel_id} - Delete channel
"""
import pytest
import requests
import uuid
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kaizer-newsbot.preview.emergentagent.com').rstrip('/')


class TestLiveTVAPI:
    """Test Live TV API endpoints"""

    def test_api_health(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API health check passed: {data['message']}")

    def test_get_live_channels(self):
        """GET /api/live-tv - Returns list of live TV channels"""
        response = requests.get(f"{BASE_URL}/api/live-tv")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/live-tv returned {len(data)} channels")
        
        # Validate channel structure if any exist
        if len(data) > 0:
            channel = data[0]
            assert "id" in channel
            assert "name" in channel
            assert "youtube_url" in channel
            assert "youtube_id" in channel
            assert "is_active" in channel
            print(f"✓ First channel: {channel['name']} (ID: {channel['youtube_id']})")

    def test_add_live_channel(self):
        """POST /api/live-tv - Add new live channel with YouTube ID extraction"""
        test_name = f"TEST_LiveChannel_{uuid.uuid4().hex[:8]}"
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        expected_yt_id = "dQw4w9WgXcQ"
        
        response = requests.post(f"{BASE_URL}/api/live-tv", json={
            "name": test_name,
            "youtube_url": test_url
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "added"
        assert "channel" in data
        
        channel = data["channel"]
        assert channel["name"] == test_name
        assert channel["youtube_url"] == test_url
        assert channel["youtube_id"] == expected_yt_id
        print(f"✓ POST /api/live-tv - Added channel '{test_name}', extracted youtube_id={expected_yt_id}")
        
        # Cleanup
        channel_id = channel["id"]
        cleanup_response = requests.delete(f"{BASE_URL}/api/live-tv/{channel_id}")
        assert cleanup_response.status_code == 200
        print(f"✓ Cleanup: Deleted test channel {channel_id}")

    def test_youtube_id_extraction_from_different_formats(self):
        """Test YouTube ID extraction from various URL formats"""
        # YouTube IDs are always 11 characters
        test_cases = [
            ("https://www.youtube.com/watch?v=abcdefghijk", "abcdefghijk"),
            ("https://youtu.be/123456789xy", "123456789xy"),
            ("https://www.youtube.com/embed/xyzabc12345", "xyzabc12345"),
            ("https://www.youtube.com/live/LIVE123abc1", "LIVE123abc1"),
        ]
        
        for test_url, expected_id in test_cases:
            test_name = f"TEST_YTExtract_{uuid.uuid4().hex[:6]}"
            response = requests.post(f"{BASE_URL}/api/live-tv", json={
                "name": test_name,
                "youtube_url": test_url
            })
            
            assert response.status_code == 200
            channel = response.json()["channel"]
            assert channel["youtube_id"] == expected_id, f"Expected {expected_id}, got {channel['youtube_id']}"
            print(f"✓ YouTube ID extracted correctly from {test_url[:40]}... -> {expected_id}")
            
            # Cleanup
            requests.delete(f"{BASE_URL}/api/live-tv/{channel['id']}")

    def test_delete_live_channel(self):
        """DELETE /api/live-tv/{channel_id} - Delete a live channel"""
        # First create a channel
        test_name = f"TEST_DeleteChannel_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/live-tv", json={
            "name": test_name,
            "youtube_url": "https://youtube.com/watch?v=test12345ab"
        })
        assert create_response.status_code == 200
        channel_id = create_response.json()["channel"]["id"]
        print(f"✓ Created test channel with id {channel_id}")
        
        # Delete the channel
        delete_response = requests.delete(f"{BASE_URL}/api/live-tv/{channel_id}")
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["status"] == "deleted"
        print(f"✓ DELETE /api/live-tv/{channel_id} - Channel deleted successfully")
        
        # Verify it's gone - try to get all and ensure this ID is not present
        list_response = requests.get(f"{BASE_URL}/api/live-tv")
        channels = list_response.json()
        channel_ids = [c["id"] for c in channels]
        assert channel_id not in channel_ids
        print(f"✓ Verified channel {channel_id} no longer exists in list")

    def test_delete_nonexistent_channel(self):
        """DELETE /api/live-tv/{channel_id} - Returns 404 for nonexistent channel"""
        fake_id = f"fake-{uuid.uuid4()}"
        response = requests.delete(f"{BASE_URL}/api/live-tv/{fake_id}")
        assert response.status_code == 404
        print(f"✓ DELETE /api/live-tv/{fake_id} returned 404 as expected")

    def test_add_channel_without_name_fails(self):
        """POST /api/live-tv - Missing name should fail validation"""
        response = requests.post(f"{BASE_URL}/api/live-tv", json={
            "youtube_url": "https://youtube.com/watch?v=test12345ab"
        })
        # FastAPI Pydantic validation should return 422
        assert response.status_code == 422
        print(f"✓ POST without name returned 422 validation error")

    def test_add_channel_without_url_fails(self):
        """POST /api/live-tv - Missing youtube_url should fail validation"""
        response = requests.post(f"{BASE_URL}/api/live-tv", json={
            "name": "Test Channel"
        })
        assert response.status_code == 422
        print(f"✓ POST without youtube_url returned 422 validation error")


class TestAdminAuthFlow:
    """Test Admin Authentication Flow"""

    def test_admin_otp_send(self):
        """Admin OTP send - phone 9876543210"""
        response = requests.post(f"{BASE_URL}/api/auth/send-otp", json={
            "mobile": "9876543210",
            "country_code": "91"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "otp_sent"
        print(f"✓ Admin OTP sent successfully")

    def test_admin_otp_verify(self):
        """Admin OTP verify - OTP 123456"""
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
        print(f"✓ Admin OTP verified, is_admin=True")


class TestGuestMode:
    """Test Guest Mode - News feed accessible without login"""

    def test_news_feed_accessible(self):
        """News feed accessible without auth"""
        response = requests.get(f"{BASE_URL}/api/news/feed")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Guest mode: News feed accessible with {len(data)} articles")

    def test_categories_accessible(self):
        """Categories accessible without auth"""
        response = requests.get(f"{BASE_URL}/api/news/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"✓ Guest mode: Categories accessible with {len(data['categories'])} categories")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
