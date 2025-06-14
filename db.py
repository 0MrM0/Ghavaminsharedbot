# db.py
# این فایل شامل توابع مربوط به مدیریت دیتابیس SQLite است.

import sqlite3
import logging
import os
from typing import Optional, Tuple

# نام فایل دیتابیس
DATABASE_NAME = "stock_data.db"

# پیکربندی لاگ‌ها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_db_connection() -> Optional[sqlite3.Connection]:
    """
    اتصال به دیتابیس SQLite و بازگرداندن شیء اتصال.
    اگر دیتابیس موجود نباشد، آن را ایجاد می‌کند.
    """
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row # برای دسترسی به ستون‌ها با نام
        logger.info(f"Connected to database: {DATABASE_NAME}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database {DATABASE_NAME}: {e}")
        return None

def create_shares_table(conn: sqlite3.Connection):
    """
    جدول 'shares' را در دیتابیس ایجاد می‌کند اگر وجود نداشته باشد.
    این تابع انتظار دارد یک شیء اتصال (conn) را به عنوان ورودی بگیرد.
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shares (
                national_code TEXT PRIMARY KEY,
                total_shares INTEGER
            )
        ''')
        # نیازی به conn.commit() در اینجا نیست، زیرا xlsx_loader آن را پس از اتمام همه درج‌ها انجام می‌دهد.
        logger.info("Table 'shares' ensured to exist.")
    except sqlite3.Error as e:
        logger.error(f"Error creating table 'shares': {e}")
        raise # رخداد خطا را دوباره پرتاب می‌کنیم تا تابع فراخواننده از آن مطلع شود.

def insert_or_replace_share_data(cursor: sqlite3.Cursor, national_code: str, total_shares: int) -> None:
    """
    داده‌های سهم را با استفاده از یک cursor موجود در دیتابیس وارد یا جایگزین می‌کند.
    این تابع نیازی به commit یا close کردن اتصال ندارد.
    """
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO shares (national_code, total_shares) VALUES (?, ?)",
            (national_code, total_shares)
        )
        # نیازی به logger.debug در اینجا نیست، چون برای هر ردیف بسیار زیاد می‌شود.
        # logger.debug(f"Inserted/Replaced: {national_code}, {total_shares}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting/replacing data for {national_code}: {e}")
        # اینجا رخداد را پرتاب نمی‌کنیم تا پردازش سایر ردیف‌ها ادامه پیدا کند
        # اما خطای خاص این ردیف را لاگ می‌کنیم.

def get_shares_by_national_code(national_code: str) -> Optional[int]:
    """
    تعداد سهام را بر اساس کدملی از دیتابیس دریافت می‌کند.
    اگر یافت نشود، None برمی‌گرداند.
    """
    conn = get_db_connection() # این تابع فقط برای خواندن است، پس می‌تواند اتصال را خودش مدیریت کند.
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT total_shares FROM shares WHERE national_code = ?",
                (national_code,)
            )
            result = cursor.fetchone()
            if result:
                return result['total_shares']
            return None
        except sqlite3.Error as e:
            logger.error(f"Error querying shares for {national_code}: {e}")
            return None
        finally:
            conn.close()
    return None

if __name__ == '__main__':
    # این بخش برای تست db.py است
    conn_test = get_db_connection()
    if conn_test:
        try:
            create_shares_table(conn_test)
            cursor_test = conn_test.cursor()
            insert_or_replace_share_data(cursor_test, "0061339326", 1500)
            insert_or_replace_share_data(cursor_test, "111974", 200)
            conn_test.commit() # Commit changes after all inserts
            print(f"Shares for 0061339326: {get_shares_by_national_code('0061339326')}")
            print(f"Shares for 111974: {get_shares_by_national_code('111974')}")
            print(f"Shares for 9999999999: {get_shares_by_national_code('9999999999')}")
        finally:
            conn_test.close()