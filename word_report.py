# word_report.py

import requests
from bs4 import BeautifulSoup
from docx import Document
from urllib.parse import urljoin


def perform_seo_audit(url):
    """Fetches and analyzes a website's content for basic and advanced SEO elements."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Core elements
        title = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
        images_without_alt = [img['src'] for img in soup.find_all('img') if 'alt' not in img or not img['alt'].strip()]

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

        # Google Search Console
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

        # Custom 404
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
    """Generates a Word document with well-structured tables for SEO audit data."""
    doc = Document()
    doc.add_heading(f"Website SEO Audit Report", level=0)
    doc.add_paragraph(f"URL Analyzed: {report_data.get('URL', 'N/A')}")

    if "Error" in report_data:
        doc.add_paragraph(f"Audit failed: {report_data['Error']}")
        return doc

    # 1. Basic SEO Info
    doc.add_heading("1. Basic SEO Information", level=1)
    table = doc.add_table(rows=3, cols=2)
    table.style = 'Light List Accent 1'
    table.cell(0, 0).text = "Title"
    table.cell(0, 1).text = report_data['Title']
    table.cell(1, 0).text = "Meta Description"
    table.cell(1, 1).text = report_data['Meta Description']
    table.cell(2, 0).text = "Total Images"
    table.cell(2, 1).text = str(report_data['Total Images'])

    # 2. On-Page Issues
    doc.add_heading("2. On-Page SEO Issues", level=1)
    doc.add_paragraph("H1 Tags Found:")
    for h1 in report_data['H1 Headings']:
        doc.add_paragraph(f"- {h1}", style="List Bullet")

    if report_data['Images without Alt Text']:
        doc.add_paragraph(f"{len(report_data['Images without Alt Text'])} images are missing alt text.")
    else:
        doc.add_paragraph("✅ All images have alt text.")

    # 3. Advanced Checks Table
    doc.add_heading("3. Advanced SEO Checks", level=1)
    checks = [
        ("Social Media Meta Tags Test", report_data["Social Meta Tags"], "Missing social tags reduce social sharing previews.", "Add Open Graph & Twitter meta tags."),
        ("Most Common Keywords Test", ", ".join([f"{k} ({v})" for k, v in report_data["Top Keywords"]]), "Unoptimized keywords affect visibility.", "Optimize content with primary keywords."),
        ("Google Analytics Test", report_data["Google Analytics"], "No analytics means lost tracking data.", "Add Google Analytics tracking script."),
        ("Favicon Test", report_data["Favicon"], "Missing favicon affects branding.", "Add a favicon.ico file."),
        ("Google Search Console Errors Test", report_data["Google Search Console"], "Not verified on GSC.", "Verify property in Google Search Console."),
        ("URL Redirects Test", "✅ Redirected" if report_data["Redirected"] else "❌ No Redirect", "Redirects ensure canonical URLs.", "Ensure all versions redirect to the main domain."),
        ("SSL Checker and HTTPS Test", report_data["HTTPS"], "HTTP pages are insecure.", "Use HTTPS with a valid SSL certificate."),
        ("Structured Data Test", report_data["Structured Data"], "Lack of structured data reduces rich results.", "Add schema.org structured data."),
        ("Custom 404 Error Page Test", report_data["Custom 404 Page"], "No custom 404 hurts UX.", "Create a branded 404 error page."),
        ("Noindex Tag Test", report_data["Noindex Tag"], "Pages might be hidden from search.", "Remove noindex if indexing is desired."),
        ("Nofollow Tag Test", report_data["Nofollow Tag"], "Affects link equity flow.", "Use nofollow only when necessary."),
    ]

    table = doc.add_table(rows=1, cols=4)
    table.style = 'Medium Grid 2 Accent 1'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Check Name"
    hdr_cells[1].text = "Status / Result"
    hdr_cells[2].text = "Issue"
    hdr_cells[3].text = "Recommendation"

    for check_name, status, issue, recommendation in checks:
        row_cells = table.add_row().cells
        row_cells[0].text = check_name
        row_cells[1].text = status
        row_cells[2].text = issue
        row_cells[3].text = recommendation

    doc.add_paragraph("\n✅ End of Report\n")

    return doc