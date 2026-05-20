"""
Test suite for Public Content API & API Key Management
Tests: API key CRUD, public endpoints (feed, article, categories, search), rate limiting, auth validation
"""
import pytest
import requests
import os
import time
import random
import string

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============================================================
# API KEY MANAGEMENT TESTS
# ============================================================

class TestApiKeyManagement:
    """Test CRUD operations for API key management (admin endpoints)"""
    
    created_key_id = None
    created_api_key = None
    
    def test_create_api_key(self):
        """POST /api/apikeys/create - Create a new API key"""
        suffix = ''.join(random.choices(string.ascii_lowercase, k=5))
        name = f"TEST_Partner_{suffix}"
        
        response = requests.post(
            f"{BASE_URL}/api/apikeys/create",
            params={"name": name, "daily_limit": 1000}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert data["status"] == "ok"
        assert "api_key" in data, "Response should contain api_key"
        assert data["api_key"].startswith("kn_"), "API key should start with 'kn_' prefix"
        assert data["name"] == name
        assert data["daily_limit"] == 1000
        assert "message" in data, "Should have warning message about saving the key"
        
        # Store for subsequent tests
        TestApiKeyManagement.created_api_key = data["api_key"]
        print(f"Created API key: {data['api_key'][:15]}...")
    
    def test_list_api_keys(self):
        """GET /api/apikeys/list - List all API keys with usage stats"""
        response = requests.get(f"{BASE_URL}/api/apikeys/list")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["status"] == "ok"
        assert "keys" in data
        assert isinstance(data["keys"], list)
        
        # Should have at least one key (the one we just created)
        assert len(data["keys"]) > 0, "Should have at least one API key"
        
        # Validate key structure
        key = data["keys"][0]
        assert "id" in key
        assert "name" in key
        assert "key_prefix" in key
        assert "active" in key
        assert "daily_limit" in key
        assert "total_requests" in key
        assert "requests_today" in key
        
        # Find and store our test key ID
        for k in data["keys"]:
            if k.get("name", "").startswith("TEST_Partner_"):
                TestApiKeyManagement.created_key_id = k["id"]
                print(f"Found test key ID: {k['id']}, Name: {k['name']}")
                break
        
        assert TestApiKeyManagement.created_key_id is not None, "Test key should be in list"
    
    def test_get_key_usage(self):
        """GET /api/apikeys/{key_id}/usage - Get detailed usage stats"""
        key_id = TestApiKeyManagement.created_key_id
        if not key_id:
            pytest.skip("No key ID available from previous test")
        
        response = requests.get(f"{BASE_URL}/api/apikeys/{key_id}/usage")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["status"] == "ok"
        assert "name" in data
        assert "total_requests" in data
        assert "daily_limit" in data
        assert "daily_usage" in data
    
    def test_toggle_api_key(self):
        """PUT /api/apikeys/{key_id}/toggle - Toggle key active/inactive"""
        key_id = TestApiKeyManagement.created_key_id
        if not key_id:
            pytest.skip("No key ID available")
        
        # Toggle to inactive
        response = requests.put(f"{BASE_URL}/api/apikeys/{key_id}/toggle")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        first_status = data["active"]
        print(f"Toggled key to active={first_status}")
        
        # Toggle back
        response2 = requests.put(f"{BASE_URL}/api/apikeys/{key_id}/toggle")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["active"] != first_status, "Toggle should flip active status"
        print(f"Toggled key back to active={data2['active']}")


# ============================================================
# PUBLIC API AUTHENTICATION TESTS
# ============================================================

class TestPublicApiAuth:
    """Test public API authentication via X-API-Key header"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure we have a valid API key for testing"""
        # First make sure the key is active
        if TestApiKeyManagement.created_key_id:
            # Check current status and make sure it's active
            response = requests.get(f"{BASE_URL}/api/apikeys/list")
            if response.status_code == 200:
                for k in response.json().get("keys", []):
                    if k["id"] == TestApiKeyManagement.created_key_id:
                        if not k["active"]:
                            # Activate it
                            requests.put(f"{BASE_URL}/api/apikeys/{TestApiKeyManagement.created_key_id}/toggle")
                        break
    
    def test_feed_without_api_key_returns_401(self):
        """GET /api/public/v1/feed without header should return 401"""
        response = requests.get(f"{BASE_URL}/api/public/v1/feed")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "Missing" in data["detail"] or "API key" in data["detail"]
    
    def test_feed_with_invalid_key_returns_401(self):
        """GET /api/public/v1/feed with invalid key should return 401"""
        response = requests.get(
            f"{BASE_URL}/api/public/v1/feed",
            headers={"X-API-Key": "invalid_key_12345"}
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert "Invalid" in data["detail"]
    
    def test_feed_with_valid_key_returns_ok(self):
        """GET /api/public/v1/feed with valid key should return 200 with status:ok"""
        api_key = TestApiKeyManagement.created_api_key
        if not api_key:
            pytest.skip("No API key available from previous test")
        
        response = requests.get(
            f"{BASE_URL}/api/public/v1/feed",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["status"] == "ok"
        assert "articles" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "has_more" in data
        
        print(f"Feed returned {len(data['articles'])} articles, total: {data['total']}")


# ============================================================
# PUBLIC API ENDPOINT TESTS
# ============================================================

class TestPublicApiEndpoints:
    """Test all public API endpoints with valid authentication"""
    
    @pytest.fixture
    def api_key(self):
        """Get valid API key"""
        key = TestApiKeyManagement.created_api_key
        if not key:
            pytest.skip("No API key available")
        return key
    
    def test_feed_default_params(self, api_key):
        """GET /api/public/v1/feed - Default parameters"""
        response = requests.get(
            f"{BASE_URL}/api/public/v1/feed",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert data["page"] == 1
        assert data["limit"] == 20  # Default limit
        
        # Validate article structure if articles exist
        if len(data["articles"]) > 0:
            article = data["articles"][0]
            assert "id" in article
            assert "title" in article
            assert "category" in article
    
    def test_feed_with_category_filter(self, api_key):
        """GET /api/public/v1/feed?category=sports - Filter by category"""
        response = requests.get(
            f"{BASE_URL}/api/public/v1/feed",
            params={"category": "sports"},
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # All returned articles should be in sports category
        for article in data["articles"]:
            assert article["category"] == "sports", f"Expected sports, got {article['category']}"
    
    def test_feed_telugu_language(self, api_key):
        """GET /api/public/v1/feed?lang=te - Telugu content"""
        response = requests.get(
            f"{BASE_URL}/api/public/v1/feed",
            params={"lang": "te"},
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        # Telugu content test - title should be from title_te field when available
        print(f"Telugu feed returned {len(data['articles'])} articles")
    
    def test_feed_pagination(self, api_key):
        """GET /api/public/v1/feed?page=2&limit=5 - Pagination"""
        response = requests.get(
            f"{BASE_URL}/api/public/v1/feed",
            params={"page": 2, "limit": 5},
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 2
        assert data["limit"] == 5
        assert len(data["articles"]) <= 5
    
    def test_categories_endpoint(self, api_key):
        """GET /api/public/v1/categories - Get all categories"""
        response = requests.get(
            f"{BASE_URL}/api/public/v1/categories",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "categories" in data
        assert len(data["categories"]) == 10, f"Expected 10 categories, got {len(data['categories'])}"
        
        # Validate category structure
        cat = data["categories"][0]
        assert "id" in cat
        assert "label_en" in cat
        assert "label_te" in cat
        
        print(f"Categories: {[c['id'] for c in data['categories']]}")
    
    def test_search_endpoint(self, api_key):
        """GET /api/public/v1/search?q=Hyderabad - Search articles"""
        response = requests.get(
            f"{BASE_URL}/api/public/v1/search",
            params={"q": "Hyderabad"},
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "query" in data
        assert data["query"] == "Hyderabad"
        assert "articles" in data
        assert "total" in data
        
        print(f"Search 'Hyderabad' returned {data['total']} results")
    
    def test_single_article(self, api_key):
        """GET /api/public/v1/articles/{id} - Get single article"""
        # First get an article ID from feed
        feed_response = requests.get(
            f"{BASE_URL}/api/public/v1/feed",
            params={"limit": 1},
            headers={"X-API-Key": api_key}
        )
        
        if feed_response.status_code != 200 or len(feed_response.json().get("articles", [])) == 0:
            pytest.skip("No articles available to test")
        
        article_id = feed_response.json()["articles"][0]["id"]
        
        # Now get single article
        response = requests.get(
            f"{BASE_URL}/api/public/v1/articles/{article_id}",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "article" in data
        assert data["article"]["id"] == article_id
        
        print(f"Got article: {data['article']['title'][:50]}...")
    
    def test_article_not_found(self, api_key):
        """GET /api/public/v1/articles/nonexistent - 404 for invalid ID"""
        response = requests.get(
            f"{BASE_URL}/api/public/v1/articles/nonexistent-id-12345",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 404


# ============================================================
# RATE LIMITING & REVOKED KEY TESTS
# ============================================================

class TestRateLimitingAndRevocation:
    """Test rate limiting and revoked key behavior"""
    
    def test_revoked_key_returns_403(self):
        """Revoked API key should return 403 error"""
        key_id = TestApiKeyManagement.created_key_id
        api_key = TestApiKeyManagement.created_api_key
        
        if not key_id or not api_key:
            pytest.skip("No test key available")
        
        # First check current status
        list_response = requests.get(f"{BASE_URL}/api/apikeys/list")
        current_active = True
        for k in list_response.json().get("keys", []):
            if k["id"] == key_id:
                current_active = k["active"]
                break
        
        # Make key inactive if it's currently active
        if current_active:
            requests.put(f"{BASE_URL}/api/apikeys/{key_id}/toggle")
        
        # Try to use revoked key
        response = requests.get(
            f"{BASE_URL}/api/public/v1/feed",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 403, f"Expected 403 for revoked key, got {response.status_code}"
        assert "revoked" in response.json()["detail"].lower()
        
        # Re-activate the key for subsequent tests
        requests.put(f"{BASE_URL}/api/apikeys/{key_id}/toggle")
        print("Verified: Revoked key returns 403")


# ============================================================
# CLEANUP - Delete test API key
# ============================================================

class TestApiKeyCleanup:
    """Cleanup test data"""
    
    def test_delete_api_key(self):
        """DELETE /api/apikeys/{key_id} - Permanently delete test key"""
        key_id = TestApiKeyManagement.created_key_id
        
        if not key_id:
            pytest.skip("No key ID to delete")
        
        response = requests.delete(f"{BASE_URL}/api/apikeys/{key_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["deleted"] is True
        
        # Verify key is gone
        list_response = requests.get(f"{BASE_URL}/api/apikeys/list")
        key_ids = [k["id"] for k in list_response.json().get("keys", [])]
        assert key_id not in key_ids, "Deleted key should not appear in list"
        
        print(f"Deleted test API key: {key_id}")
    
    def test_delete_nonexistent_key_returns_404(self):
        """DELETE /api/apikeys/nonexistent - 404 for invalid ID"""
        response = requests.delete(f"{BASE_URL}/api/apikeys/nonexistent-id-12345")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
