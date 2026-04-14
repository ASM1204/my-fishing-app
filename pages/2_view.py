import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="낚's - 히스토리", layout="wide")
st.title("📜 낚's 조과 히스토리")

def display_image(image_data):
    if isinstance(image_data, str) and image_data.strip():
        try:
            img_bytes = base64.b64decode(image_data.split("|")[0])
            return st.image(img_bytes, width=300)
        except: return st.write("📷 이미지 에러")
    return st.write("📷 사진 없음")

try:
    df = pd.read_csv("fishing_data.csv")
    if df.empty:
        st.info("기록이 없습니다.")
    else:
        df = df.sort_values(by="날짜", ascending=False).reset_index(drop=True)
        # 필터 기능 추가
        fish_filter = st.multiselect("어종 필터", options=df['어종'].unique())
        display_df = df[df['어종'].isin(fish_filter)] if fish_filter else df

        for i, row in display_df.iterrows():
            with st.container():
                st.markdown("---")
                c1, c2, c3 = st.columns([1.2, 2, 0.8])
                with c1: display_image(row.get('사진'))
                with c2:
                    st.subheader(f"{row['날짜']} | {row['어종']}")
                    st.write(f"📍 {row['포인트']} | 🎣 {row.get('사용장비', '미지정')}")
                    st.write(f"📏 {row['마릿수']}마리 / {row['길이']}cm / {row['무게']}kg")
                    st.info(f"💬 {row['메모']}")
                with c3:
                    if st.button("🗑️ 삭제", key=f"del_{i}"):
                        df.drop(df.index[df['날짜']==row['날짜']].tolist()[0], inplace=True)
                        df.to_csv("fishing_data.csv", index=False)
                        st.rerun()
except:
    st.info("데이터가 없습니다.")
