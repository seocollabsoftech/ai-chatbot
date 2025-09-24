# word_report.py

import requests
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Inches, Pt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from io import BytesIO

def perform_seo_audit(url):
    """Fetches and analyzes a website's content for SEO elements."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
        images_without_alt = [img['src'] for img in soup.find_all('img') if not img.get('alt')]
        
        # Additional basic checks
        seo_data = {
            "URL": url,
            "Meta Title": title.string.strip() if title else "❌ Missing",
            "Meta Description": meta_description['content'].strip() if meta_description and meta_description.get('content') else "❌ Missing",
            "H1 Headings": h1_tags if h1_tags else ["❌ Missing"],
            "Images without Alt Text": images_without_alt,
            "Total Images": len(soup.find_all('img')),
            "Social Media Tags": [tag.get('property') or tag.get('name') for tag in soup.find_all('meta') if 'og:' in (tag.get('property') or '') or 'twitter:' in (tag.get('name') or '')],
            "Most Common Keywords": [word for word in soup.get_text().split() if len(word) > 4][:10],  # Example
            "Google Analytics": "Found" if soup.find('script', src=lambda x: x and 'gtag' in x) else "Not Found",
            "Favicon": soup.find('link', rel='icon')['href'] if soup.find('link', rel='icon') else "Not Found",
            "SSL": "https" in url,
            "Custom 404 Page": "Check manually",
            "Noindex Tag": bool(soup.find('meta', attrs={'name':'robots', 'content':'noindex'})),
            "Nofollow Tag": bool(soup.find('meta', attrs={'name':'robots', 'content':'nofollow'})),
        }

        return seo_data

    except requests.exceptions.RequestException as e:
        return {"Error": f"Could not access the website: {e}"}

def capture_screenshot(url):
    """Capture full page screenshot using headless Chrome."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(2)  # Wait for page to load
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    return screenshot

def create_word_report(report_data):
    """Generates a Word document from SEO audit data."""
    doc = Document()
    doc.add_heading(f"SEO Audit Report - {report_data.get('URL','N/A')}", level=0)
    
    if "Error" in report_data:
        doc.add_paragraph(report_data["Error"])
        return doc

    # Add Screenshot
    try:
        screenshot_bytes = capture_screenshot(report_data['URL'])
        screenshot_stream = BytesIO(screenshot_bytes)
        doc.add_heading("Website Screenshot", level=1)
        doc.add_picture(screenshot_stream, width=Inches(6))
    except Exception as e:
        doc.add_paragraph(f"Screenshot not captured: {e}")

    # Meta Title & Description
    doc.add_heading("1. Meta Information", level=1)
    table = doc.add_table(rows=3, cols=2)
    table.style = 'Table Grid'
    table.cell(0,0).text = "Parameter"
    table.cell(0,1).text = "Value"
    table.cell(1,0).text = "Meta Title"
    table.cell(1,1).text = report_data.get("Meta Title", "")
    table.cell(2,0).text = "Meta Description"
    table.cell(2,1).text = report_data.get("Meta Description", "")

    # H1 Tags
    doc.add_heading("2. H1 Headings", level=1)
    if report_data['H1 Headings']:
        for h in report_data['H1 Headings']:
            doc.add_paragraph(f"- {h}")

    # Missing Alt Text Images
    doc.add_heading("3. Images without Alt Text", level=1)
    if report_data['Images without Alt Text']:
        for img in report_data['Images without Alt Text']:
            doc.add_paragraph(f"- {img}")
    else:
        doc.add_paragraph("✅ All images have alt text.")

    # Additional SEO Checks
    doc.add_heading("4. Additional SEO Checks", level=1)
    for key in ["Social Media Tags","Most Common Keywords","Google Analytics","Favicon","SSL","Custom 404 Page","Noindex Tag","Nofollow Tag"]:
        doc.add_paragraph(f"{key}: {report_data.get(key, 'N/A')}")

    return doc