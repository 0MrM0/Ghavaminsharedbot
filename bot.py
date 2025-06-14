# bot.py
# این فایل شامل کد ربات تلگرام است.

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import db # import the db.py module

# توکن ربات تلگرام خود را اینجا وارد کنید.
# این توکن توسط BotFather در تلگرام به شما داده شده است.
TELEGRAM_BOT_TOKEN = "8027072690:AAF1DDBu0RMMtA763iNQbu-xJoCtyztlzs8"

# پیکربندی لاگ‌ها برای نمایش پیام‌های ربات در کنسول
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# تابع شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start و خوش‌آمدگویی به کاربر."""
    user = update.effective_user
    await update.message.reply_html(
        f"سلام {user.mention_html()}! برای استعلام تعداد سهام قوامین، کدملی خود را ارسال کنید."
    )
    logger.info(f"User {user.id} started the bot.")

# تابع برای پردازش کدملی ارسالی توسط کاربر
async def handle_national_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    پردازش کدملی ارسالی کاربر و جستجو در دیتابیس.
    صفر ابتدایی و تعداد ارقام متفاوت در کدملی‌ها در نظر گرفته شده است.
    """
    national_code_input = update.message.text.strip() # دریافت پیام کاربر و حذف فاصله‌های اضافی

    # اعتبارسنجی اولیه: بررسی اینکه آیا ورودی فقط شامل ارقام است.
    if not national_code_input.isdigit():
        await update.message.reply_text("لطفاً یک کدملی معتبر (فقط شامل اعداد) ارسال کنید.")
        logger.warning(f"Invalid national code input from user {update.effective_user.id}: '{national_code_input}'")
        return

    # استفاده از تابع db برای جستجو در دیتابیس
    total_shares = db.get_shares_by_national_code(national_code_input)

    if total_shares is not None:
        await update.message.reply_text(
            f"کدملی {national_code_input} دارای {total_shares} سهم می‌باشد."
        )
        logger.info(f"Shares found for {national_code_input}: {total_shares}")
    else:
        await update.message.reply_text(
            f"متاسفانه کدملی {national_code_input} در سیستم یافت نشد. لطفاً از صحت کدملی اطمینان حاصل کنید."
        )
        logger.info(f"National code {national_code_input} not found.")

# تابع اصلی برای راه‌اندازی ربات
def main() -> None:
    """راه‌اندازی و اجرای ربات."""
    # بررسی وجود فایل دیتابیس
    if not os.path.exists(db.DATABASE_NAME):
        logger.error(f"Database file '{db.DATABASE_NAME}' not found. Please run xlsx_loader.py first.")
        print(f"\nخطا: فایل دیتابیس '{db.DATABASE_NAME}' یافت نشد.")
        print("لطفاً ابتدا اسکریپت xlsx_loader.py را اجرا کنید تا فایل اکسل پردازش و دیتابیس ساخته شود.")
        return

    # ساخت شیء Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # افزودن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_national_code))

    # شروع ربات (تا زمانی که برنامه متوقف شود، اجرا خواهد شد)
    logger.info("Bot started. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()