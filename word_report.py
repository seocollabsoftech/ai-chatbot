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
    """Generates a Word document from the SEO audit data."""
    doc = Document()
    doc.add_heading(f"SEO Audit Report for: {report_data.get('URL', 'N/A')}", level=1)
    
    if "Error" in report_data:
        doc.add_paragraph(f"Audit failed: {report_data['Error']}")
        return doc
    
    doc.add_paragraph("This report provides a basic analysis of the website's on-page SEO factors.")
    doc.add_heading("On-Page Analysis", level=2)
    
    # Page Title
    doc.add_heading("Title Tag", level=3)
    doc.add_paragraph(f"Title: {report_data['Title']}")
    doc.add_paragraph(f"Length: {len(report_data['Title'])} characters" if isinstance(report_data['Title'], str) else "Length: 0 characters")
    
    # Meta Description
    doc.add_heading("Meta Description", level=3)
    doc.add_paragraph(f"Description: {report_data['Meta Description']}")
    doc.add_paragraph(f"Length: {len(report_data['Meta Description'])} characters" if isinstance(report_data['Meta Description'], str) else "Length: 0 characters")

    # H1 Headings
    doc.add_heading("H1 Headings", level=3)
    for h1 in report_data['H1 Headings']:
        doc.add_paragraph(f"- {h1}", style='List Bullet')

    # Images with Missing Alt Text
    doc.add_heading("Images", level=3)
    doc.add_paragraph(f"Total Images: {report_data['Total Images']}")
    doc.add_paragraph(f"Images without Alt Text: {len(report_data['Images without Alt Text'])}")
    if report_data['Images without Alt Text']:
        doc.add_paragraph("The following images are missing alt text:")
        for img in report_data['Images without Alt Text']:
            doc.add_paragraph(f"- {img}", style='List Bullet')
    
    return doc