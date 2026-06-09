import aiohttp
import re
from datetime import datetime

PATTERNS = {
    "prenom": [
        r'"firstName"\s*:\s*"([^"]+)"',
        r'"recipientName"\s*:\s*"([^"]+)"',
        r'"customerName"\s*:\s*"([^"]+)"',
        r'"name"\s*:\s*"([^"]+)"',
    ],
    "heure": [
        r'"estimatedDeliveryTime"\s*:\s*(\d+)',
        r'"deliveryETA"\s*:\s*(\d+)',
        r'"eta"\s*:\s*(\d+)',
    ],
    "code": [
        r'"pinCode"\s*:\s*"([^"]+)"',
        r'"confirmationCode"\s*:\s*"([^"]+)"',
        r'"deliveryCode"\s*:\s*"([^"]+)"',
        r'"verificationCode"\s*:\s*"([^"]+)"',
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

def _extract(html, patterns):
    for p in patterns:
        m = re.search(p, html)
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()

    prenom  = _extract(html, PATTERNS["prenom"])
    heure_r = _extract(html, PATTERNS["heure"])
    code    = _extract(html, PATTERNS["code"])
    statut_r= _extract(html, PATTERNS["statut"])

    if not prenom and not heure_r and not code:
        return None

    return {
        "prenom": prenom  or "Non trouvé",
        "heure":  _format_ts(heure_r) if heure_r else "Non trouvée",
        "code":   code    or "Non disponible",
        "statut": STATUS_MAP.get((statut_r or "").lower(), statut_r or "Inconnu"),
    }
