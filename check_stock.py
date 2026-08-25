"""
Stock checker voor shop.action.com
-----------------------------------
Checkt een productpagina op Action Webshop en stuurt een gratis
pushmelding via ntfy.sh zodra het product niet meer "Tijdelijk
uitverkocht" is.

Vereisten: alleen de 'requests' library (staat standaard bij GitHub
Actions al klaar via pip install in de workflow).
"""

import os
import re
import sys
import requests

# --- Instellingen -----------------------------------------------------

PRODUCT_URL = "https://shop.action.com/nl-be/p/8720578232482/japandi-opbergboxspring-beige"

# Zet dit op iets uniek + geheim (bv. "jan-actionboxspring-9f3a2").
# Zelfde naam gebruik je in de ntfy-app om je te abonneren.
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "CHANGE-ME-uniek-topic-naam")

# Tekst die op de pagina staat zolang het product NIET beschikbaar is.
SOLD_OUT_TEXT = "Tijdelijk uitverkocht"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def is_in_stock() -> bool:
    resp = requests.get(PRODUCT_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text
    # Als de "uitverkocht"-tekst NIET meer op de pagina staat,
    # gaan we ervan uit dat het product weer beschikbaar is.
    return SOLD_OUT_TEXT.lower() not in html.lower()


def send_notification():
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data="De Japandi opbergboxspring (beige) is weer op voorraad bij Action! Snel bestellen.".encode("utf-8"),
        headers={
            "Title": "Weer op voorraad! 🛏️",
            "Click": PRODUCT_URL,
            "Priority": "urgent",
            "Tags": "bell,tada",
        },
        timeout=15,
    )


def main():
    try:
        in_stock = is_in_stock()
    except Exception as e:
        print(f"Fout bij checken van de pagina: {e}", file=sys.stderr)
        sys.exit(1)

    if in_stock:
        print("Product lijkt op voorraad -> melding versturen.")
        send_notification()
    else:
        print("Nog steeds uitverkocht. Geen melding nodig.")


if __name__ == "__main__":
    main()
