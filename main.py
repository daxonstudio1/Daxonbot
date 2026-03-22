import discord
from discord.ext import commands
from discord import Option
from datetime import timedelta

# ================= CONFIG =================

GUILD_ID = 1235640804148645928

VERIFIED_ROLE = "Verified"
MEMBER_ROLE = "Members"
STAFF_ROLE = "Staff team"

intents = discord.Intents.all()
bot = commands.Bot(intents=intents)

# ================= READY =================
@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicket())
    print(f"✅ Bot online jako {bot.user}")

# ================= WELCOME =================
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=MEMBER_ROLE)
    if role:
        await member.add_roles(role)

    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="👋 Welcome!",
            description=f"Welcome {member.mention} to **{member.guild.name}**!",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

# ================= VERIFY =================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✅ Verify",
        style=discord.ButtonStyle.success,
        custom_id="verify_button"
    )
    async def verify(self, button, interaction):
        role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE)

        if role in interaction.user.roles:
            return await interaction.response.send_message("❌ Already verified", ephemeral=True)

        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ You are now verified!", ephemeral=True)

@bot.slash_command(guild_ids=[GUILD_ID])
async def setup_verify(ctx):
    embed = discord.Embed(
        title="🔐 Verification",
        description="Click button to verify",
        color=discord.Color.red()
    )
    await ctx.channel.send(embed=embed, view=VerifyView())
    await ctx.respond("✅ Done", ephemeral=True)

# ================= TICKETS =================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎟️ Create Ticket",
        style=discord.ButtonStyle.red,
        custom_id="ticket_create"
    )
    async def create_ticket(self, button, interaction):
        guild = interaction.guild

        category = discord.utils.get(guild.categories, name="tickets")
        if not category:
            category = await guild.create_category("tickets")

        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True)
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        await channel.send(
            content=interaction.user.mention,
            embed=discord.Embed(
                title="🎟️ Ticket",
                description="Support will be with you shortly.",
                color=discord.Color.red()
            ),
            view=CloseTicket()
        )

        await interaction.response.send_message("✅ Ticket created", ephemeral=True)

class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Close",
        style=discord.ButtonStyle.gray,
        custom_id="ticket_close"
    )
    async def close(self, button, interaction):
        await interaction.channel.delete()

@bot.slash_command(guild_ids=[GUILD_ID])
async def setup_tickets(ctx):
    embed = discord.Embed(
        title="🎟️ Tickets",
        description="Click to create ticket",
        color=discord.Color.red()
    )
    await ctx.channel.send(embed=embed, view=TicketView())
    await ctx.respond("✅ Done", ephemeral=True)

# ================= MODERATION =================
warns = {}

@bot.slash_command(guild_ids=[GUILD_ID])
async def ban(ctx, user: discord.Member, reason: str = "No reason"):
    await user.ban(reason=reason)
    await ctx.respond(embed=discord.Embed(
        title="🔨 Banned",
        description=f"{user.mention}\n{reason}",
        color=discord.Color.red()
    ))

@bot.slash_command(guild_ids=[GUILD_ID])
async def kick(ctx, user: discord.Member):
    await user.kick()
    await ctx.respond(embed=discord.Embed(
        title="👢 Kicked",
        description=user.mention,
        color=discord.Color.red()
    ))

@bot.slash_command(guild_ids=[GUILD_ID])
async def timeout(ctx, user: discord.Member, seconds: int):
    await user.edit(timed_out_until=discord.utils.utcnow() + timedelta(seconds=seconds))
    await ctx.respond(embed=discord.Embed(
        title="🔇 Timeout",
        description=f"{user.mention} {seconds}s",
        color=discord.Color.red()
    ))

@bot.slash_command(guild_ids=[GUILD_ID])
async def warn(ctx, user: discord.Member, reason: str):
    warns.setdefault(user.id, []).append(reason)
    await ctx.respond(embed=discord.Embed(
        title="⚠️ Warn",
        description=f"{user.mention}\n{reason}",
        color=discord.Color.red()
    ))

@bot.slash_command(guild_ids=[GUILD_ID])
async def warns_cmd(ctx, user: discord.Member):
    data = warns.get(user.id, [])
    embed = discord.Embed(title="Warns", color=discord.Color.red())
    embed.description = "\n".join(data) if data else "None"
    await ctx.respond(embed=embed)

@bot.slash_command(guild_ids=[GUILD_ID])
async def unwarn(ctx, user: discord.Member, index: int):
    if user.id in warns and len(warns[user.id]) >= index:
        warns[user.id].pop(index-1)
    await ctx.respond("✅", ephemeral=True)

# ================= START =================
import os

bot.run(os.getenv("TOKEN"))
