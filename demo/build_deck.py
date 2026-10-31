"""Render every demo/sample_deck*.html to a PDF of the same name with headless Chromium.

The PDFs keep a real text layer, so deck.py works with or without vision.
Run: .venv/Scripts/python demo/build_deck.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    for html in sorted(HERE.glob("sample_deck*.html")):
        pdf = html.with_suffix(".pdf")
        page.goto(html.resolve().as_uri())
        page.pdf(path=str(pdf), width="13.333in", height="7.5in", print_background=True)
        print(pdf)
    browser.close()
