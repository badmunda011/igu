from pyrogram import Client, filters
from instagrapi import Client as InstaClient
import logging
import os

logging.basicConfig(level=logging.INFO)

# Instagram Credentials
IG_USERNAME = "ig_ucbot"
IG_PASSWORD = "warval50"

# Initialize Instagram Client
cl = InstaClient()
session_file = "ig_session.json"

if os.path.exists(session_file):
    try:
        cl.load_settings(session_file)
        cl.login(IG_USERNAME, IG_PASSWORD)
        logging.info("✅ Logged in using existing session!")
    except Exception as e:
        logging.error(f"⚠️ Corrupt session! Error: {e}")
        os.remove(session_file)
        logging.info("🗑️ Deleted old session file. Logging in again...")
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.dump_settings(session_file)
        logging.info("✅ New session saved!")
else:
    try:
        logging.info("🔑 Logging in to Instagram...")
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.dump_settings(session_file)
        logging.info("✅ Session saved!")
    except Exception as e:
        logging.error(f"❌ Instagram login failed! Error: {e}")
        exit()

# Initialize Telegram **Userbot** (NOT a Bot)
bot = Client("IgUserbot")  # This will use 'IgUserbot.session' instead of bot token

@bot.on_message(filters.command("ping"))
async def ping_command(_, message):
    await message.reply_text("✅ Userbot Active!")

@bot.on_message(filters.command("stats"))
async def stats_command(_, message):
    try:
        user_info = cl.user_info_by_username(IG_USERNAME)
        followers = user_info.follower_count
        following = user_info.following_count
        await message.reply_text(f"📊 **Instagram Stats:**\n👥 Followers: {followers}\n🔄 Following: {following}")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Start Userbot
bot.run()
