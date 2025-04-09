from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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
    except Exception as e:
        logging.error(f"❌ Instagram login failed! Error: {e}")
        exit()

# Initialize Telegram **Userbot**
bot = Client("IgUserbot")  # This will use 'IgUserbot.session' instead of bot token

# Dictionary to track blocked users
blocked_users = set()

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

@bot.on_message(filters.private & ~filters.bot)
async def private_message_handler(client, message):
    user_id = message.from_user.id
    if user_id in blocked_users:
        return  # Ignore messages from blocked users

    # Notify admin about the PM
    await message.forward(chat_id="me")  # Sends the message to your Saved Messages

    # Send control buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Allow", callback_data=f"allow_{user_id}"),
         InlineKeyboardButton("🚫 Block", callback_data=f"block_{user_id}")]
    ])
    await bot.send_message(
        chat_id="me",
        text=f"📩 **New PM from:** [{message.from_user.first_name}](tg://user?id={user_id})\n🆔 `{user_id}`",
        reply_markup=buttons
    )

@bot.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user_id = int(query.data.split("_")[1])

    if "block" in query.data:
        blocked_users.add(user_id)
        await query.message.edit_text(f"🚫 **User Blocked:** `{user_id}`")
        await bot.send_message(chat_id=user_id, text="⚠️ You have been blocked!")

    elif "allow" in query.data:
        if user_id in blocked_users:
            blocked_users.remove(user_id)
        await query.message.edit_text(f"✅ **User Allowed:** `{user_id}`")
        await bot.send_message(chat_id=user_id, text="✅ You have been allowed to chat!")

@bot.on_message(filters.command("reply") & filters.user("me"))
async def reply_command(client, message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply_text("❌ **Usage:** `/reply user_id message`")
        return

    try:
        user_id = int(args[1])
        msg_text = args[2]

        if user_id in blocked_users:
            await message.reply_text("🚫 **Error:** This user is blocked!")
            return

        await bot.send_message(chat_id=user_id, text=f"📩 **Admin Reply:**\n\n{msg_text}")
        await message.reply_text(f"✅ **Message sent to** `{user_id}`")
    except ValueError:
        await message.reply_text("❌ **Invalid User ID!**")

# Start Userbot
bot.run()
