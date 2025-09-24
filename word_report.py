# word_report.py

import requests
from bs4 import BeautifulSoup
from docx import Document
from urllib.parse import urljoin
import os


def perform_seo_audit(url):
    """Fetches and analyzes a website's content for SEO elements."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Basic SEO ---
        title_tag = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]

        # --- Image Alt Audit ---
        all_images = soup.find_all('img')
        missing_alt_images = []
        for img in all_images:
            src = img.get('src', '')
            if not src:
                continue
            if not img.get('alt') or not img['alt'].strip():
                file_ext = os.path.splitext(src)[1].lower()
                missing_alt_images.append({
                    "src": urljoin(url, src),
                    "type": file_ext if file_ext else "Unknown"
                })

        # --- Social Meta ---
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        social_meta_present = bool(og_tags or twitter_tags)

        # --- Keywords ---
        all_text = soup.get_text(separator=' ').lower()
        words = [w for w in all_text.split() if len(w) > 3]
        common_keywords = {}
        for w in words:
            common_keywords[w] = common_keywords.get(w, 0) + 1
        sorted_keywords = sorted(common_keywords.items(), key=lambda x: x[1], reverse=True)[:10]

        # --- Analytics / Tracking ---
        analytics_present = "gtag(" in response.text or "google-analytics.com" in response.text

        # --- Other SEO Signals ---
        favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
        gsc_meta = soup.find("meta", attrs={"name": "google-site-verification"})
        final_url = response.url
        redirected = final_url != url
        https_used = url.startswith("https")
        structured_data = soup.find_all("script", type="application/ld+json")
        not_found_test = requests.get(urljoin(url, "/nonexistent-page-xyz"), timeout=10)
        custom_404 = not_found_test.status_code == 404
        robots_meta = soup.find("meta", attrs={"name": "robots"})
        noindex = "noindex" in robots_meta["content"].lower() if robots_meta and "content" in robots_meta.attrs else False
        nofollow = "nofollow" in robots_meta["content"].lower() if robots_meta and "content" in robots_meta.attrs else False

        return {
            "URL": url,
            "Final URL": final_url,
            "Redirected": redirected,
            "Title": title_tag.string.strip() if title_tag else "❌ Missing",
            "Title Length": len(title_tag.string.strip()) if title_tag else 0,
            "Meta Description": meta_description['content'].strip() if meta_description and 'content' in meta_description else "❌ Missing",
            "Meta Description Length": len(meta_description['content'].strip()) if meta_description and 'content' in meta_description else 0,
            "H1 Headings": h1_tags if h1_tags else ["❌ Missing"],
            "Missing Alt Images": missing_alt_images,
            "Total Images": len(all_images),
            "Social Meta Tags": "✅ Present" if social_meta_present else "❌ Missing",
            "Top Keywords": sorted_keywords,
            "Google Analytics": "✅ Found" if analytics_present else "❌ Missing",
            "Favicon": "✅ Present" if favicon else "❌ Missing",
            "Google Search Console": "✅ Verified" if gsc_meta else "❌ Missing",
            "HTTPS": "✅ Secure" if https_used else "❌ Not Secure",
            "Structured Data": "✅ Found" if structured_data else "❌ Missing",
            "Custom 404 Page": "✅ Exists" if custom_404 else "❌ Not Found",
            "Noindex Tag": "✅ Present" if noindex else "❌ Not Present",
            "Nofollow Tag": "✅ Present" if nofollow else "❌ Not Present",
        }

    except requests.exceptions.RequestException as e:
        return {"Error": f"Could not access the website: {e}"}


def create_word_report(report_data):
    """Creates a Word SEO audit report with professional tables and detailed sections."""
    doc = Document()
    doc.add_heading("📊 SEO Audit Report", 0)
    doc.add_paragraph(f"URL Analyzed: {report_data.get('URL', 'N/A')}")

    if "Error" in report_data:
        doc.add_paragraph(report_data["Error"])
        return doc

    # --- Meta Title Section ---
    doc.add_heading("1. Meta Title Audit", level=1)
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Light Grid Accent 1'
    table.cell(0, 0).text = "Title"
    table.cell(0, 1).text = report_data["Title"]
    table.cell(1, 0).text = "Length"
    table.cell(1, 1).text = f"{report_data['Title Length']} characters"
    table.cell(2, 0).text = "Issue"
    table.cell(2, 1).text = "❌ Missing or too short (<50 chars)" if report_data['Title Length'] < 50 else "✅ Looks Good"
    table.cell(3, 0).text = "Recommendation"
    table.cell(3, 1).text = "Keep title between 50-60 chars, include primary keywords, and ensure uniqueness."

    # --- Meta Description Section ---
    doc.add_heading("2. Meta Description Audit", level=1)
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Light Grid Accent 1'
    table.cell(0, 0).text = "Meta Description"
    table.cell(0, 1).text = report_data["Meta Description"]
    table.cell(1, 0).text = "Length"
    table.cell(1, 1).text = f"{report_data['Meta Description Length']} characters"
    table.cell(2, 0).text = "Issue"
    table.cell(2, 1).text = "❌ Missing or too short (<120 chars)" if report_data['Meta Description Length'] < 120 else "✅ Looks Good"
    table.cell(3, 0).text = "Recommendation"
    table.cell(3, 1).text = "Keep description between 140-160 chars, make it compelling and include keywords."

    # --- Missing Alt Text Section ---
    doc.add_heading("3. Missing Image Alt Text", level=1)
    missing_images = report_data["Missing Alt Images"]
    if missing_images:
        doc.add_paragraph(f"❌ Found {len(missing_images)} images missing alt text.")
        img_table = doc.add_table(rows=1, cols=3)
        img_table.style = 'Medium Shading 1 Accent 2'
        hdr = img_table.rows[0].cells
        hdr[0].text = "Image Path / URL"
        hdr[1].text = "File Type"
        hdr[2].text = "Recommendation"
        for img in missing_images:
            row = img_table.add_row().cells
            row[0].text = img["src"]
            row[1].text = img["type"].upper()
            row[2].text = "Add descriptive alt text."
    else:
        doc.add_paragraph("✅ All images have alt text.")

    # --- Advanced SEO Checks ---
    doc.add_heading("4. Advanced SEO Checks", level=1)
    checks = [
        ("Social Media Meta Tags", report_data["Social Meta Tags"], "Add OG/Twitter tags for better sharing."),
        ("Google Analytics", report_data["Google Analytics"], "Add GA tracking to monitor traffic."),
        ("Favicon", report_data["Favicon"], "Add favicon.ico for branding."),
        ("Google Search Console", report_data["Google Search Console"], "Verify property in GSC."),
        ("HTTPS / SSL", report_data["HTTPS"], "Use SSL certificate for trust and SEO."),
        ("Structured Data", report_data["Structured Data"], "Add schema markup."),
        ("Custom 404 Page", report_data["Custom 404 Page"], "Create branded 404 page."),
        ("Noindex Tag", report_data["Noindex Tag"], "Remove if indexing is needed."),
        ("Nofollow Tag", report_data["Nofollow Tag"], "Review nofollow usage."),
    ]

    adv_table = doc.add_table(rows=1, cols=3)
    adv_table.style = 'Medium Grid 1 Accent 1'
    hdr = adv_table.rows[0].cells
    hdr[0].text = "Check"
    hdr[1].text = "Status"
    hdr[2].text = "Recommendation"

    for check, status, rec in checks:
        row = adv_table.add_row().cells
        row[0].text = check
        row[1].text = status
        row[2].text = rec

    doc.add_paragraph("\n✅ End of Report")

    return doc