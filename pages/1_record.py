import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import io
import base64

# 이미지 처리를 위한 함수
def img_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85) # 용량 최적화
    return base64.b64encode(buffered.getvalue()).decode()

st.title("📝 조과 기록하기")

# 입력 폼 시작
with st.form("fishing_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("날짜", datetime.date.today())
        point = st.text_input("포인트", placeholder="예: 시화방조제")
        fish_type = st.text_input("어종", placeholder="예: 우럭")
        count = st.number_input("마릿수", min_value=1, step=1)
        
    with col2:
        length = st.number_input("길이(cm)", min_value=0.0, step=0.1)
        weight = st.number_input("무게(kg)", min_value=0.0, step=0.1)
        memo = st.text_area("메모", placeholder="날씨, 채비 등 자유롭게 기록")
    
    # 여러 장의 이미지 업로드 지원
    uploaded_files = st.file_uploader("📸 사진 선택 (여러 장 가능)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    submitted = st.form_submit_button("저장하기 🚀")
    
    if submitted:
        if not fish_type or not point:
            st.error("어종과 포인트는 필수 입력 항목입니다!")
        else:
            # 이미지들을 base64 문자열 리스트로 변환
            img_list = []
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    img = Image.open(uploaded_file)
                    img = img.convert("RGB") # JPEG 변환을 위해 RGB 모드로 고정
                    img_str = img_to_base64(img)
                    img_list.append(img_str)
            
            # 리스트를 구분자(|)로 연결하여 텍스트로 저장
            all_imgs_str = "|".join(img_list)
            
            new_record = pd.DataFrame([{
                "날짜": date.strftime("%Y-%m-%d"),
                "포인트": point,
                "어종": fish_type,
                "마릿수": count,
                "길이": length,
                "무게": weight,
                "메모": memo,
                "사진": all_imgs_str
            }])
            
            # 기존 데이터 불러와서 합치기
            try:
                df = pd.read_csv("fishing_data.csv")
                df = pd.concat([df, new_record], ignore_index=True)
            except:
                df = new_record
            
            df.to_csv("fishing_data.csv", index=False)
            st.success("조과 기록이 성공적으로 저장되었습니다!")
            st.balloons() # 축하 효과
