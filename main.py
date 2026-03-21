import discord
from discord.ext import commands
import os

# ===== CONFIG =====
GUILD_ID = 1235640804148645928
VERIFIED_ROLE = "Verified"
MEMBER_ROLE = "Members"

# ===== INTENTS =====
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================================================
# READY
# =========================================================
@bot.event
async def on_ready():
    print(f"✅ Bot online jako {bot.user}")

# =========================================================
# START (RAILWAY)
# =========================================================
bot.run(os.getenv("TOKEN"))
