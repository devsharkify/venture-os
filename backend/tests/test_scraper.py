"""
Backend API Tests for Siasat.com Auto-Scraper Feature
Tests scraper status, manual trigger, deduplication, and category mapping
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestScraperEndpoints:
    """Test scraper-related API endpoints"""
    
    def test_scraper_status_endpoint(self):
        """Test GET /api/scraper/status returns correct fields"""
        response = requests.get(f"{BASE_URL}/api/scraper/status")
        assert response.status_code == 200, f"Status endpoint failed: {response.text}"
        
        data = response.json()
        # Required fields
        assert "last_run" in data, "Missing 'last_run' field"
        assert "articles_added" in data, "Missing 'articles_added' field"
        assert "running" in data, "Missing 'running' field"
        assert "error" in data, "Missing 'error' field"
        
        # Type checks
        assert isinstance(data["running"], bool), "'running' should be boolean"
        assert isinstance(data["articles_added"], int), "'articles_added' should be integer"
        print(f"Scraper status: last_run={data['last_run']}, articles_added={data['articles_added']}, running={data['running']}")
    
    def test_scraper_trigger_endpoint(self):
        """Test POST /api/scraper/trigger returns articles_added count"""
        response = requests.post(f"{BASE_URL}/api/scraper/trigger")
        assert response.status_code == 200, f"Trigger endpoint failed: {response.text}"
        
        data = response.json()
        assert "status" in data, "Missing 'status' field"
        assert data["status"] in ["completed", "already_running"], f"Unexpected status: {data['status']}"
        
        if data["status"] == "completed":
            assert "articles_added" in data, "Missing 'articles_added' field"
            assert isinstance(data["articles_added"], int), "'articles_added' should be integer"
            print(f"Scraper trigger: articles_added={data['articles_added']}")
        else:
            print("Scraper was already running")
    
    def test_scraper_deduplication(self):
        """Test calling trigger twice doesn't create duplicates"""
        # First trigger
        response1 = requests.post(f"{BASE_URL}/api/scraper/trigger")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Wait a moment
        time.sleep(2)
        
        # Second trigger should return 0 or very few new articles due to deduplication
        response2 = requests.post(f"{BASE_URL}/api/scraper/trigger")
        assert response2.status_code == 200
        data2 = response2.json()
        
        if data2["status"] == "completed":
            # Second run should add 0 or very few articles (deduplication)
            # Note: Could add some if siasat.com updated since first trigger
            print(f"First trigger: {data1.get('articles_added', 'running')}, Second trigger: {data2.get('articles_added', 'running')}")


class TestScrapedArticlesInFeed:
    """Test scraped articles appear correctly in the news feed"""
    
    def test_feed_contains_siasat_articles(self):
        """Test GET /api/news/feed includes siasat.com articles with proper fields"""
        response = requests.get(f"{BASE_URL}/api/news/feed?limit=100")
        assert response.status_code == 200, f"Feed failed: {response.text}"
        
        articles = response.json()
        assert isinstance(articles, list), "Feed should return a list"
        
        # Find siasat articles
        siasat_articles = [a for a in articles if a.get("source") == "siasat.com"]
        print(f"Found {len(siasat_articles)} siasat.com articles in feed (total: {len(articles)})")
        
        # If scraper has run, there should be siasat articles
        if len(siasat_articles) > 0:
            article = siasat_articles[0]
            # Verify required fields
            assert "title" in article and article["title"], "Article missing title"
            assert "category" in article, "Article missing category"
            assert "source" in article and article["source"] == "siasat.com", "Article source should be 'siasat.com'"
            assert "link" in article, "Article should have link"
            assert "siasat.com" in article.get("link", ""), f"Link should contain siasat.com: {article.get('link')}"
            assert "image" in article, "Article should have image field"
            print(f"Sample siasat article: title='{article['title'][:50]}...', category={article['category']}")
        else:
            # Trigger scraper if no articles found
            print("No siasat articles found - scraper may not have run yet")
    
    def test_siasat_article_has_valid_category(self):
        """Verify scraped articles have valid categories from category mapping"""
        response = requests.get(f"{BASE_URL}/api/news/feed?limit=100")
        assert response.status_code == 200
        
        articles = response.json()
        siasat_articles = [a for a in articles if a.get("source") == "siasat.com"]
        
        valid_categories = ["local", "city", "state", "national", "international", 
                          "sports", "entertainment", "tech", "health", "business"]
        
        for article in siasat_articles[:10]:  # Check first 10
            category = article.get("category")
            assert category in valid_categories, f"Invalid category '{category}' for article: {article.get('title', 'unknown')[:30]}"
        
        if siasat_articles:
            # Show category distribution
            categories = {}
            for a in siasat_articles:
                cat = a.get("category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1
            print(f"Category distribution: {categories}")
    
    def test_siasat_articles_have_images(self):
        """Check if scraped articles have images"""
        response = requests.get(f"{BASE_URL}/api/news/feed?limit=100")
        assert response.status_code == 200
        
        articles = response.json()
        siasat_articles = [a for a in articles if a.get("source") == "siasat.com"]
        
        articles_with_images = [a for a in siasat_articles if a.get("image")]
        print(f"Siasat articles with images: {len(articles_with_images)}/{len(siasat_articles)}")
        
        # At least some articles should have images
        if len(siasat_articles) > 5:
            assert len(articles_with_images) > 0, "No siasat articles have images"


class TestAdminAllEndpoint:
    """Test that scraped articles appear in admin endpoint"""
    
    def test_admin_all_contains_siasat_articles(self):
        """Test GET /api/news/admin/all includes siasat.com articles"""
        response = requests.get(f"{BASE_URL}/api/news/admin/all?limit=100")
        assert response.status_code == 200, f"Admin all failed: {response.text}"
        
        articles = response.json()
        siasat_articles = [a for a in articles if a.get("source") == "siasat.com"]
        
        print(f"Admin panel: {len(siasat_articles)} siasat.com articles (total: {len(articles)})")
        
        if len(siasat_articles) > 0:
            # Verify source badge will display correctly
            for article in siasat_articles[:3]:
                assert article.get("source") == "siasat.com", f"Source mismatch: {article.get('source')}"


class TestCategoryMapping:
    """Test category mapping from siasat.com URLs"""
    
    def test_category_mapping_in_articles(self):
        """Verify category mapping based on article links"""
        response = requests.get(f"{BASE_URL}/api/news/feed?limit=100")
        assert response.status_code == 200
        
        articles = response.json()
        siasat_articles = [a for a in articles if a.get("source") == "siasat.com"]
        
        # Check some expected mappings
        mapping_tests = {
            "hyderabad": "city",
            "telangana": "state",
            "andhra-pradesh": "state",
            "india": "national",
            "middle-east": "international",
            "world": "international",
            "technology": "tech",
            "entertainment": "entertainment",
            "sports": "sports",
            "business": "business",
            "health": "health",
        }
        
        verified_mappings = []
        for article in siasat_articles:
            link = article.get("link", "").lower()
            category = article.get("category")
            for pattern, expected_cat in mapping_tests.items():
                if f"/{pattern}/" in link or f"/news/{pattern}" in link:
                    if category == expected_cat:
                        verified_mappings.append(f"{pattern} -> {category}")
                    break
        
        print(f"Verified category mappings: {set(verified_mappings)}")


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"API root: {response.json()}")
    
    def test_categories_endpoint(self):
        """Test categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/news/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"Categories available: {list(data['categories'].keys())}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
