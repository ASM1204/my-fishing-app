import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="낚's - 히스토리", layout="wide")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} [data-testid="stSidebarCollapseButton"] {display: none;}</style>""", unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): st.switch_page("app.py")
st.markdown("---")

st.title("📜 조과 히스토리")

try:
    df = pd.read_csv("fishing_data.csv")
    if df.empty: st.info("기록이 없습니다.")
    else:
        df = df.sort_values(by="날짜", ascending=False)
        for i, row in df.iterrows():
            with st.container():
                st.markdown("---")
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    if isinstance(row['사진'], str) and row['사진']:
                        st.image(base64.b64decode(row['사진'].split("|")[0]), width=250)
                with c2:
                    st.subheader(f"{row['날짜']} | {row['어종']}")
                    st.write(f"📍 {row['포인트']} | 📏 {row['길이']}cm")
                    st.info(row['메모'])
                with c3:
                    if st.button("🗑️ 삭제", key=f"del_{i}"):
                        df.drop(i).to_csv("fishing_data.csv", index=False)
                        st.rerun()
except: st.info("기록이 없습니다.")
