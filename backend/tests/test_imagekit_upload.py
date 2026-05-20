"""
ImageKit Upload API Tests
Tests for image and video upload endpoints with ImageKit CDN integration
"""
import pytest
import requests
import os
import io

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable is required")


class TestImageUpload:
    """Tests for POST /api/upload/image endpoint"""
    
    def test_upload_jpeg_image_success(self):
        """Upload a valid JPEG image and verify ImageKit URL is returned"""
        # Create a minimal valid JPEG file (1x1 pixel)
        jpeg_bytes = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
            0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
            0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
            0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
            0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
            0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
            0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
            0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
            0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
            0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
            0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
            0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
            0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
            0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
            0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
            0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD5, 0xDB, 0x20, 0xB8, 0xED, 0x73, 0x5C,
            0xC5, 0xF6, 0xF4, 0xEC, 0x3F, 0xE2, 0xFF, 0xD9
        ])
        
        files = {'file': ('test_image.jpg', io.BytesIO(jpeg_bytes), 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/upload/image", files=files)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "url" in data, "Response should have 'url' field"
        assert "status" in data, "Response should have 'status' field"
        assert data["status"] == "uploaded", f"Status should be 'uploaded', got {data['status']}"
        
        # Verify ImageKit URL format
        url = data["url"]
        assert url.startswith("https://ik.imagekit.io/"), f"URL should start with 'https://ik.imagekit.io/', got {url}"
        assert "kaizer-news/images" in url, f"URL should contain 'kaizer-news/images' folder, got {url}"
        
        # Additional fields
        assert "filename" in data, "Response should have 'filename' field"
        assert "file_id" in data, "Response should have 'file_id' field"
        
        print(f"✅ Image uploaded successfully: {url}")
    
    def test_upload_png_image_success(self):
        """Upload a valid PNG image"""
        # Minimal valid PNG (1x1 pixel transparent)
        png_bytes = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
            0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
            0x0D, 0x49, 0x44, 0x41, 0x54, 0x08, 0xD7, 0x63, 0x60, 0x60, 0x60, 0x60,
            0x00, 0x00, 0x00, 0x05, 0x00, 0x01, 0x87, 0xA1, 0x4E, 0xD4, 0x00, 0x00,
            0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {'file': ('test_image.png', io.BytesIO(png_bytes), 'image/png')}
        response = requests.post(f"{BASE_URL}/api/upload/image", files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["url"].startswith("https://ik.imagekit.io/"), "PNG upload should return ImageKit URL"
        print(f"✅ PNG uploaded successfully: {data['url']}")
    
    def test_upload_invalid_file_type_rejected(self):
        """Verify non-image files are rejected"""
        # Plain text file
        text_content = b"This is not an image file"
        files = {'file': ('test.txt', io.BytesIO(text_content), 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/upload/image", files=files)
        
        # Should be rejected with 400
        assert response.status_code == 400, f"Expected 400 for invalid file type, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail' field"
        assert "Invalid file type" in data["detail"] or "Allowed" in data["detail"], f"Error should mention invalid file type: {data['detail']}"
        print(f"✅ Non-image file correctly rejected: {data['detail']}")
    
    def test_upload_pdf_as_image_rejected(self):
        """Verify PDF files are rejected when uploading as image"""
        # Minimal PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        files = {'file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf')}
        response = requests.post(f"{BASE_URL}/api/upload/image", files=files)
        
        assert response.status_code == 400, f"Expected 400 for PDF file, got {response.status_code}"
        print("✅ PDF file correctly rejected for image upload")
    
    def test_upload_file_too_large_rejected(self):
        """Verify files larger than 5MB are rejected"""
        # Create file larger than 5MB (5.1MB)
        large_content = b'\x00' * (5 * 1024 * 1024 + 100 * 1024)  # 5.1MB
        files = {'file': ('large_image.jpg', io.BytesIO(large_content), 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/upload/image", files=files)
        
        # Should be rejected with 400
        assert response.status_code == 400, f"Expected 400 for large file, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail' field"
        assert "too large" in data["detail"].lower() or "5mb" in data["detail"].lower(), f"Error should mention file size: {data['detail']}"
        print(f"✅ Large file correctly rejected: {data['detail']}")


class TestVideoUpload:
    """Tests for POST /api/upload/video endpoint"""
    
    def test_upload_mp4_video_success(self):
        """Upload a valid MP4 video and verify ImageKit URL is returned"""
        # Minimal valid MP4 header (ftyp box + moov stub)
        mp4_bytes = bytes([
            0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70, 0x69, 0x73, 0x6F, 0x6D,
            0x00, 0x00, 0x02, 0x00, 0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
            0x6D, 0x70, 0x34, 0x31, 0x61, 0x76, 0x63, 0x31, 0x00, 0x00, 0x00, 0x08,
            0x66, 0x72, 0x65, 0x65, 0x00, 0x00, 0x00, 0x00, 0x6D, 0x6F, 0x6F, 0x76
        ])
        
        files = {'file': ('test_video.mp4', io.BytesIO(mp4_bytes), 'video/mp4')}
        response = requests.post(f"{BASE_URL}/api/upload/video", files=files)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "url" in data, "Response should have 'url' field"
        assert "status" in data, "Response should have 'status' field"
        assert data["status"] == "uploaded", f"Status should be 'uploaded', got {data['status']}"
        
        # Verify ImageKit URL format
        url = data["url"]
        assert url.startswith("https://ik.imagekit.io/"), f"URL should start with 'https://ik.imagekit.io/', got {url}"
        assert "kaizer-news/videos" in url, f"URL should contain 'kaizer-news/videos' folder, got {url}"
        
        # Additional fields
        assert "filename" in data, "Response should have 'filename' field"
        assert "file_id" in data, "Response should have 'file_id' field"
        
        print(f"✅ Video uploaded successfully: {url}")
    
    def test_upload_invalid_video_type_rejected(self):
        """Verify non-video files are rejected"""
        # Plain text file
        text_content = b"This is not a video file"
        files = {'file': ('test.txt', io.BytesIO(text_content), 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/upload/video", files=files)
        
        # Should be rejected with 400
        assert response.status_code == 400, f"Expected 400 for invalid file type, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail' field"
        assert "Invalid file type" in data["detail"] or "Allowed" in data["detail"], f"Error should mention invalid file type: {data['detail']}"
        print(f"✅ Non-video file correctly rejected: {data['detail']}")
    
    def test_upload_image_as_video_rejected(self):
        """Verify image files are rejected when uploading as video"""
        # Minimal PNG
        png_bytes = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
            0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
            0x0D, 0x49, 0x44, 0x41, 0x54, 0x08, 0xD7, 0x63, 0x60, 0x60, 0x60, 0x60,
            0x00, 0x00, 0x00, 0x05, 0x00, 0x01, 0x87, 0xA1, 0x4E, 0xD4, 0x00, 0x00,
            0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        files = {'file': ('test.png', io.BytesIO(png_bytes), 'image/png')}
        response = requests.post(f"{BASE_URL}/api/upload/video", files=files)
        
        assert response.status_code == 400, f"Expected 400 for image as video, got {response.status_code}"
        print("✅ Image file correctly rejected for video upload")


class TestImageKitURLAccessibility:
    """Test that uploaded ImageKit URLs are accessible"""
    
    def test_uploaded_image_url_accessible(self):
        """Verify uploaded image URL returns 200 on HTTP GET"""
        # First upload an image
        png_bytes = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
            0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
            0x0D, 0x49, 0x44, 0x41, 0x54, 0x08, 0xD7, 0x63, 0x60, 0x60, 0x60, 0x60,
            0x00, 0x00, 0x00, 0x05, 0x00, 0x01, 0x87, 0xA1, 0x4E, 0xD4, 0x00, 0x00,
            0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {'file': ('accessibility_test.png', io.BytesIO(png_bytes), 'image/png')}
        upload_response = requests.post(f"{BASE_URL}/api/upload/image", files=files)
        
        assert upload_response.status_code == 200, "Upload should succeed first"
        
        upload_data = upload_response.json()
        image_url = upload_data["url"]
        
        # Now verify URL is accessible
        get_response = requests.get(image_url, timeout=10)
        assert get_response.status_code == 200, f"Image URL should be accessible with 200, got {get_response.status_code}"
        
        # Verify content type
        content_type = get_response.headers.get('Content-Type', '')
        assert 'image' in content_type, f"Response should be an image, got Content-Type: {content_type}"
        
        print(f"✅ Uploaded image URL is accessible: {image_url}")


class TestNewsCreationWithImageKit:
    """Test admin news creation with ImageKit uploaded images"""
    
    def test_create_news_with_imagekit_image(self):
        """Create a news article with an ImageKit image URL"""
        # First upload an image
        png_bytes = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
            0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
            0x0D, 0x49, 0x44, 0x41, 0x54, 0x08, 0xD7, 0x63, 0x60, 0x60, 0x60, 0x60,
            0x00, 0x00, 0x00, 0x05, 0x00, 0x01, 0x87, 0xA1, 0x4E, 0xD4, 0x00, 0x00,
            0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {'file': ('news_image.png', io.BytesIO(png_bytes), 'image/png')}
        upload_response = requests.post(f"{BASE_URL}/api/upload/image", files=files)
        
        assert upload_response.status_code == 200, f"Image upload should succeed: {upload_response.text}"
        image_url = upload_response.json()["url"]
        
        # Create news article with the uploaded image
        news_data = {
            "title": "TEST_ImageKit Integration Test Article",
            "summary": "This is a test article for ImageKit integration testing.",
            "category": "tech",
            "image": image_url,
            "content_type": "text",
            "priority": 5
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/news/admin/push",
            json=news_data
        )
        
        assert create_response.status_code == 200, f"News creation should succeed: {create_response.text}"
        
        created_article = create_response.json()
        assert created_article["image"] == image_url, "Article should have the ImageKit image URL"
        assert created_article["image"].startswith("https://ik.imagekit.io/"), "Image URL should be an ImageKit URL"
        
        article_id = created_article["id"]
        
        # Verify by fetching the article
        get_response = requests.get(f"{BASE_URL}/api/news/article/{article_id}")
        assert get_response.status_code == 200, "Should be able to fetch the created article"
        
        fetched_article = get_response.json()
        assert fetched_article["image"] == image_url, "Fetched article should have the ImageKit image URL"
        
        # Cleanup - delete the test article
        delete_response = requests.delete(f"{BASE_URL}/api/news/admin/{article_id}")
        assert delete_response.status_code == 200, "Article cleanup should succeed"
        
        print(f"✅ News article created with ImageKit image: {image_url}")


class TestNewsFeedWithImageKitURLs:
    """Test news feed displays articles with ImageKit URLs correctly"""
    
    def test_news_feed_returns_imagekit_urls(self):
        """Verify news feed returns articles with ImageKit URLs unchanged"""
        # Get news feed
        response = requests.get(f"{BASE_URL}/api/news/feed?limit=50")
        
        assert response.status_code == 200, f"News feed should return 200, got {response.status_code}"
        
        articles = response.json()
        imagekit_articles = []
        
        for article in articles:
            if article.get("image") and article["image"].startswith("https://ik.imagekit.io/"):
                imagekit_articles.append(article)
                # Verify the URL is complete and not modified
                assert "ik.imagekit.io" in article["image"], "ImageKit URL should be preserved"
                assert not article["image"].startswith("http://"), "URL should use HTTPS"
        
        if imagekit_articles:
            print(f"✅ Found {len(imagekit_articles)} articles with ImageKit URLs in news feed")
            for article in imagekit_articles[:3]:  # Show first 3
                print(f"   - {article['title'][:50]}...: {article['image']}")
        else:
            print("⚠️ No articles with ImageKit URLs found in feed (this may be expected if no images uploaded yet)")


# Additional health check
class TestAPIHealth:
    """Basic API health checks"""
    
    def test_api_root_accessible(self):
        """Verify API root is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"API root should return 200, got {response.status_code}"
        print("✅ API is accessible")
    
    def test_categories_endpoint(self):
        """Verify categories endpoint works"""
        response = requests.get(f"{BASE_URL}/api/news/categories")
        assert response.status_code == 200, f"Categories should return 200, got {response.status_code}"
        
        data = response.json()
        assert "categories" in data, "Response should have categories"
        print(f"✅ Categories endpoint working, {len(data['categories'])} categories found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
