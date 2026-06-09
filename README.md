# 🛵 UberEats Discord Bot

Bot Discord qui récupère les infos d'une commande UberEats via `/url`.

---

## 📋 Fonctionnalités

- **`/url [lien]`** → Affiche :
  - 👤 Prénom de la commande
  - 🕐 Heure d'arrivée estimée
  - 🔑 Code à donner au livreur
  - 📦 Statut de la commande

---

## 🚀 Installation locale

### 1. Prérequis
- Python 3.10+
- pip

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
```

### 3. Configurer le token
Crée un fichier `.env` ou modifie directement `bot.py` :
```
DISCORD_TOKEN=ton_token_discord_ici
```

Ou lance avec une variable d'environnement :
```bash
DISCORD_TOKEN=xxxxx python bot.py
```

### 4. Lancer
```bash
python bot.py
```

---

## ☁️ Hébergement 24/7 sur Railway (GRATUIT)

> Railway offre 5$ de crédit gratuit/mois, suffisant pour un petit bot.

### Étapes :
1. Crée un compte sur [railway.app](https://railway.app)
2. Clique **"New Project"** → **"Deploy from GitHub"**
3. Upload ou connecte ce dossier
4. Dans **Variables** du projet, ajoute :
   ```
   DISCORD_TOKEN = ton_token_discord
   ```
5. Railway détecte le `Dockerfile` automatiquement et déploie 🎉

---

## ☁️ Alternative : Render.com (GRATUIT)

1. Compte sur [render.com](https://render.com)
2. **New** → **Web Service** → connecte GitHub
3. Environnement : **Docker**
4. Variable d'env : `DISCORD_TOKEN = xxx`
5. **Deploy**

> ⚠️ Sur Render gratuit, le service "dort" après 15 min d'inactivité.
> Pour éviter ça, passe en plan Starter (7$/mois) ou utilise Railway.

---

## 🐳 Docker (auto-hébergé)

```bash
# Build
docker build -t ubereats-bot .

# Run
docker run -e DISCORD_TOKEN=ton_token -d ubereats-bot
```

---

## 🔑 Créer un token Discord

1. Va sur [discord.com/developers/applications](https://discord.com/developers/applications)
2. **New Application** → donne un nom
3. Onglet **Bot** → **Reset Token** → copie le token
4. Active **"Message Content Intent"** si besoin
5. Onglet **OAuth2** → **URL Generator** :
   - Scopes : `bot`, `applications.commands`
   - Permissions : `Send Messages`, `Use Slash Commands`, `Embed Links`
6. Copie l'URL générée et ajoute le bot à ton serveur

---

## ⚠️ Limitations UberEats

UberEats charge ses pages en JavaScript dynamique.
Le bot utilise **Playwright (Chromium headless)** pour simuler un vrai navigateur.

**Fonctionne avec :**
- Liens de suivi envoyés par SMS ou e-mail par UberEats
- Pages de suivi publiques (sans connexion requise)

**Ne fonctionne pas avec :**
- Pages nécessitant une connexion au compte UberEats
- Commandes terminées / expirées
