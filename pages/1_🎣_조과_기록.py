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

st.set_page_config(page_title="낚's - 기록")
st.title("📝 낚's 조과 기록")

try:
    points_df = pd.read_csv("points.csv")
    point_list = points_df["포인트명"].tolist()
except:
    point_list = []

try:
    gears_df = pd.read_csv("gears.csv")
    gear_list = gears_df["장비명"].tolist()
except:
    gear_list = []

with st.form("fishing_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 날짜", datetime.date.today())
        point = st.selectbox("📍 포인트 선택", point_list) if point_list else st.text_input("📍 포인트 직접 입력")
        fish_type = st.text_input("🐟 어종", placeholder="예: 감성돔")
        count = st.number_input("🔢 마릿수", min_value=1, step=1)
    with col2:
        length = st.number_input("📏 길이(cm)", min_value=0.0, step=0.1)
        weight = st.number_input("⚖️ 무게(kg)", min_value=0.0, step=0.1)
        selected_gear = st.selectbox("🎣 사용 장비", gear_list) if gear_list else st.text_input("🎣 장비 직접 입력")
        memo = st.text_area("💬 메모", placeholder="채비, 날씨 등")
    
    uploaded_files = st.file_uploader("📸 사진 업로드", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    submitted = st.form_submit_button("저장하기 🚀")
    
    if submitted:
        if not fish_type or not point:
            st.error("어종과 포인트는 필수입니다.")
        else:
            img_list = [img_to_base64(Image.open(f).convert("RGB")) for f in uploaded_files] if uploaded_files else []
            new_record = pd.DataFrame([{
                "날짜": date.strftime("%Y-%m-%d"), "포인트": point, "어종": fish_type,
                "마릿수": count, "길이": length, "무게": weight,
                "사용장비": selected_gear, "메모": memo, "사진": "|".join(img_list)
            }])
            try:
                df = pd.read_csv("fishing_data.csv")
                df = pd.concat([df, new_record], ignore_index=True)
            except:
                df = new_record
            df.to_csv("fishing_data.csv", index=False)
            st.success("기록 완료!")
            st.balloons()
