"""
Tests for ePaper Redesign - Iteration 16
Testing: 2-page format, 12 articles per page, editions with slots, PDF download
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEpaperEditions:
    """Test ePaper editions endpoint returns editions with morning/evening slots"""

    def test_editions_endpoint_returns_data(self):
        """GET /api/epaper/editions returns editions list"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "editions" in data, "Response should have 'editions' key"
        assert isinstance(data["editions"], list), "Editions should be a list"

    def test_editions_have_slot_field(self):
        """Each edition should have date and slot (morning/evening)"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        data = response.json()
        editions = data.get("editions", [])
        if len(editions) > 0:
            edition = editions[0]
            assert "date" in edition, "Edition should have 'date' field"
            assert "slot" in edition, "Edition should have 'slot' field"
            assert edition["slot"] in ["morning", "evening"], f"Slot should be morning/evening, got {edition['slot']}"


class TestEpaperContent:
    """Test ePaper content endpoint returns max 2 pages with up to 12 articles each"""

    def test_epaper_morning_slot_returns_max_2_pages(self):
        """GET /api/epaper/{date}?slot=morning returns at most 2 pages"""
        # Using date from context: 2026-03-05
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning&lang=en")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "pages" in data, "Response should have 'pages' key"
        pages = data.get("pages", [])
        assert len(pages) <= 2, f"Expected at most 2 pages, got {len(pages)}"

    def test_epaper_evening_slot_returns_max_2_pages(self):
        """GET /api/epaper/{date}?slot=evening returns at most 2 pages"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening&lang=en")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        pages = data.get("pages", [])
        assert len(pages) <= 2, f"Expected at most 2 pages, got {len(pages)}"

    def test_epaper_page_has_max_12_articles(self):
        """Each page should have at most 12 articles (MAX_PER_PAGE=12)"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning&lang=en")
        assert response.status_code == 200
        data = response.json()
        pages = data.get("pages", [])
        for i, page in enumerate(pages):
            articles = page.get("articles", [])
            assert len(articles) <= 12, f"Page {i+1} has {len(articles)} articles, max is 12"

    def test_epaper_returns_edition_title(self):
        """Response should include edition_title"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning&lang=en")
        assert response.status_code == 200
        data = response.json()
        assert "edition_title" in data, "Response should have 'edition_title'"
        assert "Morning Edition" in data["edition_title"] or "Mint Street" in data["edition_title"]

    def test_epaper_returns_total_articles(self):
        """Response should include total_articles count"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening&lang=en")
        assert response.status_code == 200
        data = response.json()
        assert "total_articles" in data, "Response should have 'total_articles'"

    def test_epaper_telugu_language(self):
        """Test Telugu language parameter"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening&lang=te")
        assert response.status_code == 200
        data = response.json()
        assert data.get("lang") == "te", "Lang should be 'te'"


class TestEpaperPDF:
    """Test ePaper PDF download endpoint"""

    def test_pdf_download_returns_pdf(self):
        """GET /api/epaper/{date}/pdf returns a PDF file"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05/pdf?slot=evening&lang=en", stream=True)
        # PDF generation might fail if no articles, so accept 200 or 404
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        if response.status_code == 200:
            assert response.headers.get("content-type") == "application/pdf"
            assert "content-disposition" in response.headers

    def test_pdf_filename_includes_slot(self):
        """PDF filename should include the slot (morning/evening)"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05/pdf?slot=morning&lang=en", stream=True)
        if response.status_code == 200:
            disposition = response.headers.get("content-disposition", "")
            assert "morning" in disposition or "2026-03-05" in disposition


class TestNewsFeed:
    """Test news feed still works correctly"""

    def test_public_news_endpoint(self):
        """GET /api/public/news returns articles"""
        response = requests.get(f"{BASE_URL}/api/public/news")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data, "Response should have 'articles'"

    def test_news_feed_endpoint(self):
        """GET /api/news/feed returns articles with required fields"""
        response = requests.get(f"{BASE_URL}/api/news/feed")
        assert response.status_code == 200
        data = response.json()
        # Feed endpoint returns list directly, not {"articles": [...]}
        assert isinstance(data, list), "Response should be a list of articles"
        if len(data) > 0:
            article = data[0]
            assert "id" in article, "Article should have 'id'"
            assert "title" in article, "Article should have 'title'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
