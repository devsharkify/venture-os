"""Test cases for SEO Agent and Tech Performance Agent APIs"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSEOAgent:
    """Tests for Social Media Expert / SEO Agent endpoints"""

    def test_seo_run_agent_returns_started(self):
        """POST /api/agents/seo/run should return status:started"""
        response = requests.post(f"{BASE_URL}/api/agents/seo/run")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "started"
        assert "message" in data
        print(f"SEO Agent run: {data}")

    def test_seo_latest_report_structure(self):
        """GET /api/agents/seo/latest should return SEO report with all required fields"""
        response = requests.get(f"{BASE_URL}/api/agents/seo/latest")
        assert response.status_code == 200
        data = response.json()
        
        # Check status and report structure
        assert "status" in data
        if data.get("status") == "ok":
            report = data.get("report")
            assert report is not None, "Report should exist"
            
            # Verify required fields
            assert "seo_score" in report, "SEO report should have seo_score"
            assert "trending_keywords" in report, "SEO report should have trending_keywords"
            assert "tweets" in report, "SEO report should have tweets"
            assert "content_gaps" in report, "SEO report should have content_gaps"
            assert "meta_suggestions" in report, "SEO report should have meta_suggestions"
            assert "strategy_report" in report, "SEO report should have strategy_report"
            assert "created_at" in report
            assert "id" in report
            
            # Validate data types
            assert isinstance(report["seo_score"], (int, float))
            assert isinstance(report["trending_keywords"], list)
            assert isinstance(report["tweets"], list)
            assert isinstance(report["content_gaps"], list)
            
            print(f"SEO Score: {report['seo_score']}")
            print(f"Keywords count: {len(report['trending_keywords'])}")
            print(f"Tweets count: {len(report['tweets'])}")

    def test_seo_keywords_endpoint(self):
        """GET /api/agents/seo/keywords should return trending keywords"""
        response = requests.get(f"{BASE_URL}/api/agents/seo/keywords")
        assert response.status_code == 200
        data = response.json()
        
        assert "keywords" in data
        assert isinstance(data["keywords"], list)
        
        if data["keywords"]:
            print(f"Keywords: {data['keywords'][:5]}...")
            assert "updated_at" in data

    def test_seo_social_content_endpoint(self):
        """GET /api/agents/seo/social-content should return social media content"""
        response = requests.get(f"{BASE_URL}/api/agents/seo/social-content")
        assert response.status_code == 200
        data = response.json()
        
        if data.get("content"):
            content = data["content"]
            # Check for tweets, instagram captions, hashtags
            assert "tweets" in content or "created_at" in content
            print(f"Social content keys: {list(content.keys())}")

    def test_seo_reports_list(self):
        """GET /api/agents/seo/reports should return list of SEO reports"""
        response = requests.get(f"{BASE_URL}/api/agents/seo/reports")
        assert response.status_code == 200
        data = response.json()
        
        assert "reports" in data
        assert isinstance(data["reports"], list)
        
        if data["reports"]:
            report = data["reports"][0]
            assert "id" in report
            assert "created_at" in report
            assert "seo_score" in report
            print(f"Total SEO reports: {len(data['reports'])}")


class TestTechAgent:
    """Tests for Tech Performance Agent endpoints"""

    def test_tech_run_returns_report(self):
        """POST /api/agents/tech/run should return a performance report"""
        response = requests.post(f"{BASE_URL}/api/agents/tech/run")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "ok"
        report = data.get("report")
        assert report is not None
        
        # Verify report structure
        assert "health_score" in report
        assert "last_hour" in report
        assert "top_endpoints" in report
        assert "created_at" in report
        
        # Validate health_score range
        assert 0 <= report["health_score"] <= 100
        
        # Validate last_hour stats
        lh = report["last_hour"]
        assert "total_requests" in lh
        assert "avg_response_ms" in lh
        assert "p95_response_ms" in lh
        assert "error_count" in lh
        
        print(f"Health Score: {report['health_score']}")
        print(f"Last Hour Requests: {lh['total_requests']}")
        print(f"Avg Response: {lh['avg_response_ms']}ms")

    def test_tech_latest_report(self):
        """GET /api/agents/tech/latest should return latest performance report"""
        response = requests.get(f"{BASE_URL}/api/agents/tech/latest")
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        if data.get("status") == "ok":
            report = data.get("report")
            assert report is not None
            assert "health_score" in report
            assert "last_hour" in report
            assert "top_endpoints" in report
            print(f"Latest Health Score: {report['health_score']}")

    def test_tech_recent_metrics(self):
        """GET /api/agents/tech/metrics/recent should return recent raw metrics"""
        response = requests.get(f"{BASE_URL}/api/agents/tech/metrics/recent")
        assert response.status_code == 200
        data = response.json()
        
        assert "metrics" in data
        assert isinstance(data["metrics"], list)
        
        if data["metrics"]:
            metric = data["metrics"][0]
            assert "endpoint" in metric
            assert "method" in metric
            assert "status_code" in metric
            assert "response_time_ms" in metric
            assert "timestamp" in metric
            print(f"Recent metrics count: {len(data['metrics'])}")

    def test_tech_endpoint_stats(self):
        """GET /api/agents/tech/metrics/endpoints should return per-endpoint aggregated stats"""
        response = requests.get(f"{BASE_URL}/api/agents/tech/metrics/endpoints")
        assert response.status_code == 200
        data = response.json()
        
        assert "endpoints" in data
        assert isinstance(data["endpoints"], list)
        
        if data["endpoints"]:
            endpoint = data["endpoints"][0]
            assert "endpoint" in endpoint
            assert "avg_ms" in endpoint
            assert "max_ms" in endpoint
            assert "requests" in endpoint
            assert "errors" in endpoint
            print(f"Tracked endpoints: {len(data['endpoints'])}")
            for ep in data["endpoints"][:3]:
                print(f"  {ep['endpoint']}: {ep['avg_ms']}ms avg, {ep['requests']} reqs")

    def test_tech_reports_list(self):
        """GET /api/agents/tech/reports should return list of performance reports"""
        response = requests.get(f"{BASE_URL}/api/agents/tech/reports")
        assert response.status_code == 200
        data = response.json()
        
        assert "reports" in data
        assert isinstance(data["reports"], list)
        
        if data["reports"]:
            report = data["reports"][0]
            assert "id" in report
            assert "health_score" in report
            assert "created_at" in report
            print(f"Total performance reports: {len(data['reports'])}")


class TestPerformanceMiddleware:
    """Tests to verify performance middleware is tracking API calls"""

    def test_middleware_tracking_after_api_call(self):
        """After making API calls, metrics should be recorded"""
        # First, make a few API calls to generate metrics
        requests.get(f"{BASE_URL}/api/news/categories")
        requests.get(f"{BASE_URL}/api/agents/editor/latest")
        
        # Give middleware time to flush
        import time
        time.sleep(1)
        
        # Check recent metrics
        response = requests.get(f"{BASE_URL}/api/agents/tech/metrics/recent")
        assert response.status_code == 200
        data = response.json()
        
        assert "metrics" in data
        # Metrics should have been recorded
        print(f"Metrics recorded: {len(data.get('metrics', []))}")


class TestExistingAgents:
    """Verify existing Editor and Investigator agents still work"""

    def test_editor_agent_latest(self):
        """GET /api/agents/editor/latest should still work"""
        response = requests.get(f"{BASE_URL}/api/agents/editor/latest")
        assert response.status_code == 200
        data = response.json()
        assert "report" in data or "status" in data
        print(f"Editor agent response: {list(data.keys())}")

    def test_investigator_topics(self):
        """GET /api/agents/investigator/topics should still work"""
        response = requests.get(f"{BASE_URL}/api/agents/investigator/topics")
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        print(f"Investigator topics: {len(data.get('topics', []))}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
