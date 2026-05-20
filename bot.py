import logging
import asyncio
import aiohttp
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- CONFIGURATION ---
TOKEN = "8976566832:AAFl03oOzAPS6yBb-LxKwOJEdjibDSljoqs"
ADMIN_ID = 8381570120
CHANNELS = [
    {"name": "Pixellab Shimul XD", "url": "https://t.me/PixellabShimulXD", "id": "@PixellabShimulXD"},
    {"name": "Shimul XD Chat", "url": "https://t.me/PixellabShimulXDChat", "id": "@PixellabShimulXDChat"},
    {"name": "Shimul Graphics BD", "url": "https://t.me/ShimulGraphicsBD", "id": "@ShimulGraphicsBD"},
    {"name": "Hunter Graphics Design", "url": "https://t.me/HunterGraphicsDesign", "id": "@HunterGraphicsDesign"}
]
API_URL = "https://api.pinssaver.com/pin"

# Anti-Spam & Security
user_cooldowns = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- UTILS ---
async def is_subscribed(bot, user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ['left', 'kicked', 'null']:
                return False
        except Exception:
            return False
    return True

async def progress_bar(current, total=100):
    percent = (current / total) * 100
    bar = "▓" * int(percent / 10) + "░" * (10 - int(percent / 10))
    return f"[{bar}] {int(percent)}%"

# --- SCREENS ---

async def show_verify_screen(update: Update):
    keyboard = []
    for ch in CHANNELS:
        keyboard.append([InlineKeyboardButton(f"Join {ch['name']} 🔗", url=ch['url'])])
    
    keyboard.append([InlineKeyboardButton("Verify ✅ [Click After Join]", callback_data="verify_user")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "⚠️ **ACCESS DENIED!** ⚠️\n\n"
        "বন্ধু, বটটি ব্যবহার করতে চাইলে আপনাকে অবশ্যই আমাদের সব চ্যানেলে জয়েন থাকতে হবে।\n\n"
        "🔰 *নিচের বাটনগুলো থেকে জয়েন করুন এবং ভেরিফাই বাটনে ক্লিক করুন:* "
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=constants.ParseMode.MARKDOWN)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode=constants.ParseMode.MARKDOWN)

async def show_welcome_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"✨ **WELCOME TO PREMIUM DOWNLOADER** ✨\n\n"
        f"👋 হ্যালো, *{user.first_name}*!\n"
        f"আমি একটি **Ultra-Fast Pinterest Video Downloader** বট।\n\n"
        f"🚀 **বটের বৈশিষ্ট্যসমূহ:**\n"
        f"├ ⚡ _হাই-স্পিড ডাউনলোড_\n"
        f"├ 🎬 _720p HD Quality ভিডিও_\n"
        f"├ 🛡️ _শক্তিশালী সিকিউরিটি_\n"
        f"└ 💎 _সম্পূর্ণ ফ্রি এবং প্রিমিয়াম ইউজার ইন্টারফেস_\n\n"
        f"📖 **কিভাবে ব্যবহার করবেন?**\n"
        f"যেকোনো Pinterest ভিডিওর লিংক আমাকে সেন্ড করুন। বাকি কাজ আমি করে দেব।\n\n"
        f"👨‍💻 **Developer:** [@ShimulXD](https://t.me/ShimulXD)"
    )
    
    keyboard = [[InlineKeyboardButton("Developer 👤", url="https://t.me/ShimulXD")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True)

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_subscribed(context.bot, update.effective_user.id):
        await show_welcome_screen(update, context)
    else:
        await show_verify_screen(update)

async def handle_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if await is_subscribed(context.bot, user_id):
        await query.answer("Verification Success! ✅", show_alert=False)
        await show_welcome_screen(update, context)
    else:
        await query.answer("❌ আপনি সবগুলোতে জয়েন করেননি!", show_alert=True)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text

    if not await is_subscribed(context.bot, user_id):
        return await show_verify_screen(update)

    # Security: Cooldown logic
    if user_id in user_cooldowns and time.time() - user_cooldowns[user_id] < 10:
        return await update.message.reply_text("⏳ **Slow Down!** প্রতি রিকোয়েস্টের মধ্যে ১০ সেকেন্ড গ্যাপ রাখুন।")
    
    if "pin.it" not in url and "pinterest.com" not in url:
        return await update.message.reply_text("❌ দুঃখিত বন্ধু, এটি সঠিক লিংক নয়।")

    user_cooldowns[user_id] = time.time()
    
    # Premium Animation Start
    status_msg = await update.message.reply_text("💎 **Initializing Premium Server...**")
    await asyncio.sleep(0.8)
    
    try:
        async with aiohttp.ClientSession() as session:
            await status_msg.edit_text(f"🔍 **Fetching Data...**\n{await progress_bar(20)}")
            
            async with session.get(API_URL, params={'url': url}) as resp:
                data = await resp.json()
                
                if data.get("status") == 200:
                    video_info = data['data']
                    video_url = video_info['src']['mp4'].get('720') or video_info['src']['mp4'].get('360')
                    title = video_info.get('title', 'Pinterest Video')

                    await status_msg.edit_text(f"📥 **Downloading High Quality...**\n{await progress_bar(60)}")
                    await asyncio.sleep(0.5)
                    await status_msg.edit_text(f"📤 **Uploading to Telegram...**\n{await progress_bar(90)}")

                    await update.message.reply_video(
                        video=video_url,
                        caption=f"✅ **Title:** _{title}_\n\n💎 **Quality:** 720p HD\n👤 **User:** {update.effective_user.first_name}\n\n🔥 Powered by @ShimulXD",
                        parse_mode=constants.ParseMode.MARKDOWN
                    )
                    await status_msg.delete()
                else:
                    await status_msg.edit_text("❌ সার্ভার থেকে ডাটা পাওয়া যায়নি। পরে চেষ্টা করুন।")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ **Error:** ভিডিওটি খুব বড় অথবা সার্ভার বিজি।")

# Admin Stats (Simplified)
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"📊 **Bot Status:** Active\n🚀 **Mode:** Premium Ultra High Speed")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CallbackQueryHandler(handle_verification, pattern="verify_user"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("💎 Premium Pinterest Bot Started...")
    app.run_polling()

if __name__ == '__main__':
    main()
