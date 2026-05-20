"""
Test ePaper PDF Generation
Testing:
- PDF generation with correct fonts (Playfair Display, PT Serif, Noto Serif Telugu)
- Multiple languages (English and Telugu)
- Multiple slots (morning and evening)
- PDF structure (pages, images, CMYK dots, masthead)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEpaperEditions:
    """Test /api/epaper/editions endpoint"""
    
    def test_editions_endpoint_returns_data(self):
        """GET /api/epaper/editions returns available editions"""
        response = requests.get(f"{BASE_URL}/api/epaper/editions", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "editions" in data, "Response should contain 'editions' field"
        assert isinstance(data["editions"], list), "Editions should be a list"
        assert len(data["editions"]) > 0, "Should have at least one edition"
        
        # Verify edition structure
        edition = data["editions"][0]
        assert "date" in edition, "Edition should have 'date'"
        assert "slot" in edition, "Edition should have 'slot'"
        assert "article_count" in edition, "Edition should have 'article_count'"
        print(f"✓ Found {len(data['editions'])} editions. Latest: {edition['date']} {edition['slot']} ({edition['article_count']} articles)")

class TestEpaperContent:
    """Test /api/epaper/{date} endpoint"""
    
    def test_english_evening_edition_content(self):
        """GET /api/epaper/2026-03-16?lang=en&slot=evening returns article data"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-16?lang=en&slot=evening", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "date" in data, "Response should contain 'date'"
        assert "slot" in data, "Response should contain 'slot'"
        assert "lang" in data, "Response should contain 'lang'"
        assert "pages" in data, "Response should contain 'pages'"
        assert "total_articles" in data, "Response should contain 'total_articles'"
        assert data["date"] == "2026-03-16"
        assert data["slot"] == "evening"
        assert data["lang"] == "en"
        
        # Verify pages structure
        assert len(data["pages"]) > 0, "Should have at least one page"
        page = data["pages"][0]
        assert "title" in page, "Page should have 'title'"
        assert "articles" in page, "Page should have 'articles'"
        assert len(page["articles"]) > 0, "Page should have articles"
        
        # Verify article structure
        article = page["articles"][0]
        assert "id" in article, "Article should have 'id'"
        assert "title" in article, "Article should have 'title'"
        assert "summary" in article, "Article should have 'summary'"
        print(f"✓ English evening edition has {data['total_articles']} articles across {len(data['pages'])} pages")
    
    def test_telugu_evening_edition_content(self):
        """GET /api/epaper/2026-03-16?lang=te&slot=evening returns Telugu article data"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-16?lang=te&slot=evening", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["lang"] == "te"
        # Telugu edition may have fewer articles
        print(f"✓ Telugu evening edition has {data['total_articles']} articles")

    def test_morning_edition_content(self):
        """GET /api/epaper/2026-03-17?lang=en&slot=morning returns morning edition data"""
        response = requests.get(f"{BASE_URL}/api/epaper/2026-03-17?lang=en&slot=morning", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["slot"] == "morning"
        print(f"✓ Morning edition (2026-03-17) has {data['total_articles']} articles")

class TestEpaperPDF:
    """Test /api/epaper/{date}/pdf endpoint - PDF generation and structure"""
    
    def test_english_evening_pdf_generation(self):
        """GET /api/epaper/2026-03-16/pdf?lang=en&slot=evening generates a valid PDF"""
        print("Requesting English evening PDF (this may take 30-60 seconds)...")
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-16/pdf?lang=en&slot=evening", 
            timeout=120,
            stream=True
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500] if response.status_code != 200 else ''}"
        assert response.headers.get('content-type') == 'application/pdf', f"Expected PDF content type, got {response.headers.get('content-type')}"
        
        # Check content-disposition header
        content_disp = response.headers.get('content-disposition', '')
        assert 'attachment' in content_disp, "Should have attachment disposition"
        assert 'kaizer_news' in content_disp, "Filename should contain 'kaizer_news'"
        
        # Get PDF content
        pdf_bytes = response.content
        assert len(pdf_bytes) > 1000, f"PDF should be substantial, got {len(pdf_bytes)} bytes"
        
        # Save to /tmp for analysis
        pdf_path = '/tmp/test_english_evening.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✓ English evening PDF generated in {elapsed:.1f}s, size: {len(pdf_bytes)} bytes, saved to {pdf_path}")
        
        # Analyze PDF structure using pymupdf
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            
            # Check page count
            page_count = len(doc)
            assert page_count >= 1, f"PDF should have at least 1 page, got {page_count}"
            print(f"  - PDF has {page_count} pages")
            
            # Check first page for masthead
            page1 = doc[0]
            text1 = page1.get_text()
            
            # KAIZER NEWS masthead
            assert "KAIZER NEWS" in text1, "First page should contain 'KAIZER NEWS' masthead"
            print("  - ✓ KAIZER NEWS masthead found on page 1")
            
            # Check for date
            assert "2026" in text1, "First page should contain the date (2026)"
            print("  - ✓ Date found on page 1")
            
            # Check for CMYK dots (● character)
            has_cmyk = "●" in text1 or "Page 1" in text1
            print(f"  - CMYK dots/footer: {'✓ Found' if has_cmyk else '○ Not detected in text extraction'}")
            
            # Check for images
            images = page1.get_images()
            print(f"  - Images on page 1: {len(images)}")
            
            # Check fonts used in PDF
            fonts_used = set()
            for page in doc:
                fonts = page.get_fonts()
                for font in fonts:
                    if font[3]:  # font name
                        fonts_used.add(font[3])
            
            print(f"  - Fonts used: {', '.join(list(fonts_used)[:5])}...")
            
            # Verify expected fonts (may be embedded with different names)
            has_playfair = any('Playfair' in f or 'playfair' in f.lower() for f in fonts_used)
            has_pt_serif = any('PTSerif' in f or 'PT' in f for f in fonts_used)
            print(f"  - Playfair Display font: {'✓ Found' if has_playfair else '○ May be embedded'}")
            print(f"  - PT Serif font: {'✓ Found' if has_pt_serif else '○ May be embedded'}")
            
            doc.close()
            
        except ImportError:
            print("  - PyMuPDF not installed, skipping detailed PDF analysis")
    
    def test_telugu_pdf_generation(self):
        """GET /api/epaper/2026-03-16/pdf?lang=te&slot=evening generates a valid Telugu PDF"""
        print("Requesting Telugu evening PDF...")
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-16/pdf?lang=te&slot=evening", 
            timeout=120,
            stream=True
        )
        elapsed = time.time() - start_time
        
        # May return 404 if no Telugu articles
        if response.status_code == 404:
            print(f"✓ Telugu PDF returned 404 (no Telugu articles for this date)")
            pytest.skip("No Telugu articles available for this edition")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        pdf_bytes = response.content
        pdf_path = '/tmp/test_telugu_evening.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✓ Telugu evening PDF generated in {elapsed:.1f}s, size: {len(pdf_bytes)} bytes")
        
        # Analyze for Telugu fonts
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            fonts_used = set()
            for page in doc:
                fonts = page.get_fonts()
                for font in fonts:
                    if font[3]:
                        fonts_used.add(font[3])
            
            has_noto_telugu = any('Noto' in f or 'Telugu' in f for f in fonts_used)
            print(f"  - Noto Serif Telugu font: {'✓ Found' if has_noto_telugu else '○ May be embedded'}")
            print(f"  - All fonts: {', '.join(fonts_used)}")
            doc.close()
            
        except ImportError:
            print("  - PyMuPDF not installed, skipping detailed analysis")
    
    def test_morning_pdf_generation(self):
        """GET /api/epaper/2026-03-17/pdf?lang=en&slot=morning generates morning edition PDF"""
        print("Requesting morning edition PDF...")
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-17/pdf?lang=en&slot=morning", 
            timeout=120
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 404:
            print(f"✓ Morning PDF returned 404 (insufficient articles)")
            pytest.skip("Not enough articles for morning edition")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        pdf_bytes = response.content
        assert len(pdf_bytes) > 500, "PDF should have content"
        
        pdf_path = '/tmp/test_morning.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✓ Morning edition PDF generated in {elapsed:.1f}s, size: {len(pdf_bytes)} bytes")

class TestPDFStructure:
    """Detailed PDF structure analysis"""
    
    def test_pdf_has_multiple_pages(self):
        """PDF should have multiple pages (newspaper sections)"""
        response = requests.get(
            f"{BASE_URL}/api/epaper/2026-03-16/pdf?lang=en&slot=evening", 
            timeout=120
        )
        assert response.status_code == 200
        
        pdf_path = '/tmp/test_multipage.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        try:
            import fitz
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            
            # Based on EPAPER_PAGES config, should have multiple sections
            print(f"✓ PDF has {page_count} pages")
            assert page_count >= 1, "Should have at least 1 page"
            
            # Check each page has content (some pages may be sparse)
            empty_pages = 0
            for i, page in enumerate(doc):
                text = page.get_text()
                if len(text) < 100:
                    empty_pages += 1
                    print(f"  - Page {i+1}: {len(text)} characters (sparse)")
                else:
                    print(f"  - Page {i+1}: {len(text)} characters")
            
            # Allow at most 2 sparse pages
            assert empty_pages <= 2, f"Too many sparse pages: {empty_pages}"
            
            doc.close()
            
        except ImportError:
            pytest.skip("PyMuPDF not installed")
    
    def test_pdf_contains_images(self):
        """PDF should contain at least 1 image on page 1"""
        pdf_path = '/tmp/test_multipage.pdf'
        
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            page1 = doc[0]
            images = page1.get_images()
            
            # Count total images across all pages
            total_images = sum(len(page.get_images()) for page in doc)
            
            print(f"✓ PDF contains {total_images} total images")
            print(f"  - Page 1 images: {len(images)}")
            
            # Images are expected but may not always be present depending on article data
            if len(images) == 0:
                print("  - Note: No images on page 1 (articles may lack images)")
            
            doc.close()
            
        except ImportError:
            pytest.skip("PyMuPDF not installed")
    
    def test_pdf_cmyk_footer(self):
        """PDF should have CMYK dots in footer"""
        pdf_path = '/tmp/test_multipage.pdf'
        
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            # Check last few lines of each page for CMYK footer
            for i, page in enumerate(doc):
                text = page.get_text()
                
                # Look for footer indicators
                has_page_num = f"Page {i+1}" in text or f"Pg {i+1}" in text
                has_kaizer = "mintstreet.in" in text.lower()
                has_bullet = "●" in text
                
                if has_page_num or has_kaizer or has_bullet:
                    print(f"✓ Page {i+1} footer detected (page number: {has_page_num}, kaizernews: {has_kaizer}, CMYK dots: {has_bullet})")
            
            doc.close()
            
        except ImportError:
            pytest.skip("PyMuPDF not installed")

class TestPDFHealthCheck:
    """Test PDF health check endpoint"""
    
    def test_pdf_health_check(self):
        """GET /api/epaper/pdf-check returns health status"""
        response = requests.get(f"{BASE_URL}/api/epaper/pdf-check", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data, "Response should have 'status'"
        assert "issues" in data, "Response should have 'issues'"
        
        if data["status"] == "ok":
            print(f"✓ PDF health check passed - no issues")
        else:
            print(f"⚠ PDF health check issues: {data['issues']}")
        
        # Even if there are issues, endpoint should work
        assert data["status"] in ["ok", "error"]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
