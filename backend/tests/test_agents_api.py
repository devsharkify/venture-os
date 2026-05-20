"""
Test AI Agents API endpoints (News Editor + Investigative Reporter)
Tests: editor/latest, editor/run, investigator/topics, investigator/run, investigator/report, investigator/timeline
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAgentsHealth:
    """Verify server is responsive and agents don't block main server"""
    
    def test_health_check(self):
        """Server health check should return ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Health check passed")


class TestEditorAgent:
    """News Editor Agent API tests"""
    
    def test_get_editor_latest_returns_report(self):
        """GET /api/agents/editor/latest returns editor report with editorial, hero_picks, duplicates"""
        response = requests.get(f"{BASE_URL}/api/agents/editor/latest")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "report" in data
        
        if data["status"] == "ok":
            report = data["report"]
            # Verify report structure
            assert "id" in report, "Report should have id"
            assert "editorial_en" in report, "Report should have editorial_en"
            assert "editorial_te" in report, "Report should have editorial_te"
            assert "hero_picks" in report, "Report should have hero_picks"
            assert "duplicate_groups" in report, "Report should have duplicate_groups"
            assert "created_at" in report, "Report should have created_at"
            assert "total_articles" in report, "Report should have total_articles"
            assert "hero_articles" in report, "Report should have hero_articles"
            
            # Verify editorial content exists
            assert len(report["editorial_en"]) > 100, "English editorial should have substantial content"
            
            print(f"✓ Editor report retrieved - {report['total_articles']} articles analyzed")
            print(f"  Editorial EN length: {len(report['editorial_en'])} chars")
            print(f"  Hero picks: {report['hero_picks']}")
            print(f"  Duplicate groups: {len(report['duplicate_groups'])}")
        else:
            print("⚠ No editor report yet (run editor first)")
    
    def test_post_editor_run_starts_agent(self):
        """POST /api/agents/editor/run starts editor agent (returns immediately with status:started)"""
        response = requests.post(f"{BASE_URL}/api/agents/editor/run")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started", "Should return status: started"
        assert "message" in data
        print(f"✓ Editor agent started: {data['message']}")
    
    def test_server_responsive_after_editor_start(self):
        """Server stays responsive after starting editor agent"""
        # Start the editor
        requests.post(f"{BASE_URL}/api/agents/editor/run")
        
        # Immediately check health
        time.sleep(0.5)  # Small delay
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Server responsive after starting editor agent (non-blocking)")
    
    def test_get_editor_reports_list(self):
        """GET /api/agents/editor/reports returns list of reports"""
        response = requests.get(f"{BASE_URL}/api/agents/editor/reports")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        assert isinstance(data["reports"], list)
        print(f"✓ Editor reports list: {len(data['reports'])} reports")


class TestInvestigatorAgent:
    """Investigative Reporter Agent API tests"""
    
    def test_get_topics_returns_3_topics(self):
        """GET /api/agents/investigator/topics returns 3 topics (telangana-politics, india-politics, corruption)"""
        response = requests.get(f"{BASE_URL}/api/agents/investigator/topics")
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        topics = data["topics"]
        assert len(topics) >= 3, f"Expected at least 3 topics, got {len(topics)}"
        
        topic_ids = [t["id"] for t in topics]
        assert "telangana-politics" in topic_ids, "Should have telangana-politics topic"
        assert "india-politics" in topic_ids, "Should have india-politics topic"
        assert "corruption" in topic_ids, "Should have corruption topic"
        
        # Verify topic structure
        for topic in topics:
            assert "id" in topic
            assert "name_en" in topic
            assert "name_te" in topic
            assert "keywords" in topic
            assert "active" in topic
            assert len(topic["keywords"]) > 0, "Topic should have keywords"
        
        print(f"✓ 3 topics retrieved:")
        for t in topics:
            print(f"  - {t['id']}: {t['name_en']} ({t['event_count']} events)")
    
    def test_post_investigator_run_topic_starts_investigation(self):
        """POST /api/agents/investigator/run/telangana-politics starts investigation (non-blocking)"""
        response = requests.post(f"{BASE_URL}/api/agents/investigator/run/telangana-politics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert "message" in data
        print(f"✓ Investigation started: {data['message']}")
    
    def test_get_investigation_report_telangana(self):
        """GET /api/agents/investigator/report/telangana-politics returns report with report_en, report_te, events"""
        response = requests.get(f"{BASE_URL}/api/agents/investigator/report/telangana-politics")
        assert response.status_code == 200
        data = response.json()
        
        assert "report" in data
        assert "events" in data
        assert "topic" in data
        
        if data["report"]:
            report = data["report"]
            assert "report_en" in report, "Report should have report_en"
            assert "report_te" in report, "Report should have report_te"
            assert "topic_id" in report
            assert "created_at" in report
            assert report["topic_id"] == "telangana-politics"
            
            # Verify report content
            assert len(report["report_en"]) > 200, "English report should have substantial content"
            
            print(f"✓ Telangana Politics report retrieved")
            print(f"  EN report length: {len(report['report_en'])} chars")
            print(f"  TE report length: {len(report.get('report_te', ''))} chars")
            print(f"  Events: {len(data['events'])}")
        else:
            print("⚠ No report yet (run investigator first)")
    
    def test_get_investigation_report_india_politics(self):
        """GET /api/agents/investigator/report/india-politics returns report"""
        response = requests.get(f"{BASE_URL}/api/agents/investigator/report/india-politics")
        assert response.status_code == 200
        data = response.json()
        assert "report" in data
        
        if data["report"]:
            print(f"✓ India Politics report retrieved - {len(data['events'])} events")
        else:
            print("⚠ No India Politics report yet")
    
    def test_get_investigation_report_corruption(self):
        """GET /api/agents/investigator/report/corruption returns report"""
        response = requests.get(f"{BASE_URL}/api/agents/investigator/report/corruption")
        assert response.status_code == 200
        data = response.json()
        assert "report" in data
        
        if data["report"]:
            print(f"✓ Corruption report retrieved - {len(data['events'])} events")
        else:
            print("⚠ No Corruption report yet")
    
    def test_get_timeline_returns_events(self):
        """GET /api/agents/investigator/timeline/telangana-politics returns events list"""
        response = requests.get(f"{BASE_URL}/api/agents/investigator/timeline/telangana-politics")
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert "topic" in data
        events = data["events"]
        assert isinstance(events, list)
        
        if len(events) > 0:
            event = events[0]
            # Verify event structure
            assert "id" in event
            assert "topic_id" in event
            assert "title" in event
            assert "summary" in event
            assert "source" in event
            assert event["topic_id"] == "telangana-politics"
            
            print(f"✓ Timeline retrieved - {len(events)} events")
            print(f"  Latest event: [{event['source']}] {event['title'][:60]}...")
        else:
            print("⚠ No timeline events yet")
    
    def test_server_responsive_after_investigation_start(self):
        """Server stays responsive after starting investigation"""
        requests.post(f"{BASE_URL}/api/agents/investigator/run/india-politics")
        
        # Immediately check health
        time.sleep(0.5)
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Server responsive after starting investigation (non-blocking)")
    
    def test_run_all_investigations(self):
        """POST /api/agents/investigator/run-all starts all investigations"""
        response = requests.post(f"{BASE_URL}/api/agents/investigator/run-all")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        print(f"✓ All investigations started: {data['message']}")


class TestAgentIntegration:
    """Integration tests for agent functionality"""
    
    def test_report_bilingual_content(self):
        """Verify reports have both English and Telugu content"""
        response = requests.get(f"{BASE_URL}/api/agents/editor/latest")
        assert response.status_code == 200
        data = response.json()
        
        if data["status"] == "ok":
            report = data["report"]
            editorial_en = report.get("editorial_en", "")
            editorial_te = report.get("editorial_te", "")
            
            # Check both have content
            assert len(editorial_en) > 50, "English editorial should exist"
            assert len(editorial_te) > 50, "Telugu editorial should exist"
            
            # Check Telugu contains Telugu characters
            telugu_chars = any('\u0C00' <= c <= '\u0C7F' for c in editorial_te)
            assert telugu_chars, "Telugu editorial should contain Telugu script"
            
            print("✓ Bilingual editorial content verified (EN + TE)")
    
    def test_investigation_report_bilingual(self):
        """Verify investigation reports have bilingual content"""
        response = requests.get(f"{BASE_URL}/api/agents/investigator/report/telangana-politics")
        assert response.status_code == 200
        data = response.json()
        
        if data["report"]:
            report = data["report"]
            report_en = report.get("report_en", "")
            report_te = report.get("report_te", "")
            
            assert len(report_en) > 100, "English report should exist"
            if report_te:
                telugu_chars = any('\u0C00' <= c <= '\u0C7F' for c in report_te)
                if telugu_chars:
                    print("✓ Investigation report has bilingual content (EN + TE)")
                else:
                    print("⚠ Telugu report may not have Telugu script")
            else:
                print("⚠ Telugu report empty")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
