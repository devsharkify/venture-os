"""
ePaper API Tests
Tests for the Way2News style ePaper feature including:
- /api/epaper/editions - Available edition dates
- /api/epaper/{date} - Get ePaper content for a specific date
- Telangana political news prioritization
- Dense page layout with 20+ articles per page
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEpaperEditions:
    """Tests for /api/epaper/editions endpoint"""
    
    def test_editions_returns_list(self):
        """GET /api/epaper/editions returns list of available dates"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        
        data = response.json()
        assert "editions" in data
        assert isinstance(data["editions"], list)
        print(f"SUCCESS: Found {len(data['editions'])} editions")
    
    def test_editions_have_correct_structure(self):
        """Each edition has date and article_count fields"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["editions"]) > 0:
            edition = data["editions"][0]
            assert "date" in edition, "Edition missing 'date' field"
            assert "article_count" in edition, "Edition missing 'article_count' field"
            print(f"SUCCESS: First edition - date: {edition['date']}, articles: {edition['article_count']}")
    
    def test_editions_sorted_by_date_descending(self):
        """Editions should be sorted with most recent first"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        
        data = response.json()
        editions = data["editions"]
        if len(editions) > 1:
            # Check first date is more recent than second
            assert editions[0]["date"] >= editions[1]["date"], "Editions not sorted descending"
            print(f"SUCCESS: Editions sorted correctly - {editions[0]['date']} > {editions[1]['date']}")


class TestEpaperContent:
    """Tests for /api/epaper/{date} endpoint"""
    
    def test_get_epaper_by_date(self):
        """GET /api/epaper/{date} returns edition content"""
        # Use known test date with many articles
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05")
        assert response.status_code == 200
        
        data = response.json()
        assert "date" in data
        assert "pages" in data
        assert "total_articles" in data
        assert "edition_title" in data
        print(f"SUCCESS: Got edition for 2026-03-05 with {data['total_articles']} articles")
    
    def test_epaper_has_pages_structure(self):
        """Each page has key, title, and articles array"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05")
        assert response.status_code == 200
        
        data = response.json()
        pages = data.get("pages", [])
        assert len(pages) > 0, "No pages returned"
        
        for i, page in enumerate(pages):
            assert "key" in page, f"Page {i} missing 'key'"
            assert "title" in page, f"Page {i} missing 'title'"
            assert "articles" in page, f"Page {i} missing 'articles'"
            print(f"Page {i+1}: {page['title']} - {len(page['articles'])} articles")
    
    def test_epaper_articles_structure(self):
        """Articles have required fields: id, title, summary, category"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05")
        assert response.status_code == 200
        
        data = response.json()
        pages = data.get("pages", [])
        if pages and pages[0].get("articles"):
            article = pages[0]["articles"][0]
            assert "id" in article, "Article missing 'id'"
            assert "title" in article, "Article missing 'title'"
            assert "summary" in article, "Article missing 'summary'"
            assert "category" in article, "Article missing 'category'"
            print(f"SUCCESS: Article structure valid - {article['title'][:50]}...")
    
    def test_dense_pages_with_many_articles(self):
        """Pages should be dense with 20+ articles each (for dates with enough content)"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05")
        assert response.status_code == 200
        
        data = response.json()
        total = data.get("total_articles", 0)
        pages = data.get("pages", [])
        
        # 2026-03-05 has 86 articles, should have 4 dense pages
        assert total >= 80, f"Expected 80+ articles, got {total}"
        assert len(pages) >= 3, f"Expected 3+ pages for {total} articles, got {len(pages)}"
        
        # Check pages are dense (at least 15 articles each on average)
        avg_per_page = total / len(pages) if pages else 0
        assert avg_per_page >= 15, f"Pages not dense enough - avg {avg_per_page:.1f} articles/page"
        print(f"SUCCESS: Dense layout - {total} articles across {len(pages)} pages ({avg_per_page:.1f}/page)")
    
    def test_telangana_political_news_prioritized(self):
        """State/city (Telangana political) news should appear first on front page"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05")
        assert response.status_code == 200
        
        data = response.json()
        pages = data.get("pages", [])
        assert len(pages) > 0, "No pages returned"
        
        front_page = pages[0]
        articles = front_page.get("articles", [])
        
        # Check first few articles are state/city (Telangana political)
        political_cats = {"state", "city"}
        top_articles = articles[:5]
        political_count = sum(1 for a in top_articles if a.get("category") in political_cats)
        
        # At least 3 of top 5 should be state/city
        assert political_count >= 3, f"Expected 3+ political news in top 5, got {political_count}"
        print(f"SUCCESS: {political_count}/5 top articles are Telangana political news")
        
        # Print categories of top articles
        for i, a in enumerate(top_articles):
            print(f"  #{i+1}: {a.get('category')} - {a.get('title', '')[:40]}...")


class TestEpaperLanguage:
    """Tests for Telugu language support"""
    
    def test_english_language_default(self):
        """Default language is English"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("lang") == "en"
        assert "Evening Edition" in data.get("edition_title", "")
        print(f"SUCCESS: Default language is English - {data['edition_title']}")
    
    def test_telugu_language_param(self):
        """lang=te returns Telugu content"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?lang=te")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("lang") == "te"
        # Telugu edition title should contain Telugu text
        assert "సాయంత్రం ఎడిషన్" in data.get("edition_title", "")
        print(f"SUCCESS: Telugu language - {data['edition_title']}")
    
    def test_front_page_title_by_language(self):
        """Front page title changes with language"""
        # English
        response_en = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?lang=en")
        data_en = response_en.json()
        pages_en = data_en.get("pages", [])
        
        # Telugu
        response_te = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?lang=te")
        data_te = response_te.json()
        pages_te = data_te.get("pages", [])
        
        if pages_en and pages_te:
            assert pages_en[0]["title"] == "Front Page"
            assert pages_te[0]["title"] == "ముఖ్య పేజీ"
            print(f"SUCCESS: English front page: '{pages_en[0]['title']}', Telugu: '{pages_te[0]['title']}'")


class TestEpaperEdgeCases:
    """Edge case and error handling tests"""
    
    def test_old_date_returns_response(self):
        """Date with no articles returns valid response (may include featured articles)"""
        response = requests.get(f"{BASE_URL}/api/epaper/2020-01-01")
        assert response.status_code == 200
        
        data = response.json()
        # API returns valid structure even for dates with no articles
        # Featured articles may still be included
        assert "pages" in data
        assert "total_articles" in data
        print(f"SUCCESS: Old date returns valid response with {data.get('total_articles', 0)} articles")
    
    def test_invalid_language_rejected(self):
        """Invalid language param returns error"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-05?lang=invalid")
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("SUCCESS: Invalid language rejected with 422")
    
    def test_single_page_edition(self):
        """Date with few articles (24) returns 1 page"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-06")
        assert response.status_code == 200
        
        data = response.json()
        pages = data.get("pages", [])
        total = data.get("total_articles", 0)
        
        # 2026-03-06 has 24 articles = 1 page
        assert total >= 20, f"Expected 20+ articles, got {total}"
        assert len(pages) == 1, f"Expected 1 page for {total} articles, got {len(pages)}"
        print(f"SUCCESS: {total} articles = {len(pages)} page")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
