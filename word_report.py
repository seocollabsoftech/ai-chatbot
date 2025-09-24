# word_report.py

import requests
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Inches
from io import BytesIO

def perform_seo_audit(url):
    """Fetches and analyzes a website's content for basic SEO elements."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for bad HTTP status
        soup = BeautifulSoup(response.text, 'html.parser')

        # Collect SEO data
        title = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
        images_without_alt = [img['src'] for img in soup.find_all('img') if 'alt' not in img or not img['alt'].strip()]

        report = {
            "URL": url,
            "Title": title.string.strip() if title else "❌ Missing",
            "Meta Description": meta_description['content'].strip() if meta_description and 'content' in meta_description else "❌ Missing",
            "H1 Headings": h1_tags if h1_tags else ["❌ Missing"],
            "Images without Alt Text": images_without_alt,
            "Total Images": len(soup.find_all('img')),
        }
        return report

    except requests.exceptions.RequestException as e:
        return {"Error": f"Could not access the website: {e}"}

def create_word_report(report_data):
    """Generates a Word document from the SEO audit data, matching the provided structure."""
    doc = Document()
    doc.add_heading(f"Website Audit Report for: {report_data.get('URL', 'N/A')}", level=0)
    
    if "Error" in report_data:
        doc.add_paragraph(f"Audit failed: {report_data['Error']}")
        return doc
    
    # --- 1. SEO Section ---
    doc.add_heading("1. SEO", level=1)

    # 1.1 Improper Meta Title and Description
    doc.add_heading("1.1 Improper Meta Title and Description", level=2)
    doc.add_paragraph(f"**Title:** {report_data['Title']}")
    doc.add_paragraph(f"**Description:** {report_data['Meta Description']}")
    doc.add_paragraph("Issue: Your site has an improper meta title and description.")
    doc.add_paragraph("Recommendation: Create unique and descriptive titles and meta descriptions for each page, keeping them within recommended character limits.")

    # 1.2 Missing Image Alt Tags
    doc.add_heading("1.2 Missing Image Alt Tags", level=2)
    images_without_alt = report_data['Images without Alt Text']
    if images_without_alt:
        doc.add_paragraph(f"Found {len(images_without_alt)} images with missing alt text.")
        doc.add_paragraph("The following images are missing alt text:")
        for img in images_without_alt:
            doc.add_paragraph(f"- {img}", style='List Bullet')
    else:
        doc.add_paragraph("✅ All images found have alt text.")
    doc.add_paragraph("Recommendation: Add descriptive alt attributes to all images for improved accessibility and SEO.")
    
    # 1.3 Multiple H1 Found
    doc.add_heading("1.3 Multiple H1 Found", level=2)
    h1_tags = report_data['H1 Headings']
    if len(h1_tags) > 1:
        doc.add_paragraph(f"Found {len(h1_tags)} H1 tags:")
        for h1 in h1_tags:
            doc.add_paragraph(f"- {h1}", style='List Bullet')
        doc.add_paragraph("Issue: Multiple H1 tags can confuse search engines about the page's main topic.")
        doc.add_paragraph("Recommendation: Ensure each page has only one H1 tag that accurately represents the primary content.")
    elif len(h1_tags) == 1:
        doc.add_paragraph(f"✅ Found a single H1 tag: {h1_tags[0]}")
    else:
        doc.add_paragraph("❌ No H1 tags found.")
        doc.add_paragraph("Issue: Missing H1 tags can negatively impact on-page SEO.")
        doc.add_paragraph("Recommendation: Add a single H1 tag that clearly defines the page's main topic.")

    # --- 2. Competitor Analysis ---
    doc.add_heading("2. Competitor Analysis", level=1)
    doc.add_paragraph("This section would include detailed competitor information and analysis.")

    # --- 3. Local SEO ---
    doc.add_heading("3. Local SEO", level=1)
    doc.add_paragraph("This section would detail local search engine optimization efforts.")

    # --- 4. UI/UX Suggestions ---
    doc.add_heading("4. UI/UX Suggestions", level=1)
    doc.add_paragraph("This section would include recommendations for improving the user interface and user experience.")

    return doc