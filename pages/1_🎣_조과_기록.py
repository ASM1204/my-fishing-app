import streamlit as st
import pandas as pd
import datetime
import json
import io
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="낚's - 조과 기록", layout="centered")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} [data-testid="stSidebarCollapseButton"] {display: none;}</style>""", unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): 
    st.switch_page("app.py")

st.title("🎣 조과 기록 (영구 로그인 모드)")

# 토큰 저장 파일 경로
TOKEN_FILE = 'token.json'

# --- 영구 로그인 인증 로직 ---
def get_drive_service():
    client_config = json.loads(st.secrets["google_oauth"]["client_secrets_json"])
    scopes = ['https://www.googleapis.com/auth/drive.file']
    creds = None

    # 1. 파일에 저장된 기존 토큰이 있는지 확인
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)
        except Exception:
            os.remove(TOKEN_FILE)

    # 2. 토큰이 없거나 만료된 경우
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 토큰 만료 시 자동 갱신
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception:
                creds = None
        
        if not creds:
            # 완전히 새로 로그인해야 하는 경우
            redirect_uri = "https://my-fishing.streamlit.app/"
            flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_uri)
            
            auth_code = st.query_params.get("code")
            if auth_code:
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                # 중요: 리프레시 토큰을 포함하여 파일로 저장
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                st.query_params.clear()
                st.rerun()
            else:
                # 로그인 버튼 표시 (offline 모드로 리프레시 토큰 강제 획득)
                auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
                st.info("💡 최초 1회 구글 인증이 필요합니다. 이후에는 자동으로 로그인됩니다.")
                st.link_button("🔑 구글 로그인 및 자동 로그인 등록", auth_url)
                return None

    return build('drive', 'v3', credentials=creds)

# --- 이미지 최적화 및 업로드 ---
def optimize_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((2000, 2000), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85, optimize=True)
    out.seek(0)
    return out

def upload_to_drive(service, optimized_file, filename):
    folder_id = st.secrets["google_drive"]["folder_id"]
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(optimized_file, mimetype='image/jpeg', resumable=False)
    try:
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return uploaded_file.get('id')
    except Exception as e:
        st.error(f"전송 실패: {e}")
        return None

# 3. 메인 실행
service = get_drive_service()

if service:
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
                with st.spinner("5TB 드라이브로 전송 중..."):
                    drive_ids = []
                    for idx, f in enumerate(files):
                        opt_f = optimize_image(f)
                        fname = f"{date.strftime('%Y%m%d')}_{fish_type}_{idx}.jpg"
                        fid = upload_to_drive(service, opt_f, fname)
                        if fid: drive_ids.append(fid)
                    
                    if not files or len(drive_ids) == len(files):
                        new_data = pd.DataFrame([{
                            "날짜": date.strftime("%Y-%m-%d"), "포인트": point, "어종": fish_type, 
                            "마릿수": count, "길이": length, "무게": weight, 
                            "사용장비": gear, "메모": memo, "사진": "|".join(drive_ids)
                        }])
                        try:
                            df = pd.read_csv("fishing_data.csv")
                            df = pd.concat([df, new_data], ignore_index=True)
                        except: df = new_data
                        df.to_csv("fishing_data.csv", index=False)
                        st.success("성공적으로 저장되었습니다!")
                        st.balloons()
