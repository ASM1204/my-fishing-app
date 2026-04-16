import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import io
import base64

def img_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85) 
    return base64.b64encode(buffered.getvalue()).decode()

st.set_page_config(page_title="낚's - 조과 기록")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} [data-testid="stSidebarCollapseButton"] {display: none;}</style>""", unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): st.switch_page("app.py")
st.markdown("---")

st.title("🎣 조과 기록")

try:
    point_list = pd.read_csv("points.csv")["포인트명"].tolist()
    gear_list = pd.read_csv("gears.csv")["장비명"].tolist()
except:
    point_list, gear_list = [], []

with st.form("fishing_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 날짜", datetime.date.today())
        point = st.selectbox("📍 포인트", point_list) if point_list else st.text_input("📍 포인트 직접 입력")
        fish_type = st.text_input("🐟 어종")
        count = st.number_input("🔢 마릿수", min_value=1, step=1)
    with col2:
        length = st.number_input("📏 길이(cm)", min_value=0.0)
        weight = st.number_input("⚖️ 무게(kg)", min_value=0.0)
        gear = st.selectbox("🎣 장비", gear_list) if gear_list else st.text_input("🎣 장비 입력")
        memo = st.text_area("💬 메모")
    
    files = st.file_uploader("📸 사진", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    if st.form_submit_button("저장하기 🚀"):
        img_list = [img_to_base64(Image.open(f).convert("RGB")) for f in files] if files else []
        new = pd.DataFrame([{"날짜": date.strftime("%Y-%m-%d"), "포인트": point, "어종": fish_type, "마릿수": count, "길이": length, "무게": weight, "사용장비": gear, "메모": memo, "사진": "|".join(img_list)}])
        try:
            df = pd.read_csv("fishing_data.csv")
            df = pd.concat([df, new], ignore_index=True)
        except: df = new
        df.to_csv("fishing_data.csv", index=False)
        st.success("저장 완료!")
