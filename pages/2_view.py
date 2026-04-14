import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="조과 기록 조회", layout="wide")

def display_image(base64_str):
    if base64_str:
        # 여러 장일 경우 첫 번째 사진만 썸네일로 표시
        first_img = base64_str.split("|")[0]
        img_data = base64.b64decode(first_img)
        return st.image(img_data, use_container_width=True)
    return st.write("📷 사진 없음")

st.title("📜 나의 조과 히스토리")

try:
    df = pd.read_csv("fishing_data.csv")
    
    if df.empty:
        st.info("아직 저장된 기록이 없습니다. 먼저 기록하기 페이지에서 등록해 주세요!")
    else:
        # 최신순 정렬 (날짜 기준)
        df = df.sort_values(by="날짜", ascending=False).reset_index(drop=True)
        
        # 삭제 기능을 위한 루프
        for i, row in df.iterrows():
            with st.container():
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    display_image(row['사진'])
                
                with col2:
                    st.subheader(f"{row['날짜']} | {row['어종']}")
                    st.write(f"📍 **포인트**: {row['포인트']}")
                    st.write(f"📏 **상세**: {row['마릿수']}마리 / {row['길이']}cm / {row['무게']}kg")
                    st.write(f"💬 **메모**: {row['메모']}")
                
                with col3:
                    # 삭제 버튼 (고유 키 생성)
                    if st.button(f"🗑️ 삭제", key=f"del_{i}"):
                        df = df.drop(i)
                        df.to_csv("fishing_data.csv", index=False)
                        st.success("삭제되었습니다!")
                        st.rerun()

except FileNotFoundError:
    st.info("데이터 파일이 아직 생성되지 않았습니다.")
