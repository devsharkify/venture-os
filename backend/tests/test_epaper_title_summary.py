"""
Test ePaper title condensation and summary trimming
Tests that:
1. All article titles are <= 85 characters (AI condensed)
2. All summaries end with complete sentences (no ... or incomplete text)
3. Page navigation works (2 pages)
4. Morning/Evening edition toggle works
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestEpaperTitleCondensation:
    """Tests for AI-condensed titles under 85 chars"""
    
    def test_morning_edition_titles_under_85_chars(self):
        """All morning edition titles should be <= 85 characters"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=morning&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        assert 'pages' in data
        assert len(data['pages']) > 0
        
        title_issues = []
        total_titles = 0
        
        for page in data['pages']:
            for article in page.get('articles', []):
                total_titles += 1
                title = article.get('title', '')
                if len(title) > 85:
                    title_issues.append({
                        'id': article.get('id'),
                        'title': title,
                        'length': len(title)
                    })
        
        assert total_titles > 0, "Should have at least one article"
        assert len(title_issues) == 0, f"Found {len(title_issues)} titles over 85 chars: {title_issues}"
    
    def test_evening_edition_titles_under_85_chars(self):
        """All evening edition titles should be <= 85 characters"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=evening&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        title_issues = []
        
        for page in data.get('pages', []):
            for article in page.get('articles', []):
                title = article.get('title', '')
                if len(title) > 85:
                    title_issues.append({'title': title, 'length': len(title)})
        
        assert len(title_issues) == 0, f"Found {len(title_issues)} titles over 85 chars"


class TestEpaperSummaryCompleteness:
    """Tests for summaries with complete sentences (no ... truncation)"""
    
    def test_morning_summaries_end_with_complete_sentences(self):
        """Morning summaries should end with period/!/? not ..."""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=morning&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        summary_issues = []
        
        for page in data.get('pages', []):
            for article in page.get('articles', []):
                summary = article.get('summary', '').strip()
                if not summary:
                    continue
                    
                # Check for ellipsis
                if summary.endswith('...') or summary.endswith('…'):
                    summary_issues.append({
                        'id': article.get('id'),
                        'issue': 'ends with ellipsis',
                        'ending': summary[-40:]
                    })
                # Check for proper sentence ending
                elif not (summary.endswith('.') or summary.endswith('!') or summary.endswith('?')):
                    summary_issues.append({
                        'id': article.get('id'),
                        'issue': 'no sentence ending',
                        'ending': summary[-40:]
                    })
        
        assert len(summary_issues) == 0, f"Summary issues: {summary_issues}"
    
    def test_evening_summaries_end_with_complete_sentences(self):
        """Evening summaries should end with period/!/? not ..."""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=evening&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        summary_issues = []
        
        for page in data.get('pages', []):
            for article in page.get('articles', []):
                summary = article.get('summary', '').strip()
                if not summary:
                    continue
                    
                if summary.endswith('...') or summary.endswith('…'):
                    summary_issues.append({'issue': 'ellipsis', 'ending': summary[-40:]})
                elif not (summary.endswith('.') or summary.endswith('!') or summary.endswith('?')):
                    summary_issues.append({'issue': 'no sentence ending', 'ending': summary[-40:]})
        
        assert len(summary_issues) == 0, f"Summary issues: {summary_issues}"


class TestEpaperPageNavigation:
    """Tests for page navigation and editions"""
    
    def test_epaper_returns_two_pages(self):
        """ePaper should return exactly 2 pages when enough articles"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=morning&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        pages = data.get('pages', [])
        assert len(pages) == 2, f"Expected 2 pages, got {len(pages)}"
        
        # Verify page structure
        assert pages[0].get('key') == 'front'
        assert pages[0].get('title') == 'Front Page'
        assert pages[1].get('key') == 'latest'
        assert pages[1].get('title') == 'Latest News'
    
    def test_morning_edition_slot(self):
        """Morning edition should have correct slot info"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=morning&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('slot') == 'morning'
        assert 'Morning Edition' in data.get('edition_title', '')
    
    def test_evening_edition_slot(self):
        """Evening edition should have correct slot info"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=evening&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('slot') == 'evening'
        assert 'Evening Edition' in data.get('edition_title', '')
    
    def test_max_12_articles_per_page(self):
        """Each page should have max 12 articles"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=morning&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        for page in data.get('pages', []):
            articles = page.get('articles', [])
            assert len(articles) <= 12, f"Page {page.get('key')} has {len(articles)} articles, max is 12"


class TestEpaperEditions:
    """Tests for editions list endpoint"""
    
    def test_editions_list_returns_data(self):
        """Editions endpoint should return list of available editions"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        
        data = response.json()
        editions = data.get('editions', [])
        assert len(editions) > 0, "Should have at least one edition"
        
        # Check edition structure
        for edition in editions[:5]:
            assert 'date' in edition
            assert 'slot' in edition
            assert edition['slot'] in ['morning', 'evening']
            assert 'article_count' in edition


class TestTrimToCompleteSentences:
    """Tests for trim_to_complete_sentences logic via API response"""
    
    def test_no_mid_word_truncation(self):
        """Summaries should not end mid-word"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-07?slot=morning&lang=en")
        assert response.status_code == 200
        
        data = response.json()
        incomplete_endings = [' and', ' or', ' the', ' a', ' an', ' to', ' of', ' in', ' on', ' at']
        
        issues = []
        for page in data.get('pages', []):
            for article in page.get('articles', []):
                summary = article.get('summary', '').strip()
                for ending in incomplete_endings:
                    if summary.endswith(ending):
                        issues.append({
                            'id': article.get('id'),
                            'ending': summary[-30:]
                        })
                        break
        
        assert len(issues) == 0, f"Found summaries with incomplete endings: {issues}"
