"""
Backend Refactoring Tests
Tests all API endpoints after server.py was split into modular route files:
- routes/auth.py - Auth routes
- routes/news.py - News CRUD routes  
- routes/upload.py - Upload routes
- routes/reporter.py - Reporter routes
- routes/analytics.py - Analytics routes
- routes/media.py - Live TV & Shorts routes
- routes/epaper.py - ePaper routes
- routes/scraper.py - Scraper routes
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthEndpoint:
    """Health check endpoint - routes/scraper.py"""
    
    def test_health_returns_ok(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("✓ GET /api/health returns ok")


class TestCategoriesEndpoint:
    """Categories endpoint - routes/news.py"""
    
    def test_categories_returns_10_categories(self):
        response = requests.get(f"{BASE_URL}/api/news/categories")
        assert response.status_code == 200
        data = response.json()
        categories = data.get("categories", {})
        assert len(categories) == 10
        expected = ["local", "city", "state", "national", "international", 
                    "sports", "entertainment", "tech", "health", "business"]
        for cat in expected:
            assert cat in categories
        print(f"✓ GET /api/news/categories returns {len(categories)} categories")


class TestNewsFeedEndpoint:
    """News feed endpoint - routes/news.py"""
    
    def test_news_feed_returns_articles(self):
        response = requests.get(f"{BASE_URL}/api/news/feed?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Verify article structure
        article = data[0]
        assert "id" in article
        assert "title" in article
        assert "summary" in article
        assert "category" in article
        print(f"✓ GET /api/news/feed returns {len(data)} articles")


class TestEpaperEndpoints:
    """ePaper endpoints - routes/epaper.py"""
    
    def test_epaper_editions_returns_list(self):
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        data = response.json()
        editions = data.get("editions", [])
        assert isinstance(editions, list)
        assert len(editions) > 0
        # Verify edition structure
        edition = editions[0]
        assert "date" in edition
        assert "article_count" in edition
        print(f"✓ GET /api/epaper/editions returns {len(editions)} editions")
    
    def test_epaper_date_returns_dense_pages(self):
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05")
        assert response.status_code == 200
        data = response.json()
        assert data.get("date") == "2026-03-05"
        assert data.get("lang") == "en"
        assert "edition_title" in data
        pages = data.get("pages", [])
        assert len(pages) > 0
        # Verify pages have articles
        total_articles = sum(len(p.get("articles", [])) for p in pages)
        assert total_articles > 0
        print(f"✓ GET /api/epaper/2026-03-05 returns {len(pages)} pages with {total_articles} articles")


class TestLiveTVEndpoint:
    """Live TV endpoint - routes/media.py"""
    
    def test_live_tv_returns_response(self):
        response = requests.get(f"{BASE_URL}/api/live-tv")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            channel = data[0]
            assert "id" in channel
            assert "name" in channel
            assert "youtube_url" in channel
        print(f"✓ GET /api/live-tv returns {len(data)} channels")


class TestShortsEndpoint:
    """Shorts endpoint - routes/media.py"""
    
    def test_shorts_returns_response(self):
        response = requests.get(f"{BASE_URL}/api/shorts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            short = data[0]
            assert "id" in short
            assert "youtube_url" in short
        print(f"✓ GET /api/shorts returns {len(data)} shorts")


class TestScraperEndpoint:
    """Scraper endpoint - routes/scraper.py"""
    
    def test_scraper_status_returns_response(self):
        response = requests.get(f"{BASE_URL}/api/scraper/status")
        assert response.status_code == 200
        data = response.json()
        assert "running" in data
        assert "last_run" in data
        assert "articles_added" in data
        print(f"✓ GET /api/scraper/status returns status (running={data.get('running')})")


class TestAnalyticsEndpoint:
    """Analytics endpoint - routes/analytics.py"""
    
    def test_analytics_overview_returns_data(self):
        response = requests.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        summary = data["summary"]
        assert "total_articles" in summary
        assert "total_users" in summary
        assert "views_today" in summary
        print(f"✓ GET /api/analytics/overview returns data (articles={summary.get('total_articles')})")


class TestAuthEndpoints:
    """Auth endpoints - routes/auth.py"""
    
    def test_send_otp_for_admin(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": "9876543210"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == "OTP sent successfully"
        # Admin number returns debug OTP
        assert data.get("debug_otp") == "123456"
        print("✓ POST /api/auth/send-otp works for admin number")
    
    def test_verify_otp_for_admin(self):
        # First send OTP
        requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": "9876543210"}
        )
        # Then verify
        response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": "9876543210", "otp": "123456"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == "OTP verified successfully"
        assert data.get("is_admin") == True
        assert "user" in data
        print("✓ POST /api/auth/verify-otp works with OTP 123456 for admin")


class TestNewsAdminEndpoints:
    """News admin endpoints - routes/news.py"""
    
    def test_news_admin_all_returns_articles(self):
        response = requests.get(f"{BASE_URL}/api/news/admin/all?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/news/admin/all returns {len(data)} articles")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
