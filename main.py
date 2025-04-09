import asyncio
import logging
import os
from instagrapi import Client
from pyrogram import Client as TgClient, filters
from pyrogram.types import Message

# Logging setup
logging.basicConfig(level=logging.INFO)

# Instagram Credentials
IG_USERNAME = "ig_ucbot"
IG_PASSWORD = "warval50"

# Telegram API Credentials
TELEGRAM_API_ID = 25742938  # Replace with your API ID
TELEGRAM_API_HASH = "b35b715fe8dc0a58e8048988286fc5b6"

# Initialize Instagram Client
cl = Client()

# Check if session file exists
session_file = "ig_session.json"
if os.path.exists(session_file):
    try:
        cl.load_settings(session_file)
        cl.login(IG_USERNAME, IG_PASSWORD)
        logging.info("✅ Logged in using existing session!")
    except Exception as e:
        logging.error(f"⚠️ Session file might be corrupted! Error: {e}")
        os.remove(session_file)  # Delete the corrupt session file
        logging.info("🗑️ Deleted old session file. Logging in again...")
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.dump_settings(session_file)
        logging.info("✅ New session created and saved!")
else:
    try:
        logging.info("🔑 Session file not found. Logging in...")
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.dump_settings(session_file)
        logging.info("✅ New session created and saved!")
    except Exception as e:
        logging.error(f"❌ Instagram login failed! Error: {e}")
        exit()

# Initialize Telegram Client (UserBot Session)
bot = TgClient("IgUserbot", api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)

@bot.on_message(filters.command("ping"))
async def ping_command(_, message: Message):
    await message.reply_text("✅ Instagram UserBot is Running!")

@bot.on_message(filters.command("stats"))
async def stats_command(_, message: Message):
    try:
        user_info = cl.user_info_by_username(IG_USERNAME)
        followers = user_info.follower_count
        following = user_info.following_count
        await message.reply_text(f"📊 **Instagram Stats:**\n👥 Followers: {followers}\n🔄 Following: {following}")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("dm"))
async def dm_command(_, message: Message):
    try:
        args = message.text.split(" ", 2)
        if len(args) < 3:
            await message.reply_text("Usage: `/dm <username> <message>`")
            return
        
        username, text = args[1], args[2]
        user_id = cl.user_id_from_username(username)
        cl.direct_send(text, [user_id])
        await message.reply_text(f"📩 Message sent to @{username}")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("follow"))
async def follow_command(_, message: Message):
    try:
        args = message.text.split(" ")
        if len(args) < 2:
            await message.reply_text("Usage: `/follow <username>`")
            return

        username = args[1]
        user_id = cl.user_id_from_username(username)
        cl.user_follow(user_id)
        await message.reply_text(f"✅ Followed @{username}")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("unfollow"))
async def unfollow_command(_, message: Message):
    try:
        args = message.text.split(" ")
        if len(args) < 2:
            await message.reply_text("Usage: `/unfollow <username>`")
            return

        username = args[1]
        user_id = cl.user_id_from_username(username)
        cl.user_unfollow(user_id)
        await message.reply_text(f"✅ Unfollowed @{username}")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Start the Telegram UserBot
bot.run()
