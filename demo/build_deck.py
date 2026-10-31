"""Render demo/sample_deck.html to demo/sample_deck.pdf with headless Chromium.

The PDF keeps a real text layer, so deck.py works with or without vision.
Run: .venv/Scripts/python demo/build_deck.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto((HERE / "sample_deck.html").resolve().as_uri())
    page.pdf(path=str(HERE / "sample_deck.pdf"), width="13.333in", height="7.5in", print_background=True)
    browser.close()
print(HERE / "sample_deck.pdf")
