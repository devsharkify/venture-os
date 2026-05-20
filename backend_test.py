#!/usr/bin/env python3

import requests
import sys
from datetime import datetime
import json
import os
from pathlib import Path
import io

class NewsPulseAPITester:
    def __init__(self, base_url="https://kaizer-newsbot.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_user_phone = f"9876543{datetime.now().strftime('%H%M')}"  # Unique phone for each run
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details="", endpoint=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "endpoint": endpoint,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}{endpoint}"
        
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)
        
        # Remove Content-Type for file uploads
        if files:
            test_headers.pop('Content-Type', None)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f", Expected: {expected_status}"
                try:
                    error_body = response.json()
                    details += f", Error: {error_body.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"

            self.log_test(name, success, details, endpoint)
            
            if success:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}", endpoint)
            return False, {}

    def test_otp_auth_flow(self):
        """Test complete OTP authentication flow"""
        print("\n🔐 Testing OTP Authentication Flow...")
        
        # Test send OTP
        success, response = self.run_test(
            "Send OTP",
            "POST",
            "/auth/send-otp",
            200,
            data={"mobile": self.test_user_phone, "country_code": "91"}
        )
        
        if not success:
            return False
        
        # Extract debug OTP if available
        debug_otp = response.get('debug_otp')
        if not debug_otp:
            debug_otp = "123456"  # Fallback for testing
        
        # Test verify OTP
        success, user_response = self.run_test(
            "Verify OTP",
            "POST",
            "/auth/verify-otp",
            200,
            data={"mobile": self.test_user_phone, "otp": debug_otp, "country_code": "91"}
        )
        
        if success:
            # Test get user
            self.run_test(
                "Get User Profile",
                "GET",
                f"/auth/user/{self.test_user_phone}",
                200
            )
            
            # Test update user
            self.run_test(
                "Update User Profile",
                "PUT",
                f"/auth/user/{self.test_user_phone}?name=Test User&preferred_language=en",
                200
            )
        
        return success

    def test_file_uploads(self):
        """Test file upload functionality"""
        print("\n📁 Testing File Upload APIs...")
        
        # Create a test image file in memory
        test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # Test image upload
        files = {'file': ('test.png', io.BytesIO(test_image_content), 'image/png')}
        success, response = self.run_test(
            "Upload Image",
            "POST", 
            "/upload/image",
            200,
            files=files
        )
        
        # Test invalid file type for image upload
        files = {'file': ('test.txt', io.BytesIO(b'test content'), 'text/plain')}
        self.run_test(
            "Upload Invalid Image Type",
            "POST",
            "/upload/image", 
            400,
            files=files
        )
        
        # Note: Video upload test would need a proper video file, 
        # but we'll test the endpoint exists
        return success

    def test_news_apis(self):
        """Test news-related APIs"""
        print("\n📰 Testing News APIs...")
        
        # Test get categories
        success, categories = self.run_test(
            "Get News Categories",
            "GET",
            "/news/categories",
            200
        )
        
        # Test get news feed
        self.run_test(
            "Get News Feed",
            "GET", 
            "/news/feed?limit=5",
            200
        )
        
        # Test create news (admin)
        news_data = {
            "title": "Test News Article",
            "summary": "This is a test news article",
            "category": "tech",
            "content_type": "text"
        }
        
        success, article = self.run_test(
            "Create News Article",
            "POST",
            "/news/admin/push",
            200,
            data=news_data
        )
        
        if success and 'id' in article:
            article_id = article['id']
            
            # Test get single article
            self.run_test(
                "Get Single Article",
                "GET",
                f"/news/article/{article_id}",
                200
            )
            
            # Test update article
            update_data = {"title": "Updated Test Article"}
            self.run_test(
                "Update News Article",
                "PUT",
                f"/news/admin/{article_id}",
                200,
                data=update_data
            )
            
            # Test pin/unpin article
            self.run_test(
                "Toggle Pin Article",
                "POST", 
                f"/news/admin/{article_id}/pin",
                200
            )
        
        # Test get admin news
        self.run_test(
            "Get Admin News List",
            "GET",
            "/news/admin/all?limit=5",
            200
        )
        
        return True

    def test_reporter_apis(self):
        """Test reporter-related APIs"""
        print("\n👨‍💼 Testing Reporter APIs...")
        
        # Test reporter registration
        reporter_data = {
            "name": "Test Reporter",
            "phone": self.test_user_phone,
            "email": "test@example.com",
            "location": "Test City",
            "bio": "Test reporter bio"
        }
        
        success, reporter = self.run_test(
            "Register Reporter",
            "POST",
            "/reporter/register",
            200,
            data=reporter_data
        )
        
        if success and 'id' in reporter:
            reporter_id = reporter['id']
            
            # Test check reporter status
            self.run_test(
                "Check Reporter Status",
                "GET",
                f"/reporter/check/{self.test_user_phone}",
                200
            )
            
            # Test get reporter details
            self.run_test(
                "Get Reporter Details",
                "GET",
                f"/reporter/{reporter_id}",
                200
            )
            
            # Test admin approve reporter
            self.run_test(
                "Approve Reporter (Admin)",
                "POST",
                f"/admin/reporters/{reporter_id}/approve",
                200
            )
            
            # Test submit news as reporter
            reporter_news = {
                "title": "Reporter News Test",
                "summary": "Test news from reporter",
                "category": "local",
                "news_type": "text"
            }
            
            self.run_test(
                "Submit Reporter News",
                "POST",
                f"/reporter/{reporter_id}/submit-news",
                200,
                data=reporter_news
            )
            
            # Test get reporter news
            self.run_test(
                "Get Reporter News List",
                "GET",
                f"/reporter/{reporter_id}/news",
                200
            )
        
        # Test get all reporters (admin)
        self.run_test(
            "Get All Reporters (Admin)",
            "GET",
            "/admin/reporters?limit=5",
            200
        )
        
        return True

    def test_misc_apis(self):
        """Test miscellaneous APIs"""
        print("\n🔧 Testing Miscellaneous APIs...")
        
        # Test root endpoint
        self.run_test(
            "API Root Endpoint",
            "GET",
            "/",
            200
        )
        
        # Test status check creation
        status_data = {"client_name": "test_client"}
        self.run_test(
            "Create Status Check",
            "POST",
            "/status",
            200,
            data=status_data
        )
        
        # Test get status checks
        self.run_test(
            "Get Status Checks",
            "GET",
            "/status",
            200
        )
        
        return True

    def run_all_tests(self):
        """Run all tests"""
        print(f"🚀 Starting NewsPulse API Tests...")
        print(f"Backend URL: {self.base_url}")
        print(f"Test Phone: {self.test_user_phone}")
        print("=" * 60)
        
        # Run test suites
        self.test_otp_auth_flow()
        self.test_file_uploads() 
        self.test_news_apis()
        self.test_reporter_apis()
        self.test_misc_apis()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Save detailed results
        results_file = "/app/test_reports/backend_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "tests_run": self.tests_run,
                    "tests_passed": self.tests_passed,
                    "success_rate": (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
                    "test_phone": self.test_user_phone,
                    "backend_url": self.base_url
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"📝 Detailed results saved to: {results_file}")
        
        # Return overall success
        return self.tests_passed == self.tests_run

def main():
    """Main function"""
    tester = NewsPulseAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())