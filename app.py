import streamlit as st
import requests
import pandas as pd

# ========== ต้องแก้ไขทุกครั้งที่ลิงก์เปลี่ยน ==========
NGROK_URL = "https://copy-fountain-contend.ngrok-free.dev"  # ใส่ลิงก์จากข้างบนตรงนี้
# =====================================================

st.set_page_config(page_title="Karon Real Phuket", layout="wide")
st.title("🏝️ Karon Real Phuket — ระบบจัดการห้องพัก")

# ทดสอบเชื่อมต่อ
try:
    r = requests.get(f"{NGROK_URL}/", timeout=10)
    if r.status_code == 200:
        st.success("✅ เชื่อมต่อฐานข้อมูลสำเร็จ — ข้อมูลเก็บที่เครื่องคุณ")
except Exception as e:
    st.error(f"❌ ติดต่อฐานข้อมูลไม่ได้ — ตรวจสอบว่าเครื่องเปิดและ ngrok ทำงานไหม\n{e}")
    st.stop()

menu = st.sidebar.radio("เมนูหลัก", [
    "📋 แดชบอร์ด", "🏠 จัดการห้องพัก", "📅 จัดการการจอง", "💰 รายรับ-รายจ่าย"
])

if menu == "📋 แดชบอร์ด":
    st.header("ภาพรวมระบบ")
    s = requests.get(f"{NGROK_URL}/summary").json()
    col1, col2, col3 = st.columns(3)
    col1.metric("ห้องพักทั้งหมด", s["total_prop"])
    col2.metric("ว่างให้เช่า", s["available"])
    col3.metric("คงเหลือ", f"{s['income'] - s['expense']:,.2f} บาท")

elif menu == "🏠 จัดการห้องพัก":
    st.header("ข้อมูลห้องพัก")
    with st.form("add_property"):
        name = st.text_input("ชื่อ/ชื่อห้อง")
        location = st.text_input("ที่ตั้ง")
        prop_type = st.selectbox("ประเภท", ["คอนโด", "บ้าน", "วิลล่า", "อื่นๆ"])
        price = st.number_input("ราคาต่อคืน", min_value=0.0)
        rooms = st.number_input("จำนวนห้องนอน", min_value=1)
        status = st.selectbox("สถานะ", ["ว่าง", "มีผู้เช่า", "ซ่อมบำรุง"])
        if st.form_submit_button("บันทึก"):
            requests.post(f"{NGROK_URL}/properties", json={
                "name": name, "location": location, "type": prop_type,
                "price_per_night": price, "rooms": rooms, "status": status
            })
            st.success("✅ บันทึกเรียบร้อย!")
            st.rerun()
    data = requests.get(f"{NGROK_URL}/properties").json()
    st.dataframe(pd.DataFrame(data), use_container_width=True)

elif menu == "📅 จัดการการจอง":
    st.header("การจอง")
    props = requests.get(f"{NGROK_URL}/properties").json()
    avail = [(p["id"], p["name"]) for p in props if p["status"] == "ว่าง"]
    with st.form("add_booking"):
        selected = st.selectbox("เลือกห้องพัก", avail, format_func=lambda x: x[1])
        prop_id = selected[0]
        guest = st.text_input("ชื่อผู้เข้าพัก")
        check_in = st.date_input("วันที่เช็คอิน")
        check_out = st.date_input("วันที่เช็คเอาท์")
        total = st.number_input("ราคารวม", min_value=0.0)
        if st.form_submit_button("ยืนยันการจอง"):
            requests.post(f"{NGROK_URL}/bookings", json={
                "property_id": prop_id, "guest_name": guest,
                "check_in": str(check_in), "check_out": str(check_out),
                "total_price": total, "status": "ยืนยัน"
            })
            st.success("✅ บันทึกการจองเรียบร้อย!")
            st.rerun()
    data = requests.get(f"{NGROK_URL}/bookings").json()
    st.dataframe(pd.DataFrame(data), use_container_width=True)

elif menu == "💰 รายรับ-รายจ่าย":
    st.header("บันทึกการเงิน")
    with st.form("add_transaction"):
        from datetime import datetime
        date = st.date_input("วันที่", value=datetime.now())
        t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
        category = st.text_input("หมวดหมู่")
        amount = st.number_input("จำนวนเงิน", min_value=0.0)
        note = st.text_area("หมายเหตุ")
        if st.form_submit_button("บันทึก"):
            requests.post(f"{NGROK_URL}/transactions", json={
                "date": str(date), "type": t_type, "category": category,
                "amount": amount, "note": note
            })
            st.success("✅ บันทึกเรียบร้อย!")
            st.rerun()
    s = requests.get(f"{NGROK_URL}/summary").json()
    col1, col2, col3 = st.columns(3)
    col1.metric("รวมรายรับ", f"{s['income']:,.2f} บาท")
    col2.metric("รวมรายจ่าย", f"{s['expense']:,.2f} บาท")
    col3.metric("คงเหลือ", f"{s['income'] - s['expense']:,.2f} บาท")
    data = requests.get(f"{NGROK_URL}/transactions").json()
    st.dataframe(pd.DataFrame(data), use_container_width=True)
