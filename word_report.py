import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt
from io import BytesIO

# ------------------- SEO Audit -------------------

def perform_seo_audit(target_url: str) -> dict:
    if not target_url.startswith("http"):
        target_url = "https://" + target_url

    result = {"url": target_url}

    try:
        resp = requests.get(target_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        result["status_code"] = resp.status_code
    except Exception as e:
        return {"Error": f"Failed to fetch site: {e}"}

    # Title
    title_tag = soup.find("title")
    result["title"] = title_tag.get_text(strip=True) if title_tag else "❌ Missing"

    # Meta Description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    result["meta_description"] = meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else "❌ Missing"

    # Canonical URL
    canonical = soup.find("link", rel="canonical")
    result["canonical"] = canonical["href"] if canonical else "❌ Missing"

    # H1 / H2
    result["h1_tags"] = [h1.get_text(strip=True) for h1 in soup.find_all("h1")]
    result["h2_tags"] = [h2.get_text(strip=True) for h2 in soup.find_all("h2")]

    return result

# ------------------- AI Suggestions -------------------

def generate_ai_suggestion(ai_client, element_name: str, element_value: str) -> str:
    """
    Ask Gemini AI to generate Issue/Suggestion/Benefits for each SEO element
    """
    prompt = f"""
    Provide an SEO analysis for this {element_name}:

    Value: {element_value}

    Format your response as:
    Issue:
    Suggestion:
    Benefits for Users:
    """
    response = ai_client.send_message(prompt, stream=False)
    return response.text

# ------------------- Word Report -------------------

def create_word_report(audit_data: dict, output_file, ai_client=None):
    doc = Document()
    doc.add_heading("SEO Audit Report", 0)

    url = audit_data.get("url", "N/A")
    doc.add_paragraph(f"Target URL: {url}")
    doc.add_paragraph(f"Status Code: {audit_data.get('status_code', 'Unknown')}")

    # List of elements to analyze
    elements = {
        "Title Tag": audit_data.get("title", "❌ Missing"),
        "Meta Description": audit_data.get("meta_description", "❌ Missing"),
        "Canonical URL": audit_data.get("canonical", "❌ Missing"),
        "H1 Tags": ", ".join(audit_data.get("h1_tags", [])) or "❌ Missing",
        "H2 Tags": ", ".join(audit_data.get("h2_tags", [])) or "❌ Missing",
    }

    for name, value in elements.items():
        doc.add_heading(name, level=1)
        doc.add_paragraph(value)

        # If AI client is provided, generate suggestion
        if ai_client and value != "❌ Missing":
            try:
                suggestion_text = generate_ai_suggestion(ai_client, name, value)
                doc.add_paragraph(suggestion_text)
            except Exception as e:
                doc.add_paragraph(f"AI Suggestion could not be generated: {e}")

    # Save to file path or BytesIO
    if hasattr(output_file, "write"):
        doc.save(output_file)
    else:
        doc.save(str(output_file))
    return doc