import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS nickname_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER,
    user_id INTEGER,
    old_nick TEXT,
    new_nick TEXT,
    moderator TEXT,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS guild_config (
    guild_id INTEGER PRIMARY KEY,
    log_channel_id INTEGER
)
""")

conn.commit()


def set_log_channel(guild_id, channel_id):
    cursor.execute("""
    INSERT OR REPLACE INTO guild_config (guild_id, log_channel_id)
    VALUES (?, ?)
    """, (guild_id, channel_id))
    conn.commit()


def get_log_channel(guild_id):
    cursor.execute(
        "SELECT log_channel_id FROM guild_config WHERE guild_id=?",
        (guild_id,)
    )
    result = cursor.fetchone()
    return result[0] if result else None


def add_nickname_change(guild_id, user_id, old_nick, new_nick, moderator, timestamp):
    cursor.execute("""
    INSERT INTO nickname_history
    (guild_id, user_id, old_nick, new_nick, moderator, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (guild_id, user_id, old_nick, new_nick, moderator, timestamp))
    conn.commit()


def get_history(user_id):
    cursor.execute("""
    SELECT old_nick, new_nick, moderator, timestamp
    FROM nickname_history
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 10
    """, (user_id,))
    return cursor.fetchall()