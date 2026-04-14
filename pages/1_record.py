import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import io
import base64

st.set_page_config(page_title="조과 기록")

def img_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

st.title("📝 새로운 조과 기록")

with st.form("fishing_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.date.today())
        fish_type = st.text_input("어종")
        count = st.number_input("마릿수", min_value=1, step=1)
    with col2:
        point = st.text_input("포인트")
        length = st.number_input("길이(cm)", min_value=0.0, step=0.1)
        weight = st.number_input("무게(kg)", min_value=0.0, step=0.1)
    
    memo = st.text_area("메모")
    uploaded_files = st.file_uploader("사진 선택 (여러 장 가능)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    submitted = st.form_submit_button("저장하기")
    
    if submitted:
        # 이미지 처리 (첫 번째 이미지만 저장하거나 리스트로 저장 가능)
        img_str = ""
        if uploaded_files:
            img = Image.open(uploaded_files[0])
            img = img.convert("RGB") # JPEG 변환
            img_str = img_to_base64(img)
            
        new_data = pd.DataFrame([{
            "날짜": date, "포인트": point, "어종": fish_type, 
            "마릿수": count, "길이": length, "무게": weight, 
            "메모": memo, "사진": img_str
        }])
        
        try:
            df = pd.read_csv("fishing_data.csv")
            df = pd.concat([df, new_data], ignore_index=True)
        except:
            df = new_data
            
        df.to_csv("fishing_data.csv", index=False)
        st.success("성공적으로 저장되었습니다!")
