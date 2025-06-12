# db.py (نسخه جدید با پشتیبانی از PostgreSQL)

import os
import psycopg2
import logging
from typing import Optional

# پیکربندی لاگ‌ها
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection() -> Optional[psycopg2.extensions.connection]:
    """برای اتصال به دیتابیس PostgreSQL با استفاده از DATABASE_URL"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # اگر این اسکریپت به صورت محلی برای وارد کردن داده‌ها اجرا شود، از متغیر دیگری استفاده می‌کند
        database_url = os.environ.get('DATABASE_URL_LOCAL')

    if not database_url:
        logger.error("آدرس دیتابیس یافت نشد. متغیر محیطی DATABASE_URL یا DATABASE_URL_LOCAL را تنظیم کنید.")
        return None

    try:
        conn = psycopg2.connect(database_url)
        logger.info("Successfully connected to PostgreSQL database.")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Error connecting to PostgreSQL database: {e}")
        return None

def create_shares_table(conn: psycopg2.extensions.connection):
    """جدول 'shares' را در دیتابیس ایجاد می‌کند اگر وجود نداشته باشد."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shares (
                id SERIAL PRIMARY KEY,
                national_code VARCHAR(10) UNIQUE NOT NULL,
                total_shares INTEGER NOT NULL
            );
        """)
        # ساخت ایندکس روی کدملی برای افزایش سرعت جستجو
        cur.execute("CREATE INDEX IF NOT EXISTS idx_national_code ON shares (national_code);")
    conn.commit()
    logger.info("Table 'shares' is ready.")

def insert_share_data(cursor, national_code, total_shares):
    """یک رکورد را در جدول درج می‌کند."""
    cursor.execute(
        "INSERT INTO shares (national_code, total_shares) VALUES (%s, %s)",
        (national_code, total_shares)
    )

def get_shares_by_national_code(national_code: str) -> Optional[int]:
    """تعداد سهام را بر اساس کدملی از دیتابیس PostgreSQL دریافت می‌کند."""
    conn = get_db_connection()
    if not conn:
        return None

    result_value = None
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT total_shares FROM shares WHERE national_code = %s",
                (national_code,)
            )
            result = cur.fetchone()
            if result:
                result_value = result[0]
    except psycopg2.Error as e:
        logger.error(f"Error querying shares for {national_code}: {e}")
    finally:
        if conn:
            conn.close()
            
    return result_value