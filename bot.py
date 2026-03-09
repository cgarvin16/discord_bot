import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import database
import os

DEV_MODE = False
DEV_GUILD_ID = 1429389182416977972

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    if DEV_MODE:
        guild = discord.Object(id=DEV_GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"DEV sync: {len(synced)} commands")
    else:
        synced = await bot.tree.sync()
        print(f"GLOBAL sync: {len(synced)} commands")

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
@app_commands.describe(
    member="The member to rename",
    nickname="The new nickname"
)
async def nick(interaction: discord.Interaction, member: discord.Member, nickname: str):

    if not interaction.user.guild_permissions.manage_nicknames:
        await interaction.response.send_message(
            "❌ You don't have permission to manage nicknames.",
            ephemeral=True
        )
        return

    # Capture the current display name BEFORE changing it
    old_name = member.display_name

    try:
        await member.edit(nick=nickname)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Store correct history
        database.add_nickname_change(
            interaction.guild.id,
            member.id,
            old_name,
            nickname,
            interaction.user.name,
            timestamp
        )

        # Confirmation message (cleaner)
        await interaction.response.send_message(
            f"✅ **{old_name}**'s nickname changed to {member.mention}"
        )

        # Log channel
        log_channel_id = database.get_log_channel(interaction.guild.id)
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)

            if log_channel:
                await log_channel.send(
                    f"🔧 {interaction.user.mention} changed **{old_name}** → {member.mention}"
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
@app_commands.describe(
    member="The member whose nickname will be reset"
)
async def resetnick(interaction: discord.Interaction, member: discord.Member):

    old_name = member.display_name
    new_name = member.name  # username when nickname removed

    try:
        await member.edit(nick=None)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        database.add_nickname_change(
            interaction.guild.id,
            member.id,
            old_name,
            new_name,
            interaction.user.name,
            timestamp
        )

        await interaction.response.send_message(
            f"🔄 **{old_name}**'s nickname reset to {member.mention}"
        )

        # Log channel
        log_channel_id = database.get_log_channel(interaction.guild.id)
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)

            if log_channel:
                await log_channel.send(
                    f"🔄 {interaction.user.mention} reset **{old_name}** → {member.mention}"
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
@app_commands.describe(
    member="The member to view history for"
)
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