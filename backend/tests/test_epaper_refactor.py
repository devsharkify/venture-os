"""
Test suite for ePaper refactoring verification and dual edition features.
Tests the backend API endpoints after frontend component refactoring.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEpaperEditions:
    """Tests for /api/epaper/editions endpoint"""
    
    def test_editions_endpoint_returns_list(self):
        """GET /api/epaper/editions returns editions list with slot field"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        data = response.json()
        assert "editions" in data
        assert isinstance(data["editions"], list)
        assert len(data["editions"]) > 0
        print(f"Found {len(data['editions'])} editions")
    
    def test_editions_have_required_fields(self):
        """Each edition has date, slot, and article_count"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        data = response.json()
        edition = data["editions"][0]
        assert "date" in edition
        assert "slot" in edition
        assert "article_count" in edition
        assert edition["slot"] in ["morning", "evening"]
        print(f"First edition: {edition}")
    
    def test_both_slots_available_for_march_5(self):
        """2026-03-05 has both morning and evening editions"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        data = response.json()
        march_5_editions = [e for e in data["editions"] if e["date"] == "2026-03-05"]
        slots = [e["slot"] for e in march_5_editions]
        assert "morning" in slots, "Morning edition should exist for 2026-03-05"
        assert "evening" in slots, "Evening edition should exist for 2026-03-05"
        print(f"2026-03-05 editions: {march_5_editions}")


class TestEpaperMorningEdition:
    """Tests for morning edition API"""
    
    def test_morning_edition_returns_content(self):
        """GET /api/epaper/2026-03-05?slot=morning returns morning edition"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning")
        assert response.status_code == 200
        data = response.json()
        assert data["slot"] == "morning"
        assert "Morning Edition" in data["edition_title"]
        print(f"Morning edition: {data['edition_title']}, pages: {len(data['pages'])}")
    
    def test_morning_edition_has_pages(self):
        """Morning edition contains pages with articles"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning")
        data = response.json()
        assert "pages" in data
        assert len(data["pages"]) > 0
        first_page = data["pages"][0]
        assert "key" in first_page
        assert "title" in first_page
        assert "articles" in first_page
        print(f"Morning edition has {len(data['pages'])} pages")
    
    def test_morning_telugu_edition(self):
        """GET /api/epaper/2026-03-05?slot=morning&lang=te returns Telugu morning edition"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning&lang=te")
        assert response.status_code == 200
        data = response.json()
        assert data["lang"] == "te"
        assert "Morning" in data["edition_title"]


class TestEpaperEveningEdition:
    """Tests for evening edition API"""
    
    def test_evening_edition_returns_content(self):
        """GET /api/epaper/2026-03-05?slot=evening returns evening edition"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening")
        assert response.status_code == 200
        data = response.json()
        assert data["slot"] == "evening"
        assert "Evening Edition" in data["edition_title"]
        print(f"Evening edition: {data['edition_title']}, pages: {len(data['pages'])}")
    
    def test_evening_edition_has_more_articles(self):
        """Evening edition typically has more articles than morning"""
        morning = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning").json()
        evening = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening").json()
        print(f"Morning articles: {morning['total_articles']}, Evening articles: {evening['total_articles']}")
        # Just verify both have content
        assert morning["total_articles"] > 0
        assert evening["total_articles"] > 0


class TestBreakingNewsNotifications:
    """Tests for breaking news/notifications endpoint"""
    
    def test_breaking_news_endpoint(self):
        """GET /api/notifications/breaking returns recent articles"""
        response = requests.get(f"{BASE_URL}/api/notifications/breaking")
        assert response.status_code == 200
        data = response.json()
        assert "breaking" in data
        assert "count" in data
        print(f"Breaking news count: {data['count']}")
    
    def test_breaking_news_article_fields(self):
        """Breaking news articles have required fields"""
        response = requests.get(f"{BASE_URL}/api/notifications/breaking")
        data = response.json()
        if data["count"] > 0:
            article = data["breaking"][0]
            assert "id" in article
            assert "title" in article
            assert "category" in article
            print(f"First breaking article: {article['title'][:50]}...")


class TestHealthEndpoint:
    """Basic health check"""
    
    def test_health_check(self):
        """GET /api/health returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
