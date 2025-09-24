"""
word_report.py
Automates SEO Site Checkup, scrapes the visible audit report, and writes a Word document.

Usage:
    python word_report.py https://example.com

Requirements:
    pip install selenium python-docx webdriver-manager

Notes:
 - Chrome is used by default via webdriver-manager (auto-downloads chromedriver).
 - The script attempts multiple input selectors to find the site entry box.
 - Run with a visible browser first (headless=False) to confirm selectors; switch to headless if desired.
 - Some detailed checks may require login / paid plan; the script captures the visible report sections.
"""

import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

from docx import Document
from docx.shared import Pt

# ---------- Configuration ----------
HEADLESS = False  # set True to run without opening the browser window
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 30
# -----------------------------------

def setup_driver(headless=HEADLESS):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    # optional: prevent images loading for speed
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                              options=chrome_options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver

def find_site_input(driver):
    """Try multiple selectors to find the main domain/url input on the homepage."""
    attempts = [
        (By.CSS_SELECTOR, 'input[name="url"]'),
        (By.CSS_SELECTOR, 'input[name="domain"]'),
        (By.CSS_SELECTOR, 'input[type="text"]'),
        (By.CSS_SELECTOR, 'input[placeholder*="Enter"]'),
        (By.CSS_SELECTOR, 'input[aria-label*="domain"]'),
    ]
    for by, sel in attempts:
        try:
            el = driver.find_element(by, sel)
            if el.is_displayed():
                return el
        except Exception:
            continue
    # fallback: try to find a big visible input in forms
    try:
        forms = driver.find_elements(By.TAG_NAME, "form")
        for f in forms:
            inputs = f.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                if i.is_displayed() and i.get_attribute("type") in ("text", "url"):
                    return i
    except Exception:
        pass
    return None

def click_check_button(driver):
    """Try to click the button that submits the check. Multiple selectors tried."""
    btn_selectors = [
        (By.CSS_SELECTOR, 'button[type="submit"]'),
        (By.CSS_SELECTOR, 'button[class*="check"]'),
        (By.XPATH, "//button[contains(., 'Check') or contains(., 'Analyze') or contains(., 'Start')]"),
        (By.CSS_SELECTOR, 'input[type="submit"]'),
    ]
    for by, sel in btn_selectors:
        try:
            btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((by, sel)))
            btn.click()
            return True
        except Exception:
            continue
    return False

def wait_for_results(driver):
    """Wait until some common result container appears."""
    possible = [
        (By.CSS_SELECTOR, ".result"),          # generic
        (By.CSS_SELECTOR, ".score"),           # score box
        (By.CSS_SELECTOR, ".report"),          # report container
        (By.CSS_SELECTOR, ".analysis"),        # analysis container
        (By.CSS_SELECTOR, ".checkup-results"), # possible class
        (By.XPATH, "//*[contains(@class,'seo')]"),
    ]
    for by, sel in possible:
        try:
            WebDriverWait(driver, EXPLICIT_WAIT).until(
                EC.presence_of_element_located((by, sel))
            )
            # give additional time for dynamic sections to load
            time.sleep(2)
            return True
        except Exception:
            continue
    return False

def collect_sections(driver):
    """
    Collect visible headings and their text content.
    Strategy:
     - find likely section containers (sections, articles, divs with headings)
     - for each, capture heading (h1-h4) and following text
    """
    sections = []
    # prioritize elements that typically hold reports
    candidates = driver.find_elements(By.XPATH, "//section | //article | //div[contains(@class,'section') or contains(@class,'issue') or contains(@class,'result') or contains(@class,'checkup')]")
    seen = set()
    for c in candidates:
        try:
            text = c.text.strip()
            if not text:
                continue
            # dedupe by short hash of first characters
            key = text[:200]
            if key in seen:
                continue
            seen.add(key)
            # try extract heading
            heading = ""
            for tag in ("h1","h2","h3","h4","strong"):
                try:
                    el = c.find_element(By.TAG_NAME, tag)
                    heading = el.text.strip()
                    if heading:
                        break
                except Exception:
                    continue
            # fallback heading from first line
            if not heading:
                heading = text.splitlines()[0][:80]
            sections.append({
                "heading": heading,
                "content": text
            })
        except Exception:
            continue
    # fallback: whole page text as one section
    if not sections:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        sections.append({"heading": "Full page text", "content": body_text.strip()[:20000]})
    return sections

def write_word_report(target, sections, output_path):
    doc = Document()
    doc.core_properties.title = f"SEO Audit Report - {target}"
    doc.core_properties.subject = "Automated SEO Site Checkup export"
    doc.add_heading(f"SEO Audit Report — {target}", level=1)
    doc.add_paragraph(f"Source: https://seositecheckup.com/ (automated capture)\n\n")
    for sec in sections:
        doc.add_heading(sec["heading"][:120], level=2)
        # split content into paragraphs by double newlines or single newlines
        for para in (p for p in sec["content"].splitlines() if p.strip()):
            p = doc.add_paragraph(para.strip())
            p.style.font.size = Pt(10)
    doc.save(output_path)
    return output_path

def normalize_target(t):
    if not t:
        raise ValueError("Missing target URL")
    if not t.startswith("http"):
        t = "https://" + t
    return t

def main():
    if len(sys.argv) < 2:
        print("Usage: python word_report.py <target-domain-or-url>")
        sys.exit(1)
    target = normalize_target(sys.argv[1])
    parsed = urlparse(target)
    shortname = parsed.netloc or parsed.path.strip("/").split("/")[0]
    outname = f"{shortname}_seo_audit.docx"
    outpath = Path.cwd() / outname

    driver = setup_driver()
    try:
        print("Opening seositecheckup.com ...")
        driver.get("https://seositecheckup.com/")
        time.sleep(2)

        # find input and submit
        input_el = find_site_input(driver)
        if not input_el:
            print("Could not find the site input on homepage; attempting to open tools page.")
            driver.get("https://seositecheckup.com/tools")
            time.sleep(2)
            input_el = find_site_input(driver)
        if not input_el:
            print("ERROR: Couldn't find a domain input box on the page. Try running the script with HEADLESS=False to inspect manually.")
            driver.quit()
            sys.exit(2)

        # clear and enter target
        input_el.clear()
        input_el.send_keys(target)
        time.sleep(0.5)
        # try submit via button click first
        if not click_check_button(driver):
            # fallback: press Enter in the input
            input_el.send_keys(Keys.ENTER)

        print("Submitted target, waiting for results...")
        if not wait_for_results(driver):
            print("Warning: could not detect results container automatically. Will try to collect whatever is visible.")
        else:
            print("Results appeared — collecting sections ...")

        sections = collect_sections(driver)
        print(f"Collected {len(sections)} sections. Writing Word file ...")
        saved = write_word_report(target, sections, str(outpath))
        print(f"Saved Word report to: {saved}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()