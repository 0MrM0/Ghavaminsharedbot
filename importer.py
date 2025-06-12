# importer.py (جایگزین xlsx_loader.py برای وارد کردن داده به PostgreSQL)

import pandas as pd
import os
from dotenv import load_dotenv
import db # از ماژول db جدید استفاده می‌کنیم

# --- تنظیمات ---
# فایل اکسل شما باید کنار این اسکریپت باشد
EXCEL_FILE_NAME = "saham.end.xlsx"
NATIONAL_CODE_COLUMN = "کد ملی"
TOTAL_SHARES_COLUMN = "تعدادكل سهام"

def import_excel_to_postgres():
    """فایل اکسل را می‌خواند و داده‌ها را به دیتابیس PostgreSQL وارد می‌کند."""
    load_dotenv() # برای خواندن فایل .env

    if not os.path.exists(EXCEL_FILE_NAME):
        print(f"خطا: فایل اکسل '{EXCEL_FILE_NAME}' یافت نشد.")
        return

    conn = db.get_db_connection()
    if not conn:
        print("اتصال به دیتابیس برقرار نشد. لطفاً فایل .env و آدرس دیتابیس را بررسی کنید.")
        return

    try:
        # ساخت جدول اگر وجود نداشته باشد
        db.create_shares_table(conn)

        print(f"در حال خواندن فایل اکسل '{EXCEL_FILE_NAME}'...")
        df = pd.read_excel(EXCEL_FILE_NAME)
        
        # پاکسازی داده‌ها
        df.dropna(subset=[NATIONAL_CODE_COLUMN, TOTAL_SHARES_COLUMN], inplace=True)
        df = df[pd.to_numeric(df[NATIONAL_CODE_COLUMN], errors='coerce').notnull()]
        df = df[pd.to_numeric(df[TOTAL_SHARES_COLUMN], errors='coerce').notnull()]
        df[NATIONAL_CODE_COLUMN] = df[NATIONAL_CODE_COLUMN].astype(str).str.strip()
        df[TOTAL_SHARES_COLUMN] = df[TOTAL_SHARES_COLUMN].astype(int)

        print(f"تعداد {len(df)} رکورد معتبر برای وارد کردن یافت شد.")
        print("شروع فرآیند وارد کردن داده‌ها به دیتابیس... (این کار ممکن است طولانی باشد)")

        with conn.cursor() as cur:
            # استفاده از یک روش بهینه برای درج تعداد زیاد رکورد
            from psycopg2.extras import execute_values
            
            data_tuples = list(df[[NATIONAL_CODE_COLUMN, TOTAL_SHARES_COLUMN]].itertuples(index=False, name=None))
            
            # ON CONFLICT (national_code) DO UPDATE برای جلوگیری از خطای کدملی تکراری
            # اگر کدملی وجود داشت، تعداد سهام آن را آپدیت می‌کند
            query = """
                INSERT INTO shares (national_code, total_shares) VALUES %s
                ON CONFLICT (national_code) DO UPDATE SET total_shares = EXCLUDED.total_shares;
            """
            
            execute_values(cur, query, data_tuples)
            conn.commit()

        print(f"\n✅ تمام {len(df)} رکورد با موفقیت به دیتابیس PostgreSQL منتقل شد.")

    except FileNotFoundError:
        print(f"خطا: فایل '{EXCEL_FILE_NAME}' پیدا نشد.")
    except KeyError as e:
        print(f"خطا: ستون مورد نظر یافت نشد. {e}")
    except Exception as e:
        print(f"یک خطای غیرمنتظره رخ داد: {e}")
        conn.rollback() # در صورت بروز خطا، تغییرات را لغو کن
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    import_excel_to_postgres()