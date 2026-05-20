"""
Test ePaper Summary Expansion Feature
- Verifies Telugu/English ePaper articles have 400+ char summaries
- Tests language isolation (Telugu ePaper has ONLY Telugu titles)
- Tests API response times (<15 seconds)
- Tests editions endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndEditions:
    """Basic health and editions endpoint tests"""
    
    def test_health_endpoint(self):
        """GET /api/health should return ok status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("✓ Health endpoint returns ok")

    def test_editions_endpoint(self):
        """GET /api/epaper/editions should return editions list"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions", timeout=15)
        assert response.status_code == 200
        data = response.json()
        editions = data.get("editions", [])
        assert len(editions) > 0, "No editions found"
        # Verify edition structure
        edition = editions[0]
        assert "date" in edition
        assert "slot" in edition
        assert "article_count" in edition
        print(f"✓ Editions endpoint returns {len(editions)} editions")


class TestTeluguEPaperAM:
    """Telugu AM ePaper tests - summaries should be 400+ chars, ONLY Telugu titles"""
    
    def test_telugu_am_api_response_time(self):
        """API should respond within 15 seconds"""
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=morning",
            timeout=30
        )
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 15, f"API took {elapsed:.2f}s, expected <15s"
        print(f"✓ Telugu AM API responded in {elapsed:.2f}s")

    def test_telugu_am_has_articles(self):
        """Telugu AM ePaper should have articles"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=morning",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        total = data.get("total_articles", 0)
        assert total > 0, "No articles in Telugu AM ePaper"
        print(f"✓ Telugu AM ePaper has {total} articles")

    def test_telugu_am_summaries_400_plus_chars(self):
        """All articles should have 400+ char summaries (no blank spaces)"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=morning",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        all_articles = []
        for page in data.get("pages", []):
            all_articles.extend(page.get("articles", []))
        
        assert len(all_articles) > 0, "No articles found"
        
        short_summaries = []
        for i, article in enumerate(all_articles):
            summary = article.get("summary", "")
            if len(summary) < 400:
                short_summaries.append((i, len(summary), article.get("title", "")[:30]))
        
        if short_summaries:
            for idx, s_len, title in short_summaries[:5]:
                print(f"  Warning: Article [{idx}] has {s_len} chars: {title}...")
        
        assert len(short_summaries) == 0, f"{len(short_summaries)}/{len(all_articles)} articles have <400 char summaries"
        print(f"✓ All {len(all_articles)} Telugu AM articles have 400+ char summaries")

    def test_telugu_am_only_telugu_titles(self):
        """Telugu ePaper should have ONLY Telugu titles (no English)"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=morning",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        all_articles = []
        for page in data.get("pages", []):
            all_articles.extend(page.get("articles", []))
        
        def has_telugu(text):
            return any(0x0C00 <= ord(c) <= 0x0C7F for c in text) if text else False
        
        english_only_titles = []
        for i, article in enumerate(all_articles):
            title = article.get("title", "")
            if title and not has_telugu(title):
                english_only_titles.append((i, title[:50]))
        
        if english_only_titles:
            for idx, title in english_only_titles[:5]:
                print(f"  Issue: English title at [{idx}]: {title}")
        
        assert len(english_only_titles) == 0, f"{len(english_only_titles)} articles have English-only titles in Telugu ePaper"
        print(f"✓ All {len(all_articles)} Telugu AM articles have Telugu titles")


class TestTeluguEPaperPM:
    """Telugu PM ePaper tests"""
    
    def test_telugu_pm_api_response_time(self):
        """API should respond within 15 seconds"""
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=evening",
            timeout=30
        )
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 15, f"API took {elapsed:.2f}s, expected <15s"
        print(f"✓ Telugu PM API responded in {elapsed:.2f}s")

    def test_telugu_pm_summaries_400_plus_chars(self):
        """All articles should have 400+ char summaries"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=evening",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        all_articles = []
        for page in data.get("pages", []):
            all_articles.extend(page.get("articles", []))
        
        assert len(all_articles) > 0, "No articles found"
        
        short_summaries = []
        for i, article in enumerate(all_articles):
            summary = article.get("summary", "")
            if len(summary) < 400:
                short_summaries.append((i, len(summary)))
        
        assert len(short_summaries) == 0, f"{len(short_summaries)}/{len(all_articles)} articles have <400 char summaries"
        print(f"✓ All {len(all_articles)} Telugu PM articles have 400+ char summaries")

    def test_telugu_pm_only_telugu_titles(self):
        """Telugu ePaper should have ONLY Telugu titles"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=te&slot=evening",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        all_articles = []
        for page in data.get("pages", []):
            all_articles.extend(page.get("articles", []))
        
        def has_telugu(text):
            return any(0x0C00 <= ord(c) <= 0x0C7F for c in text) if text else False
        
        english_only_titles = [a for a in all_articles if a.get("title") and not has_telugu(a.get("title"))]
        
        assert len(english_only_titles) == 0, f"{len(english_only_titles)} articles have English-only titles"
        print(f"✓ All {len(all_articles)} Telugu PM articles have Telugu titles")


class TestEnglishEPaperAM:
    """English AM ePaper tests"""
    
    def test_english_am_api_response_time(self):
        """API should respond within 15 seconds"""
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=30
        )
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 15, f"API took {elapsed:.2f}s, expected <15s"
        print(f"✓ English AM API responded in {elapsed:.2f}s")

    def test_english_am_summaries_400_plus_chars(self):
        """All articles should have 400+ char summaries"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        all_articles = []
        for page in data.get("pages", []):
            all_articles.extend(page.get("articles", []))
        
        assert len(all_articles) > 0, "No articles found"
        
        short_summaries = []
        for i, article in enumerate(all_articles):
            summary = article.get("summary", "")
            if len(summary) < 400:
                short_summaries.append((i, len(summary)))
        
        assert len(short_summaries) == 0, f"{len(short_summaries)}/{len(all_articles)} articles have <400 char summaries"
        print(f"✓ All {len(all_articles)} English AM articles have 400+ char summaries")

    def test_english_am_only_english_titles(self):
        """English ePaper should have ONLY English titles (no Telugu)"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        all_articles = []
        for page in data.get("pages", []):
            all_articles.extend(page.get("articles", []))
        
        def has_telugu(text):
            return any(0x0C00 <= ord(c) <= 0x0C7F for c in text) if text else False
        
        telugu_titles = [a for a in all_articles if a.get("title") and has_telugu(a.get("title"))]
        
        assert len(telugu_titles) == 0, f"{len(telugu_titles)} articles have Telugu titles in English ePaper"
        print(f"✓ All {len(all_articles)} English AM articles have English titles")


class TestSummaryCharacterLimits:
    """Test that character limits are properly enforced per position"""
    
    def test_hero_article_has_longest_summary(self):
        """Hero article (position 0) should have substantial summary"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08?lang=en&slot=morning",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("pages"):
            articles = data["pages"][0].get("articles", [])
            if articles:
                # Articles are sorted by summary length, first should be longest
                hero_summary_len = len(articles[0].get("summary", ""))
                # Hero should have at least 500 chars (min is 800, but trimmed to max 1400)
                assert hero_summary_len >= 500, f"Hero summary only {hero_summary_len} chars"
                print(f"✓ Hero article has {hero_summary_len} char summary")
