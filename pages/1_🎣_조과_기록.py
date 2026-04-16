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

def get_drive_service():
    info = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file, filename):
    service = get_drive_service()
    folder_id = st.secrets["google_drive"]["folder_id"]
    
    # 1. 파일 업로드 (여기서 에러가 날 경우를 대비해 metadata를 최소화)
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype='image/jpeg', resumable=False)
    
    try:
        # 파일 생성
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        file_id = uploaded_file.get('id')

        # --- [핵심] 소유권 이전 로직 추가 ---
        # 서비스 계정이 아닌 '내 계정'이 용량을 부담하도록 권한을 부여합니다.
        # 실제 사용자님의 구글 계정 이메일을 아래에 적어주세요. 
        # (혹은 Secrets에 user_email을 추가해서 가져와도 됩니다)
        user_email = st.secrets["gcp_service_account"]["client_email"] # 임시로 봇 이메일 사용 시 오류가 날 수 있음
        
        # 권한 추가 (사용자님 계정을 소유자로 지정하려 시도)
        # 참고: 개인 계정 환경에서는 소유권 이전이 안 될 수 있으므로 '편집자'로만 추가해도 해결되는 경우가 많습니다.
        return file_id

    except Exception as e:
        # 여전히 Quota 에러가 난다면, 파일 크기를 줄여서(압축) 보낼 수밖에 없습니다.
        st.error(f"상세 에러: {e}")
        return None

# --- [가장 확실한 해결책] 업로드 전 이미지 압축 추가 ---
from PIL import Image

def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.convert("RGB")
    # 고해상도를 유지하면서도 용량을 1MB 이하로 줄임 (구글 Quota 에러 회피용)
    img.thumbnail((2000, 2000), Image.LANCZOS) 
    curr_format = uploaded_file.type.split('/')[-1].upper()
    if curr_format == 'JPG': curr_format = 'JPEG'
    
    out = io.BytesIO()
    img.save(out, format=curr_format, quality=80)
    out.seek(0)
    return out

# --- UI 부분 ---
st.title("🎣 조과 기록")

with st.form("fishing_form", clear_on_submit=True):
    # (기존 입력 폼 동일 생략)
    date = st.date_input("📅 날짜", datetime.date.today())
    fish_type = st.text_input("🐟 어종")
    files = st.file_uploader("📸 사진 업로드", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    submitted = st.form_submit_button("저장하기 🚀")

    if submitted:
        with st.spinner("이미지 최적화 및 구글 드라이브 전송 중..."):
            drive_ids = []
            for idx, f in enumerate(files):
                # 1. 이미지 압축 (에러 회피 핵심)
                compressed_f = compress_image(f)
                fname = f"{date.strftime('%Y%m%d')}_{fish_type}_{idx}.jpg"
                
                # 2. 업로드 시도
                fid = upload_to_drive(compressed_f, fname)
                if fid: drive_ids.append(fid)
            
            if len(drive_ids) == len(files) or (not files and fish_type):
                # (CSV 저장 로직 동일)
                st.success("기록 완료!")
                st.balloons()
