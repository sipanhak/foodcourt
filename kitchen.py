import streamlit as st
from streamlit_autorefresh import st_autorefresh
import json
import os

st.set_page_config(page_title="Խոհանոց - Տերմինալ", page_icon="🍳", layout="wide")

# Ավտոթարմացում 5 վայրկյանը մեկ
st_autorefresh(interval=5000, limit=None, key="kitchen_autorefresh")

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

st.title("🍳 Խոհանոցի տերմինալ — Մուտքային պատվերներ")

# Ձայնի ակտիվացման կոճակ
if "sound_allowed" not in st.session_state:
    st.session_state.sound_allowed = False

if not st.session_state.sound_allowed:
    if st.button("🔊 Միացնել ձայնային ազդանշանները (Սեղմեք սկզբում)", type="primary"):
        st.session_state.sound_allowed = True
        st.rerun()
else:
    st.success("✅ Ձայնային ազդանշանն ակտիվ է")

if st.button("🔄 Թարմացնել պատվերները"):
    st.rerun()

orders = load_orders()

# Ստուգում ենք՝ կան նոր պատվերներ, թե ոչ
has_new_orders = any(o.get("status") == "🆕 Նոր" for o in orders)

if has_new_orders:
    st.warning("🔔 Ուշադրություն! Կան նոր պատվերներ:")
    
    if st.session_state.sound_allowed:
        audio_url = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"
        st.markdown(f"""
            <audio autoplay>
                <source src="{audio_url}" type="audio/mpeg">
            </audio>
        """, unsafe_allow_html=True)

if not orders:
    st.info("Ակտիվ պատվերներ չկան։")
else:
    for index, order in enumerate(reversed(orders)):
        status = order.get("status", "🆕 Նոր")
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                order_num = order['id'] % 10000 if isinstance(order['id'], int) else order['id']
                st.write(f"### Պատվեր #{order_num}")
                st.write(f"**Կարգավիճակը:** {status}")
                
                # 👈 Ավելացրինք հաճախորդի տվյալների արտածումը խոհանոցում
                st.markdown("---")
                st.write(f"👤 **Անուն:** {order.get('client_name', 'Անհայտ')}")
                st.write(f"📞 **Հեռ.:** {order.get('client_phone', 'Նշված չէ')}")
                st.write(f"👤 **Անուն:** {order.get('client_name', 'Անհայտ')}")
                st.write(f"📞 **Հեռ.:** {order.get('client_phone', 'Նշված չէ')}")
                st.write(f"🛵 **Տեսակը:** {order.get('order_type', 'Մոտենալ վերցնել')}")

            if order.get("order_type") == "Առաքում":
                st.write(f"📍 **Հասցե:** {order.get('address', 'Նշված չէ')}")
            
            with col2:
                st.write("**Պատվերի բաղադրությունը:**")
                for item_id, data in order["items"].items():
                    st.write(f"- {data['name']} x {data['qty']}")
                st.write(f"**Գումարը:** {order['total']} դր.")
            
            with col3:
                st.write("**Փոխել կարգավիճակը:**")
                real_index = len(orders) - 1 - index
                
                if status == "🆕 Նոր":
                    if st.button("Ընդունել աշխատանքի ⏳", key=f"btn_1_{order['id']}"):
                        orders[real_index]["status"] = "⏳ Պատրաստվում է"
                        save_orders(orders)
                        st.rerun()
                elif status == "⏳ Պատրաստվում է":
                    if st.button("Պատրաստ է ✅", key=f"btn_2_{order['id']}"):
                        orders[real_index]["status"] = "✅ Պատրաստ է"
                        save_orders(orders)
                        st.rerun()
                elif status == "✅ Պատրաստ է":
                    if st.button("Հեռացնել արխիվից 🗑️", key=f"btn_3_{order['id']}"):
                        orders.pop(real_index)
                        save_orders(orders)
                        st.rerun()