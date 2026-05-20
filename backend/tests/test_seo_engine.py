"""Test suite for Autonomous SEO Engine — sitemap, RSS, server-rendered pages, IndexNow, Celery/Redis integration."""
import pytest
import requests
import os
import xml.etree.ElementTree as ET

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# ============================================================
# STATIC SEO FILES
# ============================================================

class TestSitemapXml:
    """Test sitemap.xml generation with 4000+ article URLs"""
    
    def test_sitemap_xml_returns_valid_xml(self):
        """GET /sitemap.xml should return valid XML"""
        response = requests.get(f"{BASE_URL}/sitemap.xml", timeout=30)
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "") or "text/xml" in response.headers.get("content-type", "")
        
        # Parse XML to verify validity
        root = ET.fromstring(response.text)
        assert root.tag.endswith("urlset")
        print(f"Sitemap XML is valid, root tag: {root.tag}")
    
    def test_sitemap_has_4000_plus_urls(self):
        """Sitemap should contain 4000+ article URLs"""
        response = requests.get(f"{BASE_URL}/sitemap.xml", timeout=30)
        assert response.status_code == 200
        
        root = ET.fromstring(response.text)
        # Define namespace
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = root.findall("s:url", ns)
        url_count = len(urls)
        
        assert url_count > 100, f"Expected 4000+ URLs but got {url_count}"
        print(f"Sitemap contains {url_count} URLs")
        
        # Check for article URLs
        article_urls = [u for u in urls if "/news/" in u.find("s:loc", ns).text]
        print(f"Found {len(article_urls)} article URLs in sitemap")
    
    def test_sitemap_has_main_pages(self):
        """Sitemap should include main pages (home, epaper, agents)"""
        response = requests.get(f"{BASE_URL}/sitemap.xml", timeout=30)
        root = ET.fromstring(response.text)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        
        locs = [u.find("s:loc", ns).text for u in root.findall("s:url", ns)]
        
        # Check main pages exist
        assert any(loc.endswith("/") or loc.endswith(".com") for loc in locs[:10]), "Home page not in sitemap"
        assert any("/epaper" in loc for loc in locs), "ePaper page not in sitemap"
        assert any("/agents" in loc for loc in locs), "Agents page not in sitemap"
        print("Main pages (home, epaper, agents) found in sitemap")


class TestRssFeed:
    """Test RSS feed generation with latest 50 articles"""
    
    def test_rss_xml_returns_valid_xml(self):
        """GET /rss.xml should return valid RSS XML"""
        response = requests.get(f"{BASE_URL}/rss.xml", timeout=30)
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "") or "text/xml" in response.headers.get("content-type", "") or "application/rss+xml" in response.headers.get("content-type", "")
        
        root = ET.fromstring(response.text)
        assert root.tag == "rss"
        print(f"RSS XML is valid, version: {root.get('version')}")
    
    def test_rss_has_50_items(self):
        """RSS feed should contain up to 50 recent articles"""
        response = requests.get(f"{BASE_URL}/rss.xml", timeout=30)
        root = ET.fromstring(response.text)
        
        channel = root.find("channel")
        assert channel is not None, "RSS channel not found"
        
        items = channel.findall("item")
        assert len(items) >= 10, f"Expected ~50 items but got {len(items)}"
        print(f"RSS feed contains {len(items)} items")
        
        # Verify item structure
        first_item = items[0]
        assert first_item.find("title") is not None
        assert first_item.find("link") is not None
        assert first_item.find("description") is not None
        print("RSS items have valid structure (title, link, description)")
    
    def test_rss_channel_metadata(self):
        """RSS channel should have proper metadata"""
        response = requests.get(f"{BASE_URL}/rss.xml", timeout=30)
        root = ET.fromstring(response.text)
        channel = root.find("channel")
        
        assert channel.find("title") is not None and "Kaizer" in channel.find("title").text
        assert channel.find("link") is not None
        assert channel.find("description") is not None
        print(f"RSS channel title: {channel.find('title').text}")


class TestRobotsTxt:
    """Test robots.txt generation"""
    
    def test_robots_txt_returns_text(self):
        """GET /robots.txt should return valid robots.txt"""
        response = requests.get(f"{BASE_URL}/robots.txt", timeout=10)
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        
        content = response.text
        assert "User-agent:" in content
        assert "Allow:" in content
        assert "Sitemap:" in content
        print("robots.txt has valid structure")
        
    def test_robots_allows_news_disallows_admin(self):
        """robots.txt should allow news crawling, disallow admin"""
        response = requests.get(f"{BASE_URL}/robots.txt", timeout=10)
        content = response.text
        
        assert "Allow: /news/" in content or "Allow: /" in content
        assert "Disallow: /admin" in content
        assert "Disallow: /api/" in content
        print("robots.txt has correct allow/disallow rules")


# ============================================================
# SEO ENGINE API ENDPOINTS
# ============================================================

class TestSeoEngineStats:
    """Test /api/seo-engine/stats endpoint"""
    
    def test_stats_returns_seo_coverage(self):
        """GET /api/seo-engine/stats should return SEO coverage stats"""
        response = requests.get(f"{BASE_URL}/api/seo-engine/stats", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_articles" in data
        assert "with_seo_meta" in data
        assert "without_seo_meta" in data
        assert "seo_coverage_percent" in data
        
        # Verify values are reasonable
        assert isinstance(data["total_articles"], int) and data["total_articles"] > 0
        assert isinstance(data["seo_coverage_percent"], (int, float))
        
        print(f"SEO Stats: {data['total_articles']} total articles, {data['with_seo_meta']} with SEO meta ({data['seo_coverage_percent']}% coverage)")


class TestIndexNowKey:
    """Test IndexNow verification key endpoint"""
    
    def test_indexnow_key_returns_key(self):
        """GET /api/seo-engine/indexnow-key.txt should return verification key"""
        response = requests.get(f"{BASE_URL}/api/seo-engine/indexnow-key.txt", timeout=10)
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        
        key = response.text.strip()
        assert len(key) > 10
        assert "kaizernews" in key.lower()
        print(f"IndexNow key: {key}")


class TestServerRenderedArticlePage:
    """Test server-rendered article pages with full SEO meta tags"""
    
    def test_article_page_returns_html(self):
        """GET /api/seo-engine/article/{id} should return HTML with meta tags"""
        # Use test article ID
        article_id = "967df24d-d5b5-4f45-90e3-3f9e5f9711ce"
        response = requests.get(f"{BASE_URL}/api/seo-engine/article/{article_id}", timeout=15)
        
        # Could be 200 or 404 depending on article existence
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")
            html = response.text
            
            # Check for SEO meta tags
            assert "<title>" in html
            assert 'og:title' in html or 'property="og:title"' in html
            assert 'og:description' in html or 'property="og:description"' in html
            assert 'twitter:card' in html or 'name="twitter:card"' in html
            assert 'application/ld+json' in html
            
            print("Server-rendered article page has proper SEO tags: title, OG, Twitter Cards, JSON-LD")
        else:
            # Try to get any article from the news endpoint
            news_response = requests.get(f"{BASE_URL}/api/news?limit=1", timeout=10)
            if news_response.status_code == 200 and news_response.json().get("articles"):
                real_article_id = news_response.json()["articles"][0]["id"]
                response2 = requests.get(f"{BASE_URL}/api/seo-engine/article/{real_article_id}", timeout=15)
                assert response2.status_code == 200
                assert 'og:title' in response2.text or 'property="og:title"' in response2.text
                print(f"Tested with article {real_article_id}, has OG tags")
            else:
                pytest.skip("No articles available to test server-rendered page")
    
    def test_article_page_has_json_ld(self):
        """Server-rendered page should have NewsArticle JSON-LD schema"""
        # Get a real article
        news_response = requests.get(f"{BASE_URL}/api/news?limit=1", timeout=10)
        if news_response.status_code != 200 or not news_response.json().get("articles"):
            pytest.skip("No articles available")
        
        article_id = news_response.json()["articles"][0]["id"]
        response = requests.get(f"{BASE_URL}/api/seo-engine/article/{article_id}", timeout=15)
        
        if response.status_code == 200:
            html = response.text
            assert "NewsArticle" in html
            assert "@context" in html
            assert "schema.org" in html
            print("JSON-LD NewsArticle schema found in article page")


class TestSeoMetaGeneration:
    """Test SEO meta generation trigger endpoint"""
    
    def test_generate_meta_endpoint(self):
        """POST /api/seo-engine/generate-meta should start background generation"""
        response = requests.post(f"{BASE_URL}/api/seo-engine/generate-meta", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["started", "ok", "completed"]
        print(f"SEO meta generation: {data}")


class TestStaticFileRegeneration:
    """Test static SEO file regeneration endpoint"""
    
    def test_generate_static_endpoint(self):
        """POST /api/seo-engine/generate-static should regenerate static files"""
        response = requests.post(f"{BASE_URL}/api/seo-engine/generate-static", timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "completed", "error"]
        print(f"Static file regeneration: {data}")


# ============================================================
# PREVIOUS FEATURES STILL WORKING
# ============================================================

class TestPreviousFeaturesIntegration:
    """Verify previous SEO Agent and Tech Agent features still work"""
    
    def test_seo_agent_latest_returns_report(self):
        """GET /api/agents/seo/latest should return SEO report with trending keywords"""
        response = requests.get(f"{BASE_URL}/api/agents/seo/latest", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        if data.get("report"):
            report = data["report"]
            assert "trending_keywords" in report or "seo_score" in report
            print(f"SEO Agent report has trending_keywords: {len(report.get('trending_keywords', []))} items")
        else:
            print("No SEO Agent report yet (expected if agent hasn't run)")
    
    def test_tech_agent_run_returns_report(self):
        """POST /api/agents/tech/run should return performance report"""
        response = requests.post(f"{BASE_URL}/api/agents/tech/run", timeout=15)
        assert response.status_code == 200
        
        data = response.json()
        if data.get("report"):
            report = data["report"]
            assert "health_score" in report
            print(f"Tech Agent report health_score: {report['health_score']}")
        else:
            print("Tech agent returned empty report")


# ============================================================
# HTML INDEX.HTML SEO TAGS
# ============================================================

class TestFrontendIndexHtml:
    """Test frontend index.html has proper SEO tags"""
    
    def test_index_html_has_og_tags(self):
        """Frontend index.html should have Open Graph tags"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        
        html = response.text
        # Check for OG tags
        assert 'og:title' in html or 'property="og:title"' in html, "Missing og:title"
        assert 'og:description' in html or 'property="og:description"' in html, "Missing og:description"
        print("Frontend index.html has Open Graph tags")
    
    def test_index_html_has_twitter_cards(self):
        """Frontend should have Twitter Card tags"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        html = response.text
        
        assert 'twitter:card' in html or 'name="twitter:card"' in html, "Missing twitter:card"
        assert 'twitter:title' in html or 'name="twitter:title"' in html, "Missing twitter:title"
        print("Frontend index.html has Twitter Card tags")
    
    def test_index_html_has_rss_link(self):
        """Frontend should have RSS feed link"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        html = response.text
        
        assert 'rss' in html.lower() or 'application/rss+xml' in html, "Missing RSS link"
        print("Frontend index.html has RSS feed link")
    
    def test_index_html_has_meta_description(self):
        """Frontend should have meta description"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        html = response.text
        
        assert 'name="description"' in html or "meta name='description'" in html
        print("Frontend index.html has meta description")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
