# xlsx_loader.py
# این فایل مسئول خواندن فایل XLSX و ذخیره داده‌ها در دیتابیس است.

import pandas as pd
import os
import db # import the db.py module

# نام فایل اکسل ورودی (مطمئن شوید که در همین پوشه قرار دارد)
EXCEL_FILE_NAME = "saham.end.xlsx" # تغییر نام داده شده از "saham.end.xlsx - Sheet1.csv"
EXCEL_SHEET_NAME = "Sheet1" # نام شیتی که داده‌ها در آن قرار دارند

# نام ستون‌های مورد نیاز در فایل اکسل (دقیقاً همانطور که در فایل نوشته شده‌اند)
NATIONAL_CODE_COLUMN = "کد ملی"
TOTAL_SHARES_COLUMN = "تعدادكل سهام"

def load_excel_data_to_db(excel_file: str, sheet_name: str):
    """
    فایل اکسل را می‌خواند، داده‌های مربوطه را استخراج و پاکسازی می‌کند،
    سپس آن‌ها را در یک دیتابیس SQLite ذخیره می‌نماید.
    اتصال به دیتابیس در ابتدای تابع باز و در انتها بسته می‌شود.
    """
    if not os.path.exists(excel_file):
        print(f"خطا: فایل اکسل '{excel_file}' یافت نشد.")
        print("لطفاً فایل اکسل را در کنار این اسکریپت قرار دهید یا مسیر آن را تصحیح کنید.")
        return

    conn = None # مقداردهی اولیه برای اطمینان از بسته شدن در صورت بروز خطا
    try:
        conn = db.get_db_connection()
        if not conn:
            print("خطا: نتوانستیم به دیتابیس متصل شویم. عملیات بارگذاری متوقف شد.")
            return

        db.create_shares_table(conn) # اطمینان از وجود جدول با استفاده از اتصال باز

        # خواندن فایل اکسل با استفاده از pandas
        df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype={NATIONAL_CODE_COLUMN: str}, engine='openpyxl')
        print(f"فایل '{excel_file}' و شیت '{sheet_name}' با موفقیت خوانده شد.")

        # بررسی وجود ستون‌های مورد نیاز
        if NATIONAL_CODE_COLUMN not in df.columns or TOTAL_SHARES_COLUMN not in df.columns:
            print(f"خطا: ستون‌های '{NATIONAL_CODE_COLUMN}' یا '{TOTAL_SHARES_COLUMN}' در فایل اکسل یافت نشدند.")
            print("لطفاً از صحت نام ستون‌ها در فایل اکسل اطمینان حاصل کنید (دقیقاً باید مطابق باشند).")
            return

        # فیلتر کردن ستون‌های مورد نیاز و پاکسازی داده‌ها
        df_filtered = df[[NATIONAL_CODE_COLUMN, TOTAL_SHARES_COLUMN]].copy()
        df_filtered.dropna(subset=[NATIONAL_CODE_COLUMN, TOTAL_SHARES_COLUMN], inplace=True)
        print(f"تعداد ردیف‌های معتبر پس از حذف مقادیر خالی: {len(df_filtered)}")

        df_filtered[NATIONAL_CODE_COLUMN] = df_filtered[NATIONAL_CODE_COLUMN].astype(str).str.strip()
        df_filtered[TOTAL_SHARES_COLUMN] = pd.to_numeric(df_filtered[TOTAL_SHARES_COLUMN], errors='coerce')
        df_filtered.dropna(subset=[TOTAL_SHARES_COLUMN], inplace=True)
        df_filtered[TOTAL_SHARES_COLUMN] = df_filtered[TOTAL_SHARES_COLUMN].astype(int)

        cursor = conn.cursor() # ایجاد یک cursor از اتصال باز

        inserted_count = 0
        print("در حال وارد کردن داده‌ها به دیتابیس... (این کار ممکن است کمی طول بکشد)")
        for index, row in df_filtered.iterrows():
            national_code = row[NATIONAL_CODE_COLUMN]
            total_shares = row[TOTAL_SHARES_COLUMN]
            db.insert_or_replace_share_data(cursor, national_code, total_shares) # استفاده از cursor موجود
            inserted_count += 1
            if inserted_count % 10000 == 0: # نمایش پیشرفت هر 10000 ردیف
                print(f"  {inserted_count} ردیف وارد شد.")

        conn.commit() # Commit کردن تمام تغییرات پس از اتمام حلقه
        print(f"\nپردازش داده‌ها به پایان رسید.")
        print(f"تعداد کل ردیف‌های با موفقیت ذخیره شده در دیتابیس: {inserted_count}")
        print(f"داده‌ها با موفقیت از اکسل به دیتابیس '{db.DATABASE_NAME}' منتقل شدند.")

    except FileNotFoundError:
        print(f"خطا: فایل '{excel_file}' پیدا نشد.")
    except KeyError as e:
        print(f"خطا: ستون مورد نظر یافت نشد. {e}")
        print("لطفاً از صحت نام ستون‌ها در فایل اکسل اطمینان حاصل کنید.")
    except Exception as e:
        print(f"خطای غیرمنتظره در پردازش فایل اکسل: {e}")
    finally:
        if conn:
            conn.close() # بستن اتصال در هر صورت

if __name__ == "__main__":
    load_excel_data_to_db(EXCEL_FILE_NAME, EXCEL_SHEET_NAME)