import logging
import requests
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- CONFIGURATION ---
TOKEN = "8976566832:AAFl03oOzAPS6yBb-LxKwOJEdjibDSljoqs"
ADMIN_ID = 8381570120
CHANNELS = ["@PixellabShimulXD", "@PixellabShimulXDChat", "@ShimulGraphicsBD", "@HunterGraphicsDesign"]
API_URL = "https://api.pinssaver.com/pin"

# Rate limiting dictionary
user_last_request = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# জয়েন চেক ফাংশন
async def is_subscribed(bot, user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

# স্টার্ট কমান্ড ও জয়েন স্ক্রিন
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_subscribed(context.bot, user_id):
        await show_welcome(update)
    else:
        keyboard = [[InlineKeyboardButton("Join Channels", url=f"https://t.me/{CHANNELS[0].replace('@','')}")],
                    [InlineKeyboardButton("Verify ✅", callback_data="verify")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👋 হ্যালো! বটটি ব্যবহার করতে নিচের চ্যানেলগুলোতে জয়েন করুন।\n\n"
            "চ্যানেল লিষ্ট:\n" + "\n".join(CHANNELS),
            reply_markup=reply_markup
        )

async def show_welcome(update):
    welcome_text = (
        "🌟 **Pinterest Video Downloader** 🌟\n\n"
        "স্বাগতম বন্ধু! আমি পিন্টারেস্ট থেকে হাই কোয়ালিটি ভিডিও ডাউনলোড করতে পারি।\n\n"
        "🛠 **ব্যবহার বিধি:**\n"
        "১. পিন্টারেস্ট ভিডিওর লিংক কপি করুন।\n"
        "২. এখানে সেন্ড করুন।\n"
        "৩. কিছুক্ষণ অপেক্ষা করুন, আমি ভিডিও পাঠিয়ে দেব।\n\n"
        "👤 **Developer:** @ShimulXD"
    )
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(welcome_text, parse_mode="Markdown")

# ভেরিফাই বাটন হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "verify":
        if await is_subscribed(context.bot, query.from_user.id):
            await show_welcome(update)
        else:
            await query.answer("আপনি এখনো সব চ্যানেলে জয়েন করেননি! ❌", show_alert=True)

# ভিডিও ডাউনলোড ও প্রসেসিং
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text

    if not await is_subscribed(context.bot, user_id):
        return await start(update, context)

    # Security: Rate Limiting (৫ সেকেন্ড গ্যাপ)
    current_time = time.time()
    if user_id in user_last_request and current_time - user_last_request[user_id] < 5:
        return await update.message.reply_text("⚠️ অনুগ্রহ করে ৫ সেকেন্ড অপেক্ষা করে পরবর্তী লিংক দিন।")
    user_last_request[user_id] = current_time

    if "pin.it" not in url and "pinterest.com" not in url:
        return await update.message.reply_text("❌ এটি সঠিক Pinterest লিংক নয়!")

    status_msg = await update.message.reply_text("🔍 ভিডিও তথ্য খোঁজা হচ্ছে... [░░░░░░░░░░] 0%")
    
    try:
        # API Request
        params = {'url': url}
        headers = {'User-Agent': "Mozilla/5.0"}
        response = requests.get(API_URL, params=params, headers=headers).json()

        if response.get("status") == 200:
            video_url = response['data']['src']['mp4'].get('720') or response['data']['src']['mp4'].get('360')
            title = response['data'].get('title', 'Pinterest Video')
            
            await status_msg.edit_text("📥 ভিডিও ডাউনলোড করা হচ্ছে... [▓▓▓▓░░░░░░] 40%")
            await asyncio.sleep(1)
            await status_msg.edit_text("📤 টেলিগ্রামে আপলোড হচ্ছে... [▓▓▓▓▓▓▓▓░░] 80%")
            
            await update.message.reply_video(video=video_url, caption=f"✅ **Title:** {title}\n\nDownloaded by @ShimulXD")
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ ভিডিও পাওয়া যায়নি বা লিংকটি ভুল।")
    except Exception as e:
        await status_msg.edit_text(f"❌ এরর: ভিডিওটি অনেক বড় বা সার্ভার সমস্যা।")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
