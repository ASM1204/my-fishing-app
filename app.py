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

# --- 구글 드라이브 실시간 사용량 및 5TB 할당량 계산 함수 ---
def get_drive_storage_info():
    try:
        # Secrets에서 서비스 계정 정보 로드
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            info, 
            scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"]
        )
        service = build('drive', 'v3', credentials=creds)
        
        # 구글 서버에서 스토리지 쿼터(할당량) 정보 요청
        about = service.about().get(fields="storageQuota").execute()
        quota = about.get("storageQuota", {})
        
        # 1. 실제 사용량 (사용자가 업로드한 만큼 실시간 반영됨)
        used_bytes = int(quota.get("usage", 0))
        used_gb = used_bytes / (1024**3)
        
        # 2. 전체 용량 (5TB 요금제 반영)
        # 서버에서 limit 값을 못 가져오거나 15GB로 제한될 경우를 대비해 5120GB(5TB)로 강제 설정 가능
        # 서버 응답값이 15GB(16106127360) 이하라면 사용자님의 실제 용량인 5TB를 우선 적용
        server_limit_bytes = int(quota.get("limit", 0))
        user_actual_limit_gb = 5120.0 # 5TB = 5120GB
        
        # 서버 응답이 유효하면 서버값을 쓰고, 아니면 5120GB 사용
        limit_gb = server_limit_bytes / (1024**3) if server_limit_bytes > (16 * 1024**3) else user_actual_limit_gb
        
        # 3. 퍼센트 계산
        percent = min(used_gb / limit_gb, 1.0)
        
        return used_gb, limit_gb, percent
    except Exception as e:
        # 에러 발생 시 5TB 기본값 반환
        return 0.0, 5120.0, 0.0

st.title("🎣 낚's")
st.subheader("나만의 스마트 조과 수첩 (Google Drive 연동)")
st.markdown("---")

# --- 용량 게이지 표시 영역 ---
used_gb, total_gb, per = get_drive_storage_info()

st.write(f"☁️ **구글 드라이브 저장 공간 ({total_gb/1024:.1f}TB 요금제)**")
st.progress(per)
st.write(f"📊 {used_gb:.2f} GB / {total_gb:.1f} GB ({per*100:.4f}%)")

# 사진이 원본으로 올라가도 5TB면 아주 넉넉하므로 소수점 4자리까지 표기하여 변화를 볼 수 있게 했습니다.
if per > 0.9:
    st.warning("⚠️ 저장 공간이 90% 이상 사용되었습니다!")

st.markdown("---")

# --- 메인 메뉴 버튼 (빠른 실행) ---
st.write("🚀 **메뉴 선택**")
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

st.markdown("---")
st.caption("현재 모든 사진은 본인의 Google Drive 폴더에 고해상도 원본으로 안전하게 저장되고 있습니다.")
