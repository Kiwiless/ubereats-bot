"""
scraper.py — Récupère les infos d'une commande UberEats
via Playwright (navigateur headless) pour contourner le JS dynamique.
"""

import asyncio
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PWTimeout


# ══════════════════════════════════════════════
#  PATTERNS JSON embarqués dans la page UberEats
# ══════════════════════════════════════════════
PATTERNS = {
    "prenom": [
        r'"firstName"\s*:\s*"([^"]+)"',
        r'"name"\s*:\s*"([^"]+)"',
        r'"recipientName"\s*:\s*"([^"]+)"',
        r'"customerName"\s*:\s*"([^"]+)"',
    ],
    "heure": [
        r'"estimatedDeliveryTime"\s*:\s*(\d+)',
        r'"deliveryETA"\s*:\s*(\d+)',
        r'"eta"\s*:\s*(\d+)',
        r'"scheduledTime"\s*:\s*(\d+)',
        r'"arrivalTime"\s*:\s*"([^"]+)"',
    ],
    "code": [
        r'"pinCode"\s*:\s*"([^"]+)"',
        r'"confirmationCode"\s*:\s*"([^"]+)"',
        r'"deliveryCode"\s*:\s*"([^"]+)"',
        r'"verificationCode"\s*:\s*"([^"]+)"',
        r'"pickupCode"\s*:\s*"([^"]+)"',
        r'"orderCode"\s*:\s*"([^"]+)"',
    ],
    "statut": [
        r'"workflowUUID"\s*:\s*"([^"]+)"',
        r'"orderStatus"\s*:\s*"([^"]+)"',
        r'"status"\s*:\s*"([^"]+)"',
    ],
}

STATUS_MAP = {
    "pending":    "⏳ En attente",
    "accepted":   "✅ Acceptée par le restaurant",
    "preparing":  "🍳 En préparation",
    "pickup":     "🛵 En route vers toi",
    "delivering": "🛵 En route vers toi",
    "delivered":  "📦 Livrée",
    "cancelled":  "❌ Annulée",
    "completed":  "✅ Terminée",
}


def _extract(html: str, patterns: list[str]) -> str | None:
    for p in patterns:
        m = re.search(p, html)
        if m:
            return m.group(1)
    return None


def _format_timestamp(raw: str) -> str:
    """Convertit un timestamp Unix (ms ou s) en HH:MM."""
    try:
        ts = int(raw)
        if ts > 1_000_000_000_000:   # millisecondes
            ts //= 1000
        return datetime.fromtimestamp(ts).strftime("%H:%M")
    except Exception:
        return raw


def _parse_html(html: str) -> dict | None:
    prenom = _extract(html, PATTERNS["prenom"])
    heure_raw = _extract(html, PATTERNS["heure"])
    code = _extract(html, PATTERNS["code"])
    statut_raw = _extract(html, PATTERNS["statut"])

    heure = _format_timestamp(heure_raw) if heure_raw else None
    statut = STATUS_MAP.get((statut_raw or "").lower(), statut_raw)

    # Si on n'a RIEN du tout → probablement page de login
    if not prenom and not heure and not code:
        return None

    return {
        "prenom":  prenom  or "Non trouvé",
        "heure":   heure   or "Non trouvée",
        "code":    code    or "Non disponible",
        "statut":  statut  or "Inconnu",
    }


# ══════════════════════════════════════════════
#  SCRAPING AVEC PLAYWRIGHT (JS rendu côté client)
# ══════════════════════════════════════════════
async def _scrape_with_playwright(url: str) -> dict | None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = await browser.new_context(
            locale="fr-FR",
            timezone_id="Europe/Paris",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )

        page = await context.new_page()

        # Masquer la détection Playwright
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        try:
            await page.goto(url, wait_until="networkidle", timeout=30_000)
            # Laisser le JS s'exécuter
            await page.wait_for_timeout(3000)
        except PWTimeout:
            await page.wait_for_timeout(2000)  # Timeout partiel → on tente quand même

        html = await page.content()
        await browser.close()

    return _parse_html(html)


# ══════════════════════════════════════════════
#  POINT D'ENTRÉE PRINCIPAL
# ══════════════════════════════════════════════
async def fetch_order_info(url: str) -> dict | None:
    """
    Essaie de récupérer les infos de commande UberEats.
    Retourne un dict avec prenom, heure, code, statut — ou None si échec.
    """
    return await _scrape_with_playwright(url)
