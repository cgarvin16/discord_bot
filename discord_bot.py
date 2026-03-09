import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import database

TOKEN = "MTQ4MDQxNjA0MjU1NDYyNjIyMg.GCCNWJ.acv0mnjazk5ygcdAXrc7PqlIL7zIBXFG06gPHE"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


# ---------------------------
# Set Log Channel
# ---------------------------

@bot.tree.command(name="setlogchannel", description="Set nickname log channel")
@app_commands.checks.has_permissions(administrator=True)
async def setlogchannel(interaction: discord.Interaction, channel: discord.TextChannel):

    database.set_log_channel(interaction.guild.id, channel.id)

    await interaction.response.send_message(
        f"✅ Log channel set to {channel.mention}"
    )


# ---------------------------
# Nickname Command
# ---------------------------

@bot.tree.command(name="nick", description="Change a user's nickname")
async def nick(interaction: discord.Interaction, member: discord.Member, nickname: str):

    if not interaction.user.guild_permissions.manage_nicknames:
        await interaction.response.send_message(
            "You don't have permission.",
            ephemeral=True
        )
        return

    old_nick = member.nick or member.name

    try:
        await member.edit(nick=nickname)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        database.add_nickname_change(
            interaction.guild.id,
            member.id,
            old_nick,
            nickname,
            interaction.user.name,
            timestamp
        )

        await interaction.response.send_message(
            f"✅ {member.mention}'s nickname changed to **{nickname}**"
        )

        log_channel_id = database.get_log_channel(interaction.guild.id)

        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)

            if log_channel:
                await log_channel.send(
                    f"🔧 {interaction.user.mention} changed {member.mention}'s nickname\n"
                    f"Old: **{old_nick}**\nNew: **{nickname}**"
                )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I can't change that nickname.",
            ephemeral=True
        )


# ---------------------------
# Reset Nickname
# ---------------------------

@bot.tree.command(name="resetnick", description="Reset a user's nickname")
async def resetnick(interaction: discord.Interaction, member: discord.Member):

    old_nick = member.nick or member.name

    try:
        await member.edit(nick=None)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        database.add_nickname_change(
            interaction.guild.id,
            member.id,
            old_nick,
            member.name,
            interaction.user.name,
            timestamp
        )

        await interaction.response.send_message(
            f"🔄 {member.mention}'s nickname reset."
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I can't reset that nickname.",
            ephemeral=True
        )


# ---------------------------
# Nickname History
# ---------------------------

@bot.tree.command(name="nickhistory", description="View nickname history")
async def nickhistory(interaction: discord.Interaction, member: discord.Member):

    history = database.get_history(member.id)

    if not history:
        await interaction.response.send_message(
            "No nickname history found.",
            ephemeral=True
        )
        return

    message = f"📜 Nickname history for {member.mention}\n\n"

    for old, new, mod, time in history:
        message += f"**{old} → {new}** | {mod} | {time}\n"

    await interaction.response.send_message(message, ephemeral=True)


bot.run(TOKEN)