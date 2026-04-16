import streamlit as st
import pandas as pd
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# 페이지 설정 및 사이드바 제거
st.set_page_config(page_title="낚's - 조과 기록", layout="centered")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} [data-testid="stSidebarCollapseButton"] {display: none;}</style>""", unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): st.switch_page("app.py")
st.markdown("---")
st.title("🎣 조과 기록")

# --- 구글 드라이브 인증 함수 ---
def get_drive_service():
    info = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive"])
    return build('drive', 'v3', credentials=creds)

# --- 사진 업로드 함수 ---
def upload_to_drive(file, filename):
    service = get_drive_service()
    folder_id = st.secrets["google_drive"]["folder_id"]
    
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype='image/jpeg', resumable=True)
    
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return uploaded_file.get('id')

# 기초 데이터 로드
try:
    point_list = pd.read_csv("points.csv")["포인트명"].tolist()
    gear_list = pd.read_csv("gears.csv")["장비명"].tolist()
except:
    point_list, gear_list = [], []

with st.form("fishing_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 날짜", datetime.date.today())
        point = st.selectbox("📍 포인트", point_list) if point_list else st.text_input("📍 포인트 직접 입력")
        fish_type = st.text_input("🐟 어종")
        count = st.number_input("🔢 마릿수", min_value=1, step=1)
    with col2:
        length = st.number_input("📏 길이(cm)", min_value=0.0)
        weight = st.number_input("⚖️ 무게(kg)", min_value=0.0)
        gear = st.selectbox("🎣 장비", gear_list) if gear_list else st.text_input("🎣 장비 입력")
        memo = st.text_area("💬 메모")
    
    files = st.file_uploader("📸 사진 (고해상도 원본 그대로 구글 드라이브에 저장됩니다)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    if st.form_submit_button("저장하기 🚀"):
        if not fish_type:
            st.error("어종을 입력해주세요.")
        else:
            with st.spinner("사진을 구글 드라이브로 전송 중..."):
                # 구글 드라이브에 업로드 후 ID 리스트 생성
                drive_ids = []
                for idx, f in enumerate(files):
                    fname = f"{date}_{fish_type}_{idx}.jpg"
                    file_id = upload_to_drive(f, fname)
                    drive_ids.append(file_id)
                
                # 데이터 저장 (사진 컬럼에는 ID만 저장)
                new = pd.DataFrame([{
                    "날짜": date.strftime("%Y-%m-%d"), "포인트": point, "어종": fish_type, 
                    "마릿수": count, "길이": length, "무게": weight, 
                    "사용장비": gear, "메모": memo, "사진": "|".join(drive_ids)
                }])
                
                try:
                    df = pd.read_csv("fishing_data.csv")
                    df = pd.concat([df, new], ignore_index=True)
                except: df = new
                df.to_csv("fishing_data.csv", index=False)
                st.success("구글 드라이브에 원본 저장 완료!")
