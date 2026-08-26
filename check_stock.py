"""
Stock checker voor shop.action.com (Playwright-versie)
-------------------------------------------------------
Opent de productpagina met een echte (headless) browser, zodat we
dezelfde content zien als een normale bezoeker — inclusief content
die via JavaScript wordt ingevuld, en zonder dat we geraakt worden
door caching/detectie die alleen "kale" HTTP-requests treft.

Stuurt een gratis pushmelding via ntfy.sh zodra het product écht
besteld kan worden (dus niet bij een "beschikbaar vanaf datum X"-
aankondiging).

Vereisten: playwright (+ de chromium-browser, wordt geïnstalleerd
in de GitHub Actions workflow via 'playwright install chromium').
"""

import os
import re
import sys

import requests
from playwright.sync_api import sync_playwright

# --- Instellingen -----------------------------------------------------

PRODUCT_URL = "https://shop.action.com/nl-be/p/8720578232482/japandi-opbergboxspring-beige"

# Zet dit op iets uniek + geheim (bv. "jan-actionboxspring-9f3a2").
# Zelfde naam gebruik je in de ntfy-app om je te abonneren.
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "CHANGE-ME-uniek-topic-naam")

# Alle teksten die betekenen "je kan dit NU nog niet bestellen".
# Zolang een van deze teksten op de pagina staat, is het NIET
# echt op voorraad (ook een "beschikbaar vanaf ..." datum telt
# hier dus als nog-niet-beschikbaar).
NOT_AVAILABLE_PATTERNS = [
    r"tijdelijk uitverkocht",
    r"uitverkocht",
    r"beschikbaar vanaf",
    r"niet meer beschikbaar",
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def fetch_rendered_html() -> str:
    """Haalt de pagina op met een echte headless browser, zodat
    JavaScript volledig is uitgevoerd voor we de HTML uitlezen."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="nl-BE",
            timezone_id="Europe/Brussels",
        )
        page = context.new_page()
        page.goto(PRODUCT_URL, wait_until="networkidle", timeout=45000)
        # Extra korte wacht, voor het geval de status na de eerste
        # netwerkstilte nog client-side wordt bijgewerkt.
        page.wait_for_timeout(2000)
        # BELANGRIJK: we lezen hier de zichtbare tekst van de pagina
        # uit (zoals een bezoeker die ziet), NIET de ruwe HTML-bron.
        # De ruwe HTML bevat namelijk ook onzichtbare vertaal-JSON
        # (bv. "stock_level_sold_out":"Tijdelijk uitverkocht") die
        # altijd aanwezig is, los van de echte voorraadstatus. Door
        # alleen zichtbare tekst te gebruiken vermijden we valse
        # matches op die verborgen data.
        visible_text = page.inner_text("body")
        browser.close()
        return visible_text


def debug_print_status(visible_text: str) -> None:
    """Print wat het script zelf ziet, zodat je dit kan vergelijken
    met wat er op je eigen telefoon/browser te zien is."""
    text_lower = visible_text.lower()

    matched_any = False
    for pattern in NOT_AVAILABLE_PATTERNS:
        m = re.search(pattern, text_lower)
        if m:
            matched_any = True
            start = max(0, m.start() - 60)
            end = min(len(visible_text), m.end() + 60)
            snippet = " ".join(visible_text[start:end].split())
            print(f"[DEBUG] Match voor '{pattern}': ...{snippet}...")

    if not matched_any:
        print("[DEBUG] Geen van de NOT_AVAILABLE_PATTERNS gevonden in de zichtbare tekst.")


def is_in_stock(visible_text: str) -> bool:
    text_lower = visible_text.lower()
    for pattern in NOT_AVAILABLE_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    return True


def send_notification():
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data="De Japandi opbergboxspring (beige) is weer op voorraad bij Action! Snel bestellen.".encode(
            "utf-8"
        ),
        headers={
            "Title": "Weer op voorraad!".encode("utf-8"),
            "Click": PRODUCT_URL,
            "Priority": "urgent",
            "Tags": "bell,tada",
        },
        timeout=15,
    )


def main():
    try:
        visible_text = fetch_rendered_html()
        debug_print_status(visible_text)
        in_stock = is_in_stock(visible_text)
    except Exception as e:
        print(f"Fout bij checken van de pagina: {e}", file=sys.stderr)
        sys.exit(1)

    if in_stock:
        print("Product lijkt op voorraad -> melding versturen.")
        send_notification()
    else:
        print("Nog steeds niet (volledig) beschikbaar. Geen melding nodig.")


if __name__ == "__main__":
    main()
