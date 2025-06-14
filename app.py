import streamlit as st
import db  # استفاده از db.py برای ارتباط با دیتابیس

st.set_page_config(page_title="استعلام تعداد سهام", page_icon="📊", layout="centered")

st.title("📊 سامانه استعلام سهام قوامین")
st.markdown("با وارد کردن کدملی، تعداد سهام خود را مشاهده کنید.")

# فرم ورود کدملی
with st.form("search_form"):
    national_code = st.text_input("کد ملی:", max_chars=20)
    submitted = st.form_submit_button("جستجو")

if submitted:
    if not national_code.strip().isdigit():
        st.warning("لطفاً فقط عدد وارد کنید.")
    else:
        shares = db.get_shares_by_national_code(national_code.strip())
        if shares is not None:
            st.success(f"✅ کدملی {national_code} دارای {shares:,} سهم است.")
        else:
            st.error(f"❌ هیچ داده‌ای برای کدملی {national_code} یافت نشد.")
