# Discord Nickname Bot
Simple nickname bot that allows members to change nicknames on discord.

## Prerequisites
- Your bot cannot change nicknames of users whose role is higher than the bot's role. Fix this in Server Settings → Roles by dragging the bot role above normal users.
- Update these variables in `bot.py` when testing:
```py
DEV_MODE = False
GUILD_ID = 1429389182416977972 # Channel ID
```

## Commands
```sh
/setlogchannel #mod-logs
/nick @user NewName
/resetnick @user
/nickhistory @user
```