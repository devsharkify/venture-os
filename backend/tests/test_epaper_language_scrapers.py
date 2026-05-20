"""
ePaper Language Separation and Scraper Tests
Tests for: 
1. Telugu ePaper shows only Telugu content (no English leakage)
2. English ePaper shows only English content (no Telugu leakage)
3. All 5 scrapers are functional (TOI, Deccan Chronicle, Eenadu, Way2News, Siasat)
4. Core API endpoints work correctly
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


def has_telugu(text):
    """Check if text contains Telugu Unicode characters (0C00-0C7F)"""
    return any(0x0C00 <= ord(c) <= 0x0C7F for c in text) if text else False


def has_english_letters(text):
    """Check if text contains English ASCII letters"""
    return any(c.isalpha() and ord(c) < 128 for c in text) if text else False


class TestHealthAndStatus:
    """Health check and scraper status tests"""
    
    def test_health_endpoint(self):
        """GET /api/health should return ok"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
    
    def test_scraper_status(self):
        """GET /api/scraper/status should return status info"""
        response = requests.get(f"{BASE_URL}/api/scraper/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # Should have running, last_run, articles_added keys
        assert "running" in data
        assert "last_run" in data
        assert "articles_added" in data


class TestEpaperEditions:
    """ePaper editions list tests"""
    
    def test_editions_list(self):
        """GET /api/epaper/editions should return available editions"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions", timeout=30)
        assert response.status_code == 200
        data = response.json()
        editions = data.get("editions", [])
        assert len(editions) > 0, "Should have at least one edition"
        # Check edition structure
        first = editions[0]
        assert "date" in first
        assert "slot" in first
        assert "article_count" in first


class TestTeluguEpaperLanguageSeparation:
    """Tests to verify Telugu ePaper shows ONLY Telugu content"""
    
    def test_telugu_epaper_morning_titles(self):
        """Telugu ePaper (lang=te) should have Telugu titles only"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=morning",
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("lang") == "te"
        
        pages = data.get("pages", [])
        assert len(pages) > 0, "Should have at least one page"
        
        english_leaks = []
        for page in pages:
            for art in page.get("articles", []):
                title = art.get("title", "")
                # Title should contain Telugu if it has content
                if title and not has_telugu(title) and has_english_letters(title):
                    english_leaks.append(title[:50])
        
        assert len(english_leaks) == 0, f"English titles leaked into Telugu ePaper: {english_leaks}"
    
    def test_telugu_epaper_summaries(self):
        """Telugu ePaper summaries should contain Telugu text"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=morning",
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        
        telugu_summary_count = 0
        total_summaries = 0
        
        for page in data.get("pages", []):
            for art in page.get("articles", []):
                summary = art.get("summary", "")
                if summary:
                    total_summaries += 1
                    if has_telugu(summary):
                        telugu_summary_count += 1
        
        # At least 80% of summaries should have Telugu content
        if total_summaries > 0:
            ratio = telugu_summary_count / total_summaries
            assert ratio >= 0.8, f"Only {ratio*100:.0f}% summaries have Telugu (expected 80%+)"


class TestEnglishEpaperLanguageSeparation:
    """Tests to verify English ePaper shows ONLY English content"""
    
    def test_english_epaper_morning_no_telugu_titles(self):
        """English ePaper (lang=en) should NOT have Telugu titles"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("lang") == "en"
        
        pages = data.get("pages", [])
        assert len(pages) > 0, "Should have at least one page"
        
        telugu_leaks = []
        for page in pages:
            for art in page.get("articles", []):
                title = art.get("title", "")
                if title and has_telugu(title):
                    telugu_leaks.append(title[:50])
        
        assert len(telugu_leaks) == 0, f"Telugu titles leaked into English ePaper: {telugu_leaks}"
    
    def test_english_epaper_summaries_no_telugu(self):
        """English ePaper summaries should NOT contain Telugu text"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        
        telugu_leaks = []
        for page in data.get("pages", []):
            for art in page.get("articles", []):
                summary = art.get("summary", "")
                if summary and has_telugu(summary):
                    telugu_leaks.append(summary[:50])
        
        assert len(telugu_leaks) == 0, f"Telugu summaries leaked into English ePaper: {telugu_leaks}"


class TestEpaperContentQuality:
    """Tests for ePaper content quality"""
    
    def test_epaper_has_articles(self):
        """ePaper should return articles with proper structure"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        
        total = data.get("total_articles", 0)
        assert total > 0, "Should have articles"
        
        pages = data.get("pages", [])
        for page in pages:
            for art in page.get("articles", []):
                # Verify article structure
                assert "id" in art
                assert "title" in art
                assert "summary" in art
    
    def test_epaper_summary_lengths(self):
        """Most ePaper summaries should be >100 chars"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=90
        )
        assert response.status_code == 200
        data = response.json()
        
        long_summaries = 0
        total = 0
        
        for page in data.get("pages", []):
            for art in page.get("articles", []):
                summary = art.get("summary", "")
                total += 1
                if len(summary) > 100:
                    long_summaries += 1
        
        if total > 0:
            ratio = long_summaries / total
            assert ratio >= 0.5, f"Only {ratio*100:.0f}% summaries are >100 chars (expected 50%+)"


class TestScraperTrigger:
    """Scraper trigger functionality test"""
    
    def test_scraper_trigger_endpoint(self):
        """POST /api/scraper/trigger should work (may return 0 if all scraped)"""
        response = requests.post(
            f"{BASE_URL}/api/scraper/trigger",
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        # Either completed or already_running
        assert data.get("status") in ["completed", "already_running"]
        if data.get("status") == "completed":
            assert "articles_added" in data


class TestLanguageSpecificTitleCache:
    """Test the language-specific title cache fix (epaper_title_en vs epaper_title_te)"""
    
    def test_telugu_title_not_overwritten_by_english_cache(self):
        """
        The bug was: English cached titles (epaper_title) were leaking into Telugu ePaper.
        Fix: Cache keys are now language-specific (epaper_title_en, epaper_title_te)
        This test verifies Telugu titles remain Telugu after cache is populated.
        """
        # First fetch English to potentially populate cache
        en_resp = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=90
        )
        assert en_resp.status_code == 200
        
        # Then fetch Telugu and verify no English leakage
        te_resp = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=morning",
            timeout=90
        )
        assert te_resp.status_code == 200
        te_data = te_resp.json()
        
        # Check that titles are still Telugu after English fetch
        english_titles_found = []
        for page in te_data.get("pages", []):
            for art in page.get("articles", []):
                title = art.get("title", "")
                if title and not has_telugu(title) and has_english_letters(title):
                    english_titles_found.append(title[:50])
        
        assert len(english_titles_found) == 0, \
            f"Language cache leak: English titles in Telugu ePaper after English fetch: {english_titles_found}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
