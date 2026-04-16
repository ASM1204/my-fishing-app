import streamlit as st
import pandas as pd
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

st.set_page_config(page_title="낚's - 조과 기록", layout="centered")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} [data-testid="stSidebarCollapseButton"] {display: none;}</style>""", unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): st.switch_page("app.py")
st.markdown("---")
st.title("🎣 조과 기록")

def get_drive_service():
    try:
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"인증 오류: {e}")
        return None

def upload_to_drive(file, filename):
    service = get_drive_service()
    if not service: return None
    folder_id = st.secrets["google_drive"]["folder_id"]
    
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype='image/jpeg', resumable=False)
    
    try:
        # supportsAllDrives=True 옵션을 추가하여 공유된 공간의 할당량을 사용하도록 유도
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id',
            supportsAllDrives=True  # 이 옵션이 중요합니다
        ).execute()
        return uploaded_file.get('id')
    except Exception as e:
        st.error(f"업로드 오류: {e}")
        return None

# 데이터 로드 및 폼 구성 (기존과 동일)
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
    
    files = st.file_uploader("📸 사진 업로드", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    if st.form_submit_button("저장하기 🚀"):
        if not fish_type:
            st.error("어종을 입력해주세요.")
        else:
            with st.spinner("업로드 중..."):
                drive_ids = []
                for idx, f in enumerate(files):
                    fname = f"{date.strftime('%Y%m%d')}_{fish_type}_{idx}.jpg"
                    fid = upload_to_drive(f, fname)
                    if fid: drive_ids.append(fid)
                
                if len(drive_ids) == len(files):
                    new_data = pd.DataFrame([{"날짜": date.strftime("%Y-%m-%d"), "포인트": point, "어종": fish_type, "마릿수": count, "길이": length, "무게": weight, "사용장비": gear, "메모": memo, "사진": "|".join(drive_ids)}])
                    try:
                        df = pd.read_csv("fishing_data.csv")
                        df = pd.concat([df, new_data], ignore_index=True)
                    except: df = new_data
                    df.to_csv("fishing_data.csv", index=False)
                    st.success("기록 완료!")
                    st.balloons()
                else:
                    st.error("일부 업로드 실패. 구글 드라이브 설정 확인이 필요합니다.")
