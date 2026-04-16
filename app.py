import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="낚's - HOME", layout="centered")

# --- 스타일 설정 ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 타이틀 ---
st.title("🎣 낚's")
st.subheader("나만의 스마트 조과 수첩")
st.markdown("---")

# --- 용량 계산 및 게이지 표기 ---
def get_storage_info(file_path, total_capacity_mb=50.0):
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        used_mb = size_bytes / (1024 * 1024)
    else:
        used_mb = 0.0
    
    percent = min(used_mb / total_capacity_mb, 1.0)
    return used_mb, total_capacity_mb, percent

st.write("📂 **데이터 저장소 사용량**")
used, total, per = get_storage_info("fishing_data.csv")

# 게이지 바
st.progress(per)
# 아래 줄의 오타(.1True -> .1f)를 수정했습니다.
st.write(f"📊 {used:.2f} MB / {total:.1f} MB ({per*100:.1f}%)")

if per > 0.8:
    st.warning("⚠️ 저장 공간이 얼마 남지 않았습니다. 사진 관리가 필요합니다.")

st.markdown("---")

# --- 각 화면 이동 버튼 ---
st.write("🚀 **빠른 실행**")
col1, col2 = st.columns(2)

with col1:
    if st.button("🗺️ 지도 보기"):
        st.switch_page("pages/0_🗺️_지도.py")
    if st.button("🎣 조과 기록"):
        st.switch_page("pages/1_🎣_조과_기록.py")

with col2:
    if st.button("📜 히스토리"):
        st.switch_page("pages/2_📜_조과_히스토리.py")
    if st.button("📊 데이터 분석"):
        st.switch_page("pages/3_📊_분석.py")

if st.button("🛠️ 장비 및 설정 관리"):
    st.switch_page("pages/4_🛠️_장비.py")

st.sidebar.info("왼쪽 메뉴를 통해서도 이동이 가능합니다.")
