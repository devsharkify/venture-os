"""
Test Telegram Bot Routes and ePaper PDF Generation
Tests for iteration 21 - Telegram bot integration and PDF fixes
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndConfig:
    """Basic health and configuration checks"""
    
    def test_health_endpoint(self):
        """GET /api/health returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"✓ Health check passed: {data}")
    
    def test_telegram_config(self):
        """GET /api/telegram/config returns bot_configured:true"""
        response = requests.get(f"{BASE_URL}/api/telegram/config")
        assert response.status_code == 200
        data = response.json()
        assert "bot_configured" in data
        assert data["bot_configured"] == True, f"Bot should be configured, got: {data}"
        print(f"✓ Telegram config: bot_configured={data['bot_configured']}, admin_chat_id={data.get('admin_chat_id')}")


class TestTelegramReportEndpoints:
    """Test Telegram report generation endpoints"""
    
    def test_send_morning_report(self):
        """POST /api/telegram/send-report/morning generates report"""
        response = requests.post(f"{BASE_URL}/api/telegram/send-report/morning")
        assert response.status_code == 200
        data = response.json()
        # Will return "failed" if no admin_chat_id set, which is expected
        assert "status" in data
        print(f"✓ Morning report endpoint: status={data.get('status')}")
    
    def test_send_evening_report(self):
        """POST /api/telegram/send-report/evening generates report"""
        response = requests.post(f"{BASE_URL}/api/telegram/send-report/evening")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✓ Evening report endpoint: status={data.get('status')}")
    
    def test_send_pdf_endpoint(self):
        """POST /api/telegram/send-pdf generates PDF"""
        response = requests.post(f"{BASE_URL}/api/telegram/send-pdf")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✓ Send PDF endpoint: status={data.get('status')}")
    
    def test_send_pdf_with_params(self):
        """POST /api/telegram/send-pdf with date/slot/lang params"""
        response = requests.post(f"{BASE_URL}/api/telegram/send-pdf?date=2026-03-08&slot=morning&lang=en")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✓ Send PDF with params: status={data.get('status')}")


class TestEpaperPDFDownload:
    """Test ePaper PDF download endpoints - core feature"""
    
    def test_pdf_english_morning(self):
        """GET /api/epaper/2026-03-08/pdf?lang=en&slot=morning returns PDF"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08/pdf?lang=en&slot=morning",
            timeout=60
        )
        # May return 404 if no articles for this date, but should not error
        if response.status_code == 200:
            assert response.headers.get('content-type') == 'application/pdf'
            assert len(response.content) > 1000, "PDF should have substantial content"
            print(f"✓ English morning PDF: {len(response.content)} bytes")
        elif response.status_code == 404:
            print(f"✓ English morning PDF: 404 (no articles for date)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}, {response.text}")
    
    def test_pdf_telugu_morning(self):
        """GET /api/epaper/2026-03-08/pdf?lang=te&slot=morning returns Telugu PDF"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-08/pdf?lang=te&slot=morning",
            timeout=60
        )
        if response.status_code == 200:
            assert response.headers.get('content-type') == 'application/pdf'
            print(f"✓ Telugu morning PDF: {len(response.content)} bytes")
        elif response.status_code == 404:
            print(f"✓ Telugu morning PDF: 404 (no Telugu articles for date)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}, {response.text}")
    
    def test_pdf_latest_date(self):
        """Test PDF with latest available date"""
        # First get editions list
        editions_resp = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert editions_resp.status_code == 200
        editions = editions_resp.json().get("editions", [])
        
        if not editions:
            pytest.skip("No editions available")
        
        # Use the first (most recent) edition
        latest = editions[0]
        date = latest["date"]
        slot = latest.get("slot", "evening")
        
        print(f"  Testing PDF for latest edition: {date} {slot}")
        response = requests.get(
            f"{BASE_URL}/api/epaper/{date}/pdf?lang=en&slot={slot}",
            timeout=60
        )
        
        if response.status_code == 200:
            assert response.headers.get('content-type') == 'application/pdf'
            assert len(response.content) > 1000
            print(f"✓ Latest PDF ({date} {slot}): {len(response.content)} bytes")
        elif response.status_code == 404:
            print(f"✓ Latest PDF ({date} {slot}): 404 (no articles)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}")


class TestEpaperEditions:
    """Test ePaper editions listing"""
    
    def test_editions_list(self):
        """GET /api/epaper/editions returns edition list"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions")
        assert response.status_code == 200
        data = response.json()
        assert "editions" in data
        editions = data["editions"]
        print(f"✓ Editions list: {len(editions)} editions available")
        if editions:
            print(f"  Latest: {editions[0]['date']} {editions[0]['slot']} ({editions[0]['article_count']} articles)")
    
    def test_edition_content(self):
        """GET /api/epaper/{date} returns edition content"""
        # Get editions first
        editions_resp = requests.get(f"{BASE_URL}/api/epaper/editions")
        editions = editions_resp.json().get("editions", [])
        
        if not editions:
            pytest.skip("No editions available")
        
        latest = editions[0]
        response = requests.get(f"{BASE_URL}/api/epaper/{latest['date']}?lang=en&slot={latest['slot']}")
        assert response.status_code == 200
        data = response.json()
        assert "pages" in data
        assert "edition_title" in data
        print(f"✓ Edition content: {len(data.get('pages', []))} pages, {data.get('total_articles', 0)} articles")


class TestTelegramWebhook:
    """Test Telegram webhook endpoint"""
    
    def test_webhook_empty_message(self):
        """POST /api/telegram/webhook handles empty message"""
        response = requests.post(
            f"{BASE_URL}/api/telegram/webhook",
            json={"message": {}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✓ Webhook empty message handled: {data}")
    
    def test_webhook_start_command(self):
        """POST /api/telegram/webhook with /start command"""
        response = requests.post(
            f"{BASE_URL}/api/telegram/webhook",
            json={
                "message": {
                    "chat": {"id": 123456789},
                    "text": "/start"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✓ Webhook /start handled: {data}")


class TestAgentsPage:
    """Test Agents page is accessible"""
    
    def test_agents_editor_latest(self):
        """GET /api/agents/editor/latest returns data"""
        response = requests.get(f"{BASE_URL}/api/agents/editor/latest")
        assert response.status_code == 200
        print(f"✓ Editor latest: {response.status_code}")
    
    def test_agents_investigator_topics(self):
        """GET /api/agents/investigator/topics returns topics"""
        response = requests.get(f"{BASE_URL}/api/agents/investigator/topics")
        assert response.status_code == 200
        print(f"✓ Investigator topics: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
