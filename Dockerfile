# Dockerfile

# 1. استفاده از یک ایمیج رسمی و سبک پایتون
FROM python:3.9-slim

# 2. تعیین پوشه کاری داخل کانتینر
WORKDIR /app

# 3. نصب پکیج‌های سیستمی مورد نیاز (برای psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# 4. کپی کردن فایل نیازمندی‌ها و نصب کتابخانه‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. کپی کردن بقیه کدهای پروژه به داخل کانتینر
COPY . .

# 6. دستوری که برای اجرای بات شما استفاده می‌شود
CMD ["python", "bot.py"]