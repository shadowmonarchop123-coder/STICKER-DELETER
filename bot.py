import os
import time
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 8104158848

app = Client("anti_spam_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ========================
# STORAGE
# ========================
data = {}

def get_group(group_id):
    if group_id not in data:
        data[group_id] = {
            "users": {},
            "settings": {
                "cooldown": 10,
                "sticker": True,
                "gif": True,
                "emoji": True
            }
        }
    return data[group_id]

# ========================
# EMOJI CHECK
# ========================
emoji_pattern = re.compile(
    r"^[\U0001F300-\U0001FAFF\U00002700-\U000027BF]+$"
)

def is_emoji_only(text):
    return bool(text and emoji_pattern.fullmatch(text.strip()))

# ========================
# ADMIN CHECK
# ========================
async def is_admin(client, message):
    if message.from_user.id == OWNER_ID:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ["administrator", "creator"]
    except:
        return False

# ========================
# START (DM UI)
# ========================
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Support Channel", url="https://t.me/+Y6c_X38FJvU1OWZl")],
        [InlineKeyboardButton("💬 Support Group", url="https://t.me/+C3tXdJcwoSBiZGZl")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/mvtyy")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ])

    await message.reply_text(
        "🔥 Welcome to Anti-Spam Bot\n\nClean your groups automatically 🚀",
        reply_markup=keyboard
    )

# ========================
# HELP BUTTON
# ========================
@app.on_callback_query(filters.regex("help"))
async def help_cb(client, query):
    await query.message.edit_text(
        "⚙️ **HOW TO USE BOT**\n\n"
        "1. Add bot to your group\n"
        "2. Give admin rights:\n"
        "   • Delete messages\n\n"
        "📌 **COMMANDS:**\n"
        "/setcooldown 10\n"
        "/toggle_sticker on/off\n"
        "/toggle_gif on/off\n"
        "/toggle_emoji on/off\n\n"
        "🚫 **RULES:**\n"
        "- Sticker spam → deleted\n"
        "- GIF spam → deleted\n"
        "- Emoji-only spam → deleted\n"
        "- Text + emoji → allowed\n\n"
        "⚡ Bot works silently (no messages)"
    )

# ========================
# SET COOLDOWN
# ========================
@app.on_message(filters.command("setcooldown") & filters.group)
async def set_cooldown(client, message):
    if not await is_admin(client, message):
        return

    try:
        sec = int(message.command[1])
        group = get_group(message.chat.id)
        group["settings"]["cooldown"] = sec
        await message.delete()
    except:
        await message.delete()

# ========================
# TOGGLE SYSTEM
# ========================
@app.on_message(filters.command("toggle_sticker") & filters.group)
async def toggle_sticker(client, message):
    if not await is_admin(client, message):
        return

    try:
        state = message.command[1].lower()
        group = get_group(message.chat.id)
        group["settings"]["sticker"] = (state == "on")
        await message.delete()
    except:
        await message.delete()

@app.on_message(filters.command("toggle_gif") & filters.group)
async def toggle_gif(client, message):
    if not await is_admin(client, message):
        return

    try:
        state = message.command[1].lower()
        group = get_group(message.chat.id)
        group["settings"]["gif"] = (state == "on")
        await message.delete()
    except:
        await message.delete()

@app.on_message(filters.command("toggle_emoji") & filters.group)
async def toggle_emoji(client, message):
    if not await is_admin(client, message):
        return

    try:
        state = message.command[1].lower()
        group = get_group(message.chat.id)
        group["settings"]["emoji"] = (state == "on")
        await message.delete()
    except:
        await message.delete()

# ========================
# MAIN SPAM DETECTOR
# ========================
@app.on_message(filters.group)
async def spam_handler(client, message):
    if not message.from_user:
        return

    group = get_group(message.chat.id)
    user_id = message.from_user.id
    now = time.time()

    if user_id not in group["users"]:
        group["users"][user_id] = {
            "sticker": 0,
            "gif": 0,
            "emoji": 0
        }

    user = group["users"][user_id]
    settings = group["settings"]
    cooldown = settings["cooldown"]

    # Sticker Spam
    if message.sticker and settings["sticker"]:
        if now - user["sticker"] < cooldown:
            await message.delete()
            return
        user["sticker"] = now

    # GIF Spam
    if message.animation and settings["gif"]:
        if now - user["gif"] < cooldown:
            await message.delete()
            return
        user["gif"] = now

    # Emoji-only Spam
    if message.text and settings["emoji"]:
        if is_emoji_only(message.text):
            if now - user["emoji"] < cooldown:
                await message.delete()
                return
            user["emoji"] = now

# ========================
# RUN
# ========================
print("🔥 Bot Started...")
app.run()
