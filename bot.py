import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from scraper import fetch_order_info

# ══════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════
TOKEN = os.getenv("DISCORD_TOKEN", "TON_TOKEN_ICI")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ══════════════════════════════════════════════
#  COMMANDE /url
# ══════════════════════════════════════════════
@tree.command(name="url", description="Suivre une commande UberEats")
@app_commands.describe(lien="Colle ici le lien de ta commande UberEats")
async def url_command(interaction: discord.Interaction, lien: str):
    if "ubereats.com" not in lien:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Lien invalide",
                description="Merci de coller un lien **UberEats** valide.\n`https://www.ubereats.com/orders/...`",
                color=0xFF3008,
            ),
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True)

    try:
        infos = await fetch_order_info(lien)
    except Exception as e:
        embed = discord.Embed(
            title="⚠️ Erreur lors de la récupération",
            description=f"```{str(e)}```",
            color=0xFF8C00,
        )
        await interaction.followup.send(embed=embed)
        return

    if not infos:
        embed = discord.Embed(
            title="🔒 Commande introuvable",
            description=(
                "Impossible de récupérer les informations.\n\n"
                "**Causes possibles :**\n"
                "• Le lien a expiré\n"
                "• La page nécessite une connexion UberEats\n"
                "• La commande est déjà livrée\n\n"
                "💡 Utilise le lien de suivi envoyé par **SMS ou e-mail**."
            ),
            color=0xFF8C00,
        )
        await interaction.followup.send(embed=embed)
        return

    # ── Embed principal ──
    color = 0x06C167  # Vert UberEats

    embed = discord.Embed(
        title="🛵  Suivi de commande UberEats",
        color=color,
    )

    embed.add_field(
        name="👤  Prénom",
        value=f"```{infos.get('prenom', 'Inconnu')}```",
        inline=True,
    )
    embed.add_field(
        name="🕐  Heure d'arrivée",
        value=f"```{infos.get('heure', 'Inconnue')}```",
        inline=True,
    )
    embed.add_field(
        name="🔑  Code à donner au livreur",
        value=f"```{infos.get('code', 'Non disponible')}```",
        inline=False,
    )

    if infos.get("statut"):
        embed.add_field(name="📦  Statut", value=infos["statut"], inline=False)

    embed.set_footer(
        text=f"Demandé par {interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
    )

    await interaction.followup.send(embed=embed)


# ══════════════════════════════════════════════
#  EVENTS
# ══════════════════════════════════════════════
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅  Connecté en tant que {bot.user}  (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="les livraisons UberEats 🛵",
        )
    )


bot.run(TOKEN)
