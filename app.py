import streamlit as st
import os
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="낚's - HOME", layout="centered")

# --- 사이드바 제거 및 버튼 스타일 설정 ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapseButton"] { display: none; }
    .stButton>button { width: 100%; height: 60px; font-size: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎣 낚's")
st.subheader("나만의 스마트 조과 수첩")
st.markdown("---")

# --- 용량 게이지 ---
def get_storage_info(file_path, total_capacity_mb=50.0):
    used_mb = os.path.getsize(file_path) / (1024 * 1024) if os.path.exists(file_path) else 0.0
    return used_mb, total_capacity_mb, min(used_mb / total_capacity_mb, 1.0)

used, total, per = get_storage_info("fishing_data.csv")
st.write("📂 **데이터 저장소 사용량**")
st.progress(per)
st.write(f"📊 {used:.2f} MB / {total:.1f} MB ({per*100:.1f}%)")

st.markdown("---")

# --- 메뉴 버튼 ---
st.write("🚀 **메뉴 선택**")
col1, col2 = st.columns(2)
with col1:
    if st.button("🗺️ 지도 보기"): st.switch_page("pages/0_🗺️_지도.py")
    if st.button("🎣 조과 기록"): st.switch_page("pages/1_🎣_조과_기록.py")
with col2:
    if st.button("📜 히스토리"): st.switch_page("pages/2_📜_조과_히스토리.py")
    if st.button("📊 데이터 분석"): st.switch_page("pages/3_📊_분석.py")

if st.button("🛠️ 장비 및 설정 관리"): st.switch_page("pages/4_🛠️_장비.py")
