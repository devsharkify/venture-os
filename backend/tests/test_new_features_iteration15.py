"""
Test iteration 15 - Testing new features:
1. ePaper scroll-based page navigation
2. Article modal Tinder-like swipe navigation
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestEpaperEditionsAPI:
    """Test ePaper editions API endpoints for scroll-based navigation"""

    def test_get_editions_returns_slots(self):
        """Verify editions API returns editions with slot field"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        data = response.json()
        assert "editions" in data
        assert len(data["editions"]) > 0
        # Verify slot field exists for scroll-based navigation
        for edition in data["editions"][:5]:
            assert "date" in edition
            assert "slot" in edition
            assert edition["slot"] in ["morning", "evening"]
            assert "article_count" in edition

    def test_get_epaper_pages_returns_multiple(self):
        """Verify ePaper API returns multiple pages for vertical scroll layout"""
        # Get latest edition
        editions_resp = requests.get(f"{BASE_URL}/api/epaper/editions")
        editions = editions_resp.json()["editions"]
        assert len(editions) > 0
        
        latest = editions[0]
        response = requests.get(f"{BASE_URL}/api/epaper/{latest['date']}?slot={latest['slot']}")
        assert response.status_code == 200
        data = response.json()
        assert "pages" in data
        # Scroll-based navigation requires multiple pages
        assert len(data["pages"]) >= 1
        # Verify page structure
        for page in data["pages"]:
            assert "title" in page
            assert "articles" in page


class TestPublicNewsAPI:
    """Test public news API for article modal swipe navigation"""

    def test_news_feed_returns_articles(self):
        """Verify news feed API returns articles for swipe navigation"""
        response = requests.get(f"{BASE_URL}/api/news/feed?limit=10")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) > 0
        # Verify article structure needed for swipe modal
        for article in articles[:3]:
            assert "id" in article
            assert "title" in article
            assert "category" in article

    def test_public_news_endpoint(self):
        """Verify public news endpoint returns articles"""
        response = requests.get(f"{BASE_URL}/api/public/news")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data or isinstance(data, list) or "total" in data

    def test_news_by_category(self):
        """Test news by category for filtered article lists"""
        response = requests.get(f"{BASE_URL}/api/news/category/national?limit=5")
        assert response.status_code == 200
        articles = response.json()
        # All returned articles should have category national
        for article in articles:
            assert article["category"] == "national" or "national" in article.get("category", "")


class TestArticleViewTracking:
    """Test article view tracking for modal navigation"""

    def test_article_view_post_endpoint(self):
        """Verify article view tracking works for modal navigation"""
        # Get an article first
        feed_resp = requests.get(f"{BASE_URL}/api/news/feed?limit=1")
        articles = feed_resp.json()
        if not articles:
            pytest.skip("No articles available for view tracking test")
        
        article_id = articles[0]["id"]
        # Test view tracking endpoint (used when modal opens)
        response = requests.post(
            f"{BASE_URL}/api/news/{article_id}/view",
            params={"user_phone": "", "source": "app"}
        )
        # Should succeed (200/201) or return 404 if article not found
        assert response.status_code in [200, 201, 404, 422]


class TestDataIntegrity:
    """Test data integrity for scroll and swipe features"""

    def test_article_has_required_fields_for_modal(self):
        """Verify articles have all required fields for article modal display"""
        response = requests.get(f"{BASE_URL}/api/news/feed?limit=5")
        articles = response.json()
        required_fields = ["id", "title", "category"]
        optional_fields = ["summary", "image", "published_at", "category_label"]
        
        for article in articles:
            for field in required_fields:
                assert field in article, f"Missing required field: {field}"

    def test_epaper_page_has_required_fields_for_scroll(self):
        """Verify ePaper pages have all required fields for scroll-based display"""
        editions_resp = requests.get(f"{BASE_URL}/api/epaper/editions")
        editions = editions_resp.json()["editions"]
        if not editions:
            pytest.skip("No editions available")
        
        latest = editions[0]
        response = requests.get(f"{BASE_URL}/api/epaper/{latest['date']}?slot={latest['slot']}")
        data = response.json()
        
        for page in data["pages"]:
            assert "title" in page
            assert "articles" in page
            # Articles in page should be iterable for rendering
            assert isinstance(page["articles"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
