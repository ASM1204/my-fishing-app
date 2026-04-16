import streamlit as st
import pandas as pd
import datetime
import json
import io
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image

# 1. 페이지 설정 및 스타일
st.set_page_config(page_title="낚's - 조과 기록", layout="centered")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} [data-testid="stSidebarCollapseButton"] {display: none;}</style>""", unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): 
    st.switch_page("app.py")

st.markdown("---")
st.title("🎣 조과 기록 (개인 5TB 모드)")

# --- OAuth 2.0 인증 로직 ---
def get_drive_service():
    # 1. Secrets에서 설정 로드
    client_config = json.loads(st.secrets["google_oauth"]["client_secrets_json"])
    scopes = ['https://www.googleapis.com/auth/drive.file']
    
    # 배포 환경에 따른 리디렉션 URI 설정
    redirect_uri = "https://my-fishing.streamlit.app/" if not st.sidebar.checkbox("로컬 테스트용", value=False) else "http://localhost:8501"

    flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_uri)

    # 2. URL 파라미터에서 인증 코드 확인
    auth_code = st.query_params.get("code")
    
    if auth_code:
        try:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            st.error(f"인증 토큰 획득 실패: {e}")
            st.query_params.clear() # 에러 시 파라미터 초기화
            return None
    else:
        # 3. 인증 전이면 로그인 버튼 표시
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.warning("⚠️ 사진 업로드를 위해 구글 계정 인증이 필요합니다.")
        st.link_button("🔑 구글 로그인 (5TB 권한 사용)", auth_url)
        return None

# --- 이미지 최적화 ---
def optimize_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((2000, 2000), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85, optimize=True)
    out.seek(0)
    return out

# --- 구글 드라이브 업로드 함수 ---
def upload_to_drive(service, optimized_file, filename):
    folder_id = st.secrets["google_drive"]["folder_id"]
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(optimized_file, mimetype='image/jpeg', resumable=False)
    
    try:
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return uploaded_file.get('id')
    except Exception as e:
        st.error(f"업로드 실패: {e}")
        return None

# 메인 로직 시작
service = get_drive_service()

if service:
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
        
        files = st.file_uploader("📸 사진 업로드", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
        
        if st.form_submit_button("저장하기 🚀"):
            if not fish_type:
                st.error("어종을 입력해주세요.")
            else:
                with st.spinner("이미지 최적화 및 업로드 중..."):
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
                        st.success("상민님 계정으로 안전하게 저장되었습니다!")
                        st.balloons()
