"""
word_report.py
Lightweight SEO audit script that fetches basic on-page SEO data and exports it as a Word document.
✅ Compatible with Streamlit Cloud (no Selenium/browser required)
"""

import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt
from pathlib import Path

# ------------------- Core Audit Logic -------------------

def perform_seo_audit(target_url: str) -> dict:
    """Fetch the HTML and collect SEO data into a dictionary."""

    # Normalize URL
    if not target_url.startswith("http"):
        target_url = "https://" + target_url

    result = {"url": target_url}

    # Fetch HTML
    try:
        resp = requests.get(target_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        result["status_code"] = resp.status_code
    except Exception as e:
        return {"Error": f"Failed to fetch site: {e}"}

    # Title Tag
    title_tag = soup.find("title")
    result["title"] = title_tag.get_text(strip=True) if title_tag else "❌ Missing"

    # Meta Description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    result["meta_description"] = meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else "❌ Missing"

    # Meta Keywords
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    result["meta_keywords"] = meta_keywords["content"].strip() if meta_keywords and "content" in meta_keywords.attrs else "❌ Missing"

    # Canonical URL
    canonical = soup.find("link", rel="canonical")
    result["canonical"] = canonical["href"] if canonical else "❌ Missing"

    # H1 / H2 Tags
    result["h1_tags"] = [h1.get_text(strip=True) for h1 in soup.find_all("h1")]
    result["h2_tags"] = [h2.get_text(strip=True) for h2 in soup.find_all("h2")]

    # Image ALT attributes
    images = soup.find_all("img")
    alt_missing = [img.get("src") for img in images if not img.get("alt")]
    result["total_images"] = len(images)
    result["missing_alt_count"] = len(alt_missing)
    result["missing_alt_images"] = alt_missing[:10]  # show first 10

    # Robots.txt check
    parsed = urlparse(target_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        robots_resp = requests.get(robots_url, timeout=10)
        result["robots_status"] = "✅ Found" if robots_resp.status_code == 200 else "❌ Not Found"
    except:
        result["robots_status"] = "❌ Not Found"

    # Sitemap.xml check
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    try:
        sitemap_resp = requests.get(sitemap_url, timeout=10)
        result["sitemap_status"] = "✅ Found" if sitemap_resp.status_code == 200 else "❌ Not Found"
    except:
        result["sitemap_status"] = "❌ Not Found"

    return result

# ------------------- Word Report Generator -------------------

def create_word_report(audit_data: dict, output_file):
    """
    Create a Word SEO report from the collected data.
    output_file can be a file path (str/Path) or a BytesIO object
    """
    doc = Document()
    doc.add_heading("SEO Audit Report", 0)

    url = audit_data.get("url", "N/A")
    doc.add_paragraph(f"Target URL: {url}")
    doc.add_paragraph(f"Status Code: {audit_data.get('status_code', 'Unknown')}")

    # Title
    doc.add_heading("1. Title Tag", level=1)
    doc.add_paragraph(audit_data.get("title", "❌ Missing"))

    # Meta Description
    doc.add_heading("2. Meta Description", level=1)
    doc.add_paragraph(audit_data.get("meta_description", "❌ Missing"))

    # Meta Keywords
    doc.add_heading("3. Meta Keywords", level=1)
    doc.add_paragraph(audit_data.get("meta_keywords", "❌ Missing"))

    # Canonical URL
    doc.add_heading("4. Canonical URL", level=1)
    doc.add_paragraph(audit_data.get("canonical", "❌ Missing"))

    # H1 / H2
    doc.add_heading("5. Heading Tags", level=1)
    doc.add_paragraph("H1 Tags:")
    for h1 in audit_data.get("h1_tags", []):
        doc.add_paragraph(f" - {h1}")
    doc.add_paragraph("H2 Tags:")
    for h2 in audit_data.get("h2_tags", []):
        doc.add_paragraph(f" - {h2}")

    # Image ALT attributes
    doc.add_heading("6. Image ALT Attributes", level=1)
    total_images = audit_data.get("total_images", 0)
    missing_alt = audit_data.get("missing_alt_count", 0)
    doc.add_paragraph(f"Total Images: {total_images}")
    doc.add_paragraph(f"Images Missing ALT: {missing_alt}")
    if missing_alt > 0:
        doc.add_paragraph("Examples:")
        for img in audit_data.get("missing_alt_images", []):
            doc.add_paragraph(f" - {img}")

    # Robots.txt & Sitemap
    doc.add_heading("7. Robots.txt & Sitemap", level=1)
    doc.add_paragraph(f"Robots.txt: {audit_data.get('robots_status')}")
    doc.add_paragraph(f"Sitemap.xml: {audit_data.get('sitemap_status')}")

    # Save document
    if hasattr(output_file, "write"):  # BytesIO
        doc.save(output_file)
    else:  # path
        doc.save(str(output_file))
    return doc