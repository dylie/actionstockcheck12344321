# Stock checker – Japandi opbergboxspring (Action)

Dit stuurt automatisch een **gratis pushmelding op je telefoon** zodra
het product weer op voorraad is:
https://shop.action.com/nl-be/p/8720578232482/japandi-opbergboxspring-beige

Het draait volledig gratis in de cloud via GitHub Actions — je hoeft
zelf niets aan te laten staan.

## Stap 1 — Installeer de ntfy-app op je telefoon
- Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy
- iOS: https://apps.apple.com/us/app/ntfy/id1625396347

Bedenk een **uniek, geheim topic-naam**, bv. `jan-boxspring-9f3a2`
(niet iets algemeens als "stock", want dat is voor iedereen zichtbaar).
Open de app, tik op "+", en abonneer je op die naam.

## Stap 2 — Zet dit script op GitHub (gratis account volstaat)
1. Ga naar https://github.com/new en maak een **private** repository
   (bv. `action-stock-checker`).
2. Upload de bestanden uit deze map (`check_stock.py`, de map
   `.github/workflows/check-stock.yml`, en dit bestand) naar die repo.
   Kan via "Add file → Upload files" in de GitHub-website.
3. Ga in je repo naar **Settings → Secrets and variables → Actions →
   New repository secret**.
   - Name: `NTFY_TOPIC`
   - Value: het topic-naam dat je in Stap 1 koos, bv. `jan-boxspring-9f3a2`
4. Klaar. GitHub start de check nu automatisch elke 15 minuten.

## Testen
Ga naar het tabblad **Actions** in je repo → kies de workflow
"Check Action stock" → klik **Run workflow** om hem meteen één keer
te laten draaien en te zien of alles werkt (kijk bij de logs of er
geen foutmelding is).

## Stoppen
Verwijder de repo, of verwijder gewoon het bestand
`.github/workflows/check-stock.yml`.
