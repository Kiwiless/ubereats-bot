import re
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

PATTERNS = {
    "prenom": [
        r'"firstName"\s*:\s*"([^"]+)"',
        r'"recipientName"\s*:\s*"([^"]+)"',
        r'"customerName"\s*:\s*"([^"]+)"',
        r'"eaterName"\s*:\s*"([^"]+)"',
    ],
    "heure": [
        r'"estimatedDeliveryTime"\s*:\s*(\d+)',
        r'"deliveryETA"\s*:\s*(\d+)',
        r'"eta"\s*:\s*(\d+)',
        r'"scheduledTime"\s*:\s*(\d+)',
    ],
    "code": [
        r'"pinCode"\s*:\s*"([^"]+)"',
        r'"confirmationCode"\s*:\s*"([^"]+)"',
        r'"deliveryCode"\s*:\s*"([^"]+)"',
        r'"verificationCode"\s*:\s*"([^"]+)"',
        r'"handoffCode"\s*:\s*"([^"]+)"',
    ],
    "statut": [
        r'"orderStatus"\s*:\s*"([^"]+)"',
        r'"status"\s*:\s*"([^"]+)"',
    ],
}

STATUS_MAP = {
    "pending":    "⏳ En attente",
    "accepted":   "✅ Acceptée",
    "preparing":  "🍳 En préparation",
    "delivering": "🛵 En route vers toi",
    "delivered":  "📦 Livrée",
    "cancelled":  "❌ Annulée",
}

def _extract(text, patterns):
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return None

def _format_ts(raw):
    try:
        ts = int(raw)
        if ts > 1_000_000_000_000:
            ts //= 1000
        return datetime.fromtimestamp(ts).strftime("%H:%M")
    except:
        return raw

async def fetch_order_info(url: str) -> dict | None:
    captured = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = await browser.new_context(
            locale="fr-FR",
            timezone_id="Europe/Paris",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )

        page = await context.new_page()

        # ── Intercepter les réponses API UberEats (JSON brut) ──
        async def handle_response(response):
            if "ubereats.com" in response.url and response.status == 200:
                ct = response.headers.get("content-type", "")
                if "json" in ct:
                    try:
                        body = await response.text()
                        captured.append(body)
                    except:
                        pass

        page.on("response", handle_response)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await page.wait_for_timeout(5000)
        except PWTimeout:
            await page.wait_for_timeout(2000)

        html = await page.content()
        await browser.close()

    # ── Chercher dans les réponses API interceptées EN PREMIER ──
    all_text = "\n".join(captured) + "\n" + html

    prenom   = _extract(all_text, PATTERNS["prenom"])
    heure_r  = _extract(all_text, PATTERNS["heure"])
    code     = _extract(all_text, PATTERNS["code"])
    statut_r = _extract(all_text, PATTERNS["statut"])

    if not prenom and not heure_r and not code:
        return None

    return {
        "prenom": prenom or "Non trouvé",
        "heure":  _format_ts(heure_r) if heure_r else "Non trouvée",
        "code":   code or "Non disponible",
        "statut": STATUS_MAP.get((statut_r or "").lower(), statut_r or "Inconnu"),
    }
