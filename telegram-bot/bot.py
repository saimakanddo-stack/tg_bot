import logging
import aiohttp
import asyncio
import json
import os
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from config import BOT_TOKEN, JSON_URL, BLOG_URL

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables for deployment
PORT = int(os.getenv('PORT', 8080))

# File paths for state
USERS_FILE = "users.json"
LAST_IDS_FILE = "last_ids.json"

# Flask app for health checks
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'telegram-bot'}), 200

def load_data(file_path, default):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except:
                return default
    return default

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f)

def add_user(chat_id):
    users = set(load_data(USERS_FILE, []))
    if chat_id not in users:
        users.add(chat_id)
        save_data(USERS_FILE, list(users))
        logger.info(f"New user registered: {chat_id}")

async def fetch_video_data():
    """Fetches video data from the JSON URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(JSON_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        return data
                    return data.get("videos", [])
                else:
                    logger.error(f"Failed to fetch JSON: Status {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error fetching JSON: {e}")
        return []

async def delete_message_after(message, delay: int):
    """Deletes a message after a specified delay."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Failed to delete message: {e}")

async def send_video_info(bot, chat_id, video):
    """Sends video information with photo and button to a specific chat."""
    title = video.get("title", "Video")
    desc = video.get("description", video.get("storyline", "No description available."))
    genre = video.get("genre", "N/A")
    lang = video.get("language_info", video.get("info3_language", video.get("language", "N/A")))
    year = video.get("released", video.get("year", "N/A"))
    img_url = video.get("imageUrl")
    video_id = video.get("id")
    
    target_url = f"{BLOG_URL}/?video={video_id}"
    
    message_text = (
        f"🎬 *{title}*\n\n"
        f"📝 *Description:* {desc}\n"
        f"🎭 *Genre:* {genre}\n"
        f"🌐 *Language:* {lang}\n"
        f"📅 *Year:* {year}\n"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                text="📺 Watch Now (Mini App)",
                web_app=WebAppInfo(url=target_url)
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if img_url:
            await bot.send_photo(
                chat_id=chat_id,
                photo=img_url,
                caption=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")

async def monitor_json(context: ContextTypes.DEFAULT_TYPE):
    """Job to monitor JSON for updates and broadcast new videos."""
    videos = await fetch_video_data()
    if not videos:
        return

    last_ids = set(load_data(LAST_IDS_FILE, []))
    current_ids = {str(v.get("id")) for v in videos}
    
    if not last_ids:
        save_data(LAST_IDS_FILE, list(current_ids))
        logger.info("First monitor run: Populated initial IDs.")
        return

    new_ids = current_ids - last_ids
    if new_ids:
        logger.info(f"New updates detected! New IDs: {new_ids}")
        users = load_data(USERS_FILE, [])
        
        for vid_id in new_ids:
            video = next((v for v in videos if str(v.get("id")) == vid_id), None)
            if video:
                for user_id in users:
                    await send_video_info(context.bot, user_id, video)
                    await asyncio.sleep(0.3)
        
        save_data(LAST_IDS_FILE, list(current_ids))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command, including deep linking and auto-deletion."""
    msg = update.message
    if not msg:
        return

    chat_id = update.effective_chat.id
    add_user(chat_id)

    try:
        await msg.delete()
    except Exception as e:
        logger.warning(f"Could not delete user message: {e}")

    args = context.args
    user = update.effective_user
    
    if not args:
        message_text = (
            f"স্বাগতম {user.first_name}!\n\n"
            "Dub Fusion Hub Video Bot এ আপনাকে স্বাগতম। "
            "ভিডিও পেতে সরাসরি লিঙ্ক ব্যবহার করুন বা ভিডিও আইডি প্রদান করুন।"
        )
        keyboard = [
            [
                InlineKeyboardButton("📢 Join Channel", url="https://t.me/dubflixhub"),
                InlineKeyboardButton("💬 Join Group", url="https://t.me/+gFFmFry18LYwMzFl")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id,
            text=message_text,
            reply_markup=reply_markup
        )
        return

    video_id = args[0]
    videos = await fetch_video_data()
    video = next((v for v in videos if str(v.get("id")) == video_id), None)
    
    if video:
        await send_video_info(context.bot, chat_id, video)
    else:
        error_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"দুঃখিত, আইডি '{video_id}' এর কোনো ভিডিও পাওয়া যায়নি।"
        )
        asyncio.create_task(delete_message_after(error_msg, 5))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    await update.message.reply_text(
        "সাহায্য:\n"
        "১. ভিডিও ID দিয়ে সার্চ করুন (e.g., /start movie1)\n"
        "২. কোনো সমস্যা হলে যোগাযোগ করুন @dubflixhub"
    )

if __name__ == '__main__':
    if not BOT_TOKEN or "AAE" not in BOT_TOKEN:
        print("Error: Invalid BOT_TOKEN format. Check your Base64 encoding in config.py")
    else:
        # Build application
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('help', help_command))
        
        # Add Job Queue for monitoring
        job_queue = application.job_queue
        job_queue.run_repeating(monitor_json, interval=300, first=10)
        
        print("Bot is starting with Multi-Service support...")

        # Deployment Logic (Webhook vs Polling)
        if 'RAILWAY_STATIC_URL' in os.environ or 'RENDER' in os.environ or 'KOYEB_APP_NAME' in os.environ:
            # Production: Webhook usage
            logger.info("Starting in Webhook mode...")
            url = os.getenv('RAILWAY_STATIC_URL', os.getenv('RENDER_EXTERNAL_URL', os.getenv('KOYEB_PUBLIC_DOMAIN', '')))
            if url:
                if not url.startswith('http'):
                    url = f"https://{url}"
                
                # Start Flask in a separate thread for health checks if needed, 
                # but run_webhook also handles the web server.
                # Here we use run_webhook which starts its own webserver.
                application.run_webhook(
                    listen="0.0.0.0",
                    port=PORT,
                    url_path=BOT_TOKEN,
                    webhook_url=f"{url}/{BOT_TOKEN}"
                )
            else:
                logger.error("No deployment URL found for Webhook!")
        else:
            # Development: Polling usage
            logger.info("Starting in Polling mode...")
            application.run_polling()
