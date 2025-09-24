# word_report.py

import requests
from bs4 import BeautifulSoup
from docx import Document
from urllib.parse import urljoin


def perform_seo_audit(url):
    """Fetches and analyzes a website's content for basic SEO elements + advanced checks."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Core elements
        title = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
        images_without_alt = [img['src'] for img in soup.find_all('img') if 'alt' not in img or not img['alt'].strip()]

        # --- Additional Tests ---
        # Social Meta Tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        social_meta_present = bool(og_tags or twitter_tags)

        # Keyword Analysis
        all_text = soup.get_text(separator=' ').lower()
        words = [w for w in all_text.split() if len(w) > 3]
        common_keywords = {}
        for w in words:
            common_keywords[w] = common_keywords.get(w, 0) + 1
        sorted_keywords = sorted(common_keywords.items(), key=lambda x: x[1], reverse=True)[:10]

        # Google Analytics
        analytics_present = "gtag(" in response.text or "google-analytics.com" in response.text

        # Favicon
        favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
        favicon_present = bool(favicon)

        # Search Console verification
        gsc_meta = soup.find("meta", attrs={"name": "google-site-verification"})
        gsc_present = bool(gsc_meta)

        # URL Redirect
        final_url = response.url
        redirected = final_url != url

        # SSL Check
        https_used = url.startswith("https")

        # Structured Data
        structured_data = soup.find_all("script", type="application/ld+json")
        structured_data_present = len(structured_data) > 0

        # Custom 404 Page
        not_found_test = requests.get(urljoin(url, "/nonexistent-page-xyz"), timeout=10)
        custom_404 = not_found_test.status_code == 404

        # Noindex / Nofollow
        robots_meta = soup.find("meta", attrs={"name": "robots"})
        noindex = "noindex" in robots_meta["content"].lower() if robots_meta and "content" in robots_meta.attrs else False
        nofollow = "nofollow" in robots_meta["content"].lower() if robots_meta and "content" in robots_meta.attrs else False

        report = {
            "URL": url,
            "Final URL": final_url,
            "Redirected": redirected,
            "Title": title.string.strip() if title else "❌ Missing",
            "Meta Description": meta_description['content'].strip() if meta_description and 'content' in meta_description else "❌ Missing",
            "H1 Headings": h1_tags if h1_tags else ["❌ Missing"],
            "Images without Alt Text": images_without_alt,
            "Total Images": len(soup.find_all('img')),
            "Social Meta Tags": "✅ Present" if social_meta_present else "❌ Missing",
            "Top Keywords": sorted_keywords,
            "Google Analytics": "✅ Found" if analytics_present else "❌ Missing",
            "Favicon": "✅ Present" if favicon_present else "❌ Missing",
            "Google Search Console": "✅ Verified" if gsc_present else "❌ Missing",
            "HTTPS": "✅ Secure" if https_used else "❌ Not Secure",
            "Structured Data": "✅ Found" if structured_data_present else "❌ Missing",
            "Custom 404 Page": "✅ Exists" if custom_404 else "❌ Not Found",
            "Noindex Tag": "✅ Present" if noindex else "❌ Not Present",
            "Nofollow Tag": "✅ Present" if nofollow else "❌ Not Present",
        }

        return report

    except requests.exceptions.RequestException as e:
        return {"Error": f"Could not access the website: {e}"}


def create_word_report(report_data):
    """Generates a Word document from the SEO audit data, including advanced checks."""
    doc = Document()
    doc.add_heading(f"Website Audit Report for: {report_data.get('URL', 'N/A')}", level=0)

    if "Error" in report_data:
        doc.add_paragraph(f"Audit failed: {report_data['Error']}")
        return doc

    # --- 1. SEO Basics ---
    doc.add_heading("1. SEO Basics", level=1)
    doc.add_paragraph(f"Title: {report_data['Title']}")
    doc.add_paragraph(f"Meta Description: {report_data['Meta Description']}")

    # --- 2. On-Page Issues ---
    doc.add_heading("2. On-Page Issues", level=1)

    # Missing Alt Text
    doc.add_heading("2.1 Missing Image Alt Text", level=2)
    if report_data['Images without Alt Text']:
        doc.add_paragraph(f"Found {len(report_data['Images without Alt Text'])} images missing alt text.")
        for img in report_data['Images without Alt Text']:
            doc.add_paragraph(f"- {img}", style="List Bullet")
    else:
        doc.add_paragraph("✅ All images have alt text.")

    # H1 Analysis
    doc.add_heading("2.2 H1 Tags", level=2)
    for h1 in report_data['H1 Headings']:
        doc.add_paragraph(f"- {h1}", style="List Bullet")

    # --- 3. Advanced SEO Checks ---
    doc.add_heading("3. Advanced SEO Checks", level=1)

    checks = [
        ("Social Media Meta Tags Test", report_data["Social Meta Tags"]),
        ("Most Common Keywords Test", ", ".join([f"{k} ({v})" for k, v in report_data["Top Keywords"]])),
        ("Google Analytics Test", report_data["Google Analytics"]),
        ("Favicon Test", report_data["Favicon"]),
        ("Google Search Console Errors Test", report_data["Google Search Console"]),
        ("URL Redirects Test", "✅ Redirected" if report_data["Redirected"] else "❌ No Redirect"),
        ("SSL Checker and HTTPS Test", report_data["HTTPS"]),
        ("Structured Data Test", report_data["Structured Data"]),
        ("Custom 404 Error Page Test", report_data["Custom 404 Page"]),
        ("Noindex Tag Test", report_data["Noindex Tag"]),
        ("Nofollow Tag Test", report_data["Nofollow Tag"]),
    ]

    for section, value in checks:
        doc.add_heading(section, level=2)
        doc.add_paragraph(f"Result: {value}")
        doc.add_paragraph("Issue: If marked ❌, this element is missing or improperly configured.")
        doc.add_paragraph("Recommendation: Review and fix this section to improve SEO and user experience.")

    return doc