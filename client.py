import streamlit as st
from streamlit_autorefresh import st_autorefresh
import json
import os
import time
import re
import random

st.set_page_config(page_title="Ֆուդ-կորտ - Հաճախորդ", page_icon="🍔", layout="wide")

st_autorefresh(interval=10000, limit=None, key="client_autorefresh")

ORDERS_FILE = "orders.json"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=4)

def is_valid_name(name):
    pattern = r"^[a-zA-Zа-яА-Яա-ֆԱ-Ֆե-ևԷ-Ֆ\s]+$"
    return bool(re.match(pattern, name.strip()))

def is_valid_arm_phone(phone):
    clean_phone = re.sub(r"[\s\-\(\)]", "", phone.strip())
    pattern = r"^(?:\+374|0)(33|41|43|44|55|77|91|93|94|95|96|98|99|10|11|12)\d{6}$"
    return bool(re.match(pattern, clean_phone))

st.title("🍔 Ֆուդ-կորտ: Կատարեք պատվեր")

if "cart" not in st.session_state:
    st.session_state.cart = {}
if "my_order_ids" not in st.session_state:
    st.session_state.my_order_ids = []
if "sms_code" not in st.session_state:
    st.session_state.sms_code = None
if "phone_verified" not in st.session_state:
    st.session_state.phone_verified = False

products = [
    {"id": "1", "name": "Բուրգեր Կլասիկ", "price": 1500.0, "category": "Արագ սնունդ", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400"},
    {"id": "2", "name": "Ֆրի Կարտոֆիլ", "price": 700.0, "category": "Արագ սնունդ", "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400"},
    {"id": "3", "name": "Կոլա 0.5", "price": 500.0, "category": "Ըմպելիքներ", "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400"},
    {"id": "4", "name": "Պիցցա Պեպերոնի", "price": 2800.0, "category": "Պիցցա", "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400"},
]

col_menu, col_cart = st.columns([2, 1])

with col_menu:
    st.subheader("Մենյու")
    category_filter = st.selectbox("Կատեգորիա", ["Բոլորը", "Արագ սնունդ", "Ըմպելիքներ", "Պիցցա"])

    for item in products:
        if category_filter == "Բոլորը" or item["category"] == category_filter:
            with st.container(border=True):
                col_img, col_info, col_btn = st.columns([1.5, 3, 2])
                with col_img:
                    st.image(item["image"], use_container_width=True)
                with col_info:
                    st.write(f"### {item['name']}")
                    st.write(f"**Գինը:** {item['price']} դր.")
                with col_btn:
                    if st.button("Ավելացնել 🛒", key=f"add_{item['id']}", use_container_width=True):
                        item_id = item["id"]
                        if item_id in st.session_state.cart:
                            st.session_state.cart[item_id]["qty"] += 1
                        else:
                            st.session_state.cart[item_id] = {"name": item["name"], "price": item["price"], "qty": 1}
                        st.toast(f"Ավելացվեց՝ {item['name']}")

with col_cart:
    st.subheader("🛒 Ձեր զամբյուղը")
    if len(st.session_state.cart) == 0:
        st.info("Զամբյուղը դատարկ է")
    else:
        subtotal_price = 0
        for item_id, data in list(st.session_state.cart.items()):
            subtotal = data["price"] * data["qty"]
            subtotal_price += subtotal
            st.write(f"• **{data['name']}** x {data['qty']} = {subtotal} դր.")
            
            cc1, cc2 = st.columns(2)
            if cc1.button("➖", key=f"m_{item_id}"):
                if data["qty"] > 1:
                    st.session_state.cart[item_id]["qty"] -= 1
                else:
                    del st.session_state.cart[item_id]
                st.rerun()
            if cc2.button("➕", key=f"p_{item_id}"):
                st.session_state.cart[item_id]["qty"] += 1
                st.rerun()

        st.markdown("---")
        
        # 🛵 ՊԱՏՎԵՐԻ ՏԵՍԱԿԻ ԸՆՏՐՈՒԹՅՈՒՆ (Առաքում թե Մոտենալ վերցնել)
        st.subheader("🛵 Պատվերի եղանակը")
        order_type = st.radio("Ընտրեք տարբերակը:", ["🛍️ Մոտենալ վերցնել", "🚚 Առաքում (+500 դր.)"])

        delivery_fee = 0
        address = ""

        if order_type == "🚚 Առաքում (+500 դր.)":
            delivery_fee = 500
            address = st.text_input("Առաքման հասցեն", placeholder="Օր.՝ Աբովյան փող., տուն 12, բն. 4")

        st.markdown("---")
        st.subheader("👤 Ձեր տվյալները")
        client_name = st.text_input("Անուն", placeholder="Օր.՝ Արման")
        client_phone = st.text_input("Հեռախոսահամար", placeholder="Օր.՝ +374 91 123456")

        # SMS-ՍՏՈՒԳՈՒՄ
        if not st.session_state.phone_verified:
            if st.button("📩 Ուղարկել SMS հաստատման կոդ"):
                if not client_name.strip() or not is_valid_name(client_name):
                    st.error("❌ Խնդրում ենք մուտքագրել ճիշտ անուն (միայն տառերով)։")
                elif not is_valid_arm_phone(client_phone):
                    st.error("❌ Մուտքագրեք վավեր հայկական հեռախոսահամար։")
                elif order_type == "🚚 Առաքում (+500 դր.)" and not address.strip():
                    st.error("❌ Խնդրում ենք լրացնել առաքման հասցեն։")
                else:
                    st.session_state.sms_code = str(random.randint(1000, 9999))
                    st.info(f"📲 [ԹԵՍՏԱՅԻՆ] Ձեր SMS կոդն է՝ **{st.session_state.sms_code}**")

            if st.session_state.sms_code:
                user_entered_code = st.text_input("Մուտքագրեք SMS-ով ստացված 4-նիշ կոդը", max_chars=4)
                if st.button("✅ Հաստատել կոդը"):
                    if user_entered_code == st.session_state.sms_code:
                        st.session_state.phone_verified = True
                        st.success("🎉 Համարը հաջողությամբ հաստատվեց։")
                        st.rerun()
                    else:
                        st.error("❌ Սխալ SMS կոդ։")
        else:
            st.success("✅ Հեռախոսահամարը հաստատված է")

        # ԳՈՒՄԱՐՆԵՐԻ ՀԱՇՎԱՐԿ
        final_total = subtotal_price + delivery_fee
        st.write(f"Ապրանքների գումարը՝ **{subtotal_price} դր.**")
        if delivery_fee > 0:
            st.write(f"Առաքման վճար՝ **{delivery_fee} դր.**")
        st.write(f"### Ընդհանուր՝ {final_total} դր.")
        
        if st.button("Ձևակերպել պատվերը", type="primary", use_container_width=True, disabled=not st.session_state.phone_verified):
            if order_type == "🚚 Առաքում (+500 դր.)" and not address.strip():
                st.error("❌ Խնդրում ենք լրացնել առաքման հասցեն։")
            else:
                orders = load_orders()
                order_id = int(time.time())
                new_order = {
                    "id": order_id,
                    "client_name": client_name.strip(),
                    "client_phone": client_phone.strip(),
                    "order_type": "Առաքում" if delivery_fee > 0 else "Մոտենալ վերցնել",
                    "address": address.strip() if delivery_fee > 0 else "Տեղում/Վերցնել",
                    "items": st.session_state.cart.copy(),
                    "subtotal": subtotal_price,
                    "delivery_fee": delivery_fee,
                    "total": final_total,
                    "status": "🆕 Նոր"
                }
                orders.append(new_order)
                save_orders(orders)
                
                st.session_state.my_order_ids.append(order_id)
                st.session_state.cart.clear()
                st.session_state.phone_verified = False
                st.session_state.sms_code = None
                
                st.success(f"Պատվեր #{order_id % 10000} ուղարկվեց խոհանոց!")
                st.rerun()

    if st.session_state.my_order_ids:
        st.markdown("---")
        st.subheader("📋 Ձեր պատվերները")
        if st.button("🔄 Թարմացնել կարգավիճակը"):
            st.rerun()

        all_orders = {o["id"]: o for o in load_orders()}
        for oid in reversed(st.session_state.my_order_ids):
            order_info = all_orders.get(oid)
            if order_info:
                st.info(f"Պատվեր #{oid % 10000} — **{order_info['status']}**")
            else:
                st.write(f"Պատվեր #{oid % 10000} (ավարտված է/ջնջված)")