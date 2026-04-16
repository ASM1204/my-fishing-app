import streamlit as st
import os
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 페이지 설정
st.set_page_config(page_title="낚's - HOME", layout="centered")

# --- 사이드바 제거 및 스타일 설정 ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapseButton"] { display: none; }
    .stButton>button { width: 100%; height: 60px; font-size: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 구글 드라이브 용량 정보 가져오기 함수 ---
def get_drive_storage_info():
    try:
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"])
        service = build('drive', 'v3', credentials=creds)
        
        # 드라이브 전체 용량 정보 쿼리
        about = service.about().get(fields="storageQuota").execute()
        quota = about.get("storageQuota", {})
        
        limit = int(quota.get("limit", 15 * 1024**3)) / (1024**3) # GB 단위
        usage = int(quota.get("usage", 0)) / (1024**3)           # GB 단위
        percent = min(usage / limit, 1.0)
        
        return usage, limit, percent
    except:
        return 0, 15, 0

st.title("🎣 낚's")
st.subheader("나만의 스마트 조과 수첩 (Google Drive 연동)")
st.markdown("---")

# --- 용량 게이지 표시 ---
st.write("☁️ **구글 드라이브 저장 공간 (15GB 무료)**")
used_gb, total_gb, per = get_drive_storage_info()

st.progress(per)
st.write(f"📊 {used_gb:.2f} GB / {total_gb:.1f} GB ({per*100:.1f}%)")

if per > 0.9:
    st.warning("⚠️ 구글 드라이브 용량이 거의 가득 찼습니다!")

st.markdown("---")

# --- 메뉴 이동 버튼 ---
st.write("🚀 **메뉴 선택**")
col1, col2 = st.columns(2)

with col1:
    if st.button("🗺️ 지도 보기"): st.switch_page("pages/0_🗺️_지도.py")
    if st.button("🎣 조과 기록"): st.switch_page("pages/1_🎣_조과_기록.py")

with col2:
    if st.button("📜 히스토리"): st.switch_page("pages/2_📜_조과_히스토리.py")
    if st.button("📊 데이터 분석"): st.switch_page("pages/3_📊_분석.py")

if st.button("🛠️ 장비 및 설정 관리"): st.switch_page("pages/4_🛠️_장비.py")
