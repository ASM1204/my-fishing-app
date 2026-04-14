import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="조과 기록 조회", layout="wide")

def display_image(image_data):
    # 데이터가 비어있는지(문자열이 아닌지) 체크
    if isinstance(image_data, str) and image_data.strip():
        try:
            # 여러 장일 경우 첫 번째 사진만 썸네일로 표시
            first_img = image_data.split("|")[0]
            img_bytes = base64.b64decode(first_img)
            return st.image(img_bytes, use_container_width=True)
        except:
            return st.write("📷 이미지 불러오기 실패")
    return st.write("📷 사진 없음")

st.title("📜 나의 조과 히스토리")

try:
    df = pd.read_csv("fishing_data.csv")
    
    if df.empty:
        st.info("기록된 데이터가 없습니다.")
    else:
        # 최신순 정렬
        df = df.sort_values(by="날짜", ascending=False).reset_index(drop=True)
        
        for i, row in df.iterrows():
            with st.container():
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    # 사진 컬럼의 데이터를 안전하게 전달
                    display_image(row.get('사진'))
                
                with col2:
                    st.subheader(f"{row['날짜']} | {row['어종']}")
                    st.write(f"📍 **포인트**: {row['포인트']}")
                    st.write(f"📏 **상세**: {row['마릿수']}마리 / {row['길이']}cm / {row['무게']}kg")
                    st.write(f"💬 **메모**: {row['메모']}")
                
                with col3:
                    if st.button(f"🗑️ 삭제", key=f"del_{i}"):
                        df = df.drop(i)
                        df.to_csv("fishing_data.csv", index=False)
                        st.success("삭제 완료!")
                        st.rerun()

except FileNotFoundError:
    st.info("기록하기 페이지에서 첫 데이터를 만들어보세요!")
