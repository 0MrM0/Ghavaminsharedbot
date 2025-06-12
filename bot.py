# bot.py (نسخه نهایی برای Fly.io)

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import db  # ما از ماژول db جدید استفاده خواهیم کرد

# --- تنظیمات اولیه ---
# توکن بات و آدرس دیتابیس از متغیرهای محیطی (Secrets) در Fly.io خوانده می‌شود
# این روش امن و استاندارد است
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

# پیکربندی لاگ‌ها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- توابع اصلی بات ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"سلام {user.mention_html()}! برای استعلام تعداد سهام، کدملی خود را ارسال کنید."
    )
    logger.info(f"User {user.id} ({user.username}) started the bot.")

async def handle_national_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پردازش کدملی و پاسخ به کاربر"""
    national_code_input = update.message.text.strip()
    
    # بررسی اولیه ورودی کاربر
    if not national_code_input.isdigit() or len(national_code_input) != 10:
        await update.message.reply_text("❗️ لطفاً یک کدملی معتبر (عدد ۱۰ رقمی) وارد کنید.")
        return

    # نمایش پیام "در حال پردازش"
    processing_message = await update.message.reply_text("⏳ در حال استعلام، لطفاً صبر کنید...")

    total_shares = db.get_shares_by_national_code(national_code_input)

    if total_shares is not None:
        response_text = f"✅ تعداد سهام شما: {total_shares}"
        logger.info(f"Shares found for {national_code_input}: {total_shares}")
    else:
        response_text = "❌ کدملی وارد شده در سیستم یافت نشد."
        logger.info(f"National code {national_code_input} not found.")
        
    # ویرایش پیام "در حال پردازش" و نمایش نتیجه نهایی
    await context.bot.edit_message_text(
        text=response_text,
        chat_id=update.effective_chat.id,
        message_id=processing_message.message_id
    )

def main() -> None:
    """راه‌اندازی و اجرای ربات"""
    if not BOT_TOKEN:
        logger.error("توکن تلگرام (BOT_TOKEN) یافت نشد! لطفاً آن را به عنوان secret تنظیم کنید.")
        return
        
    if not DATABASE_URL:
        logger.error("آدرس دیتابیس (DATABASE_URL) یافت نشد!")
        return

    logger.info("Bot is starting...")
    
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_national_code))

    application.run_polling()

if __name__ == '__main__':
    main()