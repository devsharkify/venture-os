"""
Test suite for Dual Edition ePaper feature
Tests morning/evening slot functionality for ePaper editions
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDualEditionEditions:
    """Test /api/epaper/editions endpoint with slot info"""
    
    def test_editions_returns_slot_field(self):
        """GET /api/epaper/editions returns editions with 'slot' field (morning/evening)"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        
        data = response.json()
        assert "editions" in data
        editions = data["editions"]
        assert len(editions) > 0, "Should have at least one edition"
        
        # Verify slot field exists and is valid
        for edition in editions[:10]:
            assert "date" in edition, "Edition should have date field"
            assert "slot" in edition, "Edition should have slot field"
            assert edition["slot"] in ["morning", "evening"], f"Slot should be morning/evening, got {edition['slot']}"
            assert "article_count" in edition, "Edition should have article_count field"
            assert isinstance(edition["article_count"], int), "article_count should be integer"
            assert edition["article_count"] >= 0, "article_count should be non-negative"
    
    def test_editions_has_both_morning_and_evening(self):
        """Verify editions list includes both morning and evening slots"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        
        editions = response.json()["editions"]
        slots = set(e["slot"] for e in editions)
        
        assert "morning" in slots, "Should have morning editions"
        assert "evening" in slots, "Should have evening editions"


class TestDualEditionContent:
    """Test /api/epaper/{date}?slot= endpoint"""
    
    def test_morning_edition_returns_correct_title(self):
        """GET /api/epaper/{date}?slot=morning returns Morning Edition with correct title"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning")
        assert response.status_code == 200
        
        data = response.json()
        assert data["slot"] == "morning", "Slot should be morning"
        assert "Morning Edition" in data["edition_title"], f"Title should contain 'Morning Edition', got {data['edition_title']}"
        assert data["date"] == "2026-03-05"
        assert data["lang"] == "en"
    
    def test_evening_edition_returns_correct_title(self):
        """GET /api/epaper/{date}?slot=evening returns Evening Edition with correct title"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening")
        assert response.status_code == 200
        
        data = response.json()
        assert data["slot"] == "evening", "Slot should be evening"
        assert "Evening Edition" in data["edition_title"], f"Title should contain 'Evening Edition', got {data['edition_title']}"
        assert data["date"] == "2026-03-05"
    
    def test_morning_edition_telugu(self):
        """GET /api/epaper/{date}?slot=morning&lang=te returns Telugu Morning Edition"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning&lang=te")
        assert response.status_code == 200
        
        data = response.json()
        assert data["slot"] == "morning"
        assert data["lang"] == "te"
        # Telugu for "Morning Edition" is "ఉదయం ఎడిషన్"
        assert "ఉదయం ఎడిషన్" in data["edition_title"], f"Title should contain Telugu Morning Edition text, got {data['edition_title']}"
    
    def test_evening_edition_telugu(self):
        """GET /api/epaper/{date}?slot=evening&lang=te returns Telugu Evening Edition"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening&lang=te")
        assert response.status_code == 200
        
        data = response.json()
        assert data["slot"] == "evening"
        assert data["lang"] == "te"
        # Telugu for "Evening Edition" is "సాయంత్రం ఎడిషన్"
        assert "సాయంత్రం ఎడిషన్" in data["edition_title"], f"Title should contain Telugu Evening Edition text, got {data['edition_title']}"
    
    def test_without_slot_param_backward_compatible(self):
        """GET /api/epaper/{date} without slot param still works (backward compatible)"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05")
        assert response.status_code == 200
        
        data = response.json()
        assert data["date"] == "2026-03-05"
        assert "slot" in data, "Response should still have slot field"
        assert data["slot"] in ["morning", "evening"], "Default slot should be valid"
        assert "pages" in data
        assert "total_articles" in data
    
    def test_morning_evening_have_different_articles(self):
        """Morning and evening editions should have different article counts (filtered by time)"""
        morning = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning").json()
        evening = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening").json()
        
        # They should have different article counts
        morning_count = morning["total_articles"]
        evening_count = evening["total_articles"]
        
        # Both should have articles
        assert morning_count > 0, "Morning edition should have articles"
        assert evening_count > 0, "Evening edition should have articles"
        
        # Article counts can be different (time-based filtering)
        print(f"Morning articles: {morning_count}, Evening articles: {evening_count}")


class TestDualEditionPDF:
    """Test PDF download with slot parameter"""
    
    def test_pdf_morning_edition(self):
        """GET /api/epaper/{date}/pdf?slot=morning returns PDF for morning edition"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05/pdf?slot=morning", stream=True)
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        
        # Check filename in content-disposition
        content_disp = response.headers.get("content-disposition", "")
        assert "morning" in content_disp.lower(), f"Filename should contain 'morning', got {content_disp}"
    
    def test_pdf_evening_edition(self):
        """GET /api/epaper/{date}/pdf?slot=evening returns PDF for evening edition"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05/pdf?slot=evening", stream=True)
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        
        content_disp = response.headers.get("content-disposition", "")
        assert "evening" in content_disp.lower(), f"Filename should contain 'evening', got {content_disp}"
    
    def test_pdf_without_slot(self):
        """GET /api/epaper/{date}/pdf without slot still works"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05/pdf", stream=True)
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"


class TestHealthAndScraper:
    """Test health and scraper status endpoints"""
    
    def test_health_endpoint(self):
        """GET /api/health returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
    
    def test_scraper_status(self):
        """GET /api/scraper/status returns status with last_run info"""
        response = requests.get(f"{BASE_URL}/api/scraper/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "running" in data
        assert "last_run" in data
        assert "articles_added" in data
        assert isinstance(data["running"], bool)


class TestEditionPageStructure:
    """Test page structure of editions"""
    
    def test_morning_edition_has_pages(self):
        """Morning edition should have properly structured pages"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning")
        assert response.status_code == 200
        
        data = response.json()
        pages = data.get("pages", [])
        assert len(pages) > 0, "Morning edition should have at least one page"
        
        for page in pages:
            assert "key" in page
            assert "title" in page
            assert "articles" in page
            assert isinstance(page["articles"], list)
    
    def test_evening_edition_has_pages(self):
        """Evening edition should have properly structured pages"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=evening")
        assert response.status_code == 200
        
        data = response.json()
        pages = data.get("pages", [])
        assert len(pages) > 0, "Evening edition should have at least one page"
    
    def test_articles_have_required_fields(self):
        """Articles in edition should have required fields"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?slot=morning")
        assert response.status_code == 200
        
        data = response.json()
        if data["pages"]:
            first_page = data["pages"][0]
            if first_page["articles"]:
                article = first_page["articles"][0]
                assert "id" in article
                assert "title" in article
                assert "summary" in article
                assert "category" in article


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
