import streamlit as st
import pandas as pd
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image
import io

# 1. 페이지 설정 및 사이드바 제거
st.set_page_config(page_title="낚's - 조과 기록", layout="centered")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapseButton"] { display: none; }
    .stButton>button { width: 100%; height: 60px; font-size: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 홈 버튼
if st.button("🏠 HOME으로 가기"): 
    st.switch_page("app.py")

st.markdown("---")
st.title("🎣 조과 기록")

# --- 구글 드라이브 서비스 인증 ---
def get_drive_service():
    try:
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"구글 인증 오류: {e}")
        return None

# --- 이미지 최적화 (가벼운 압축) ---
def optimize_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.convert("RGB")
    img.thumbnail((1600, 1600), Image.LANCZOS)
    
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85, optimize=True)
    out.seek(0)
    return out

# --- 구글 드라이브 업로드 (소유권 이전 로직 포함) ---
def upload_to_drive(optimized_file, filename):
    service = get_drive_service()
    if not service: return None
    
    folder_id = st.secrets["google_drive"]["folder_id"]
    USER_EMAIL = "sangminan1204@gmail.com"
    
    # [중요] metadata에 소유권 관련 설정을 포함할 수 없으므로 생성 후 권한 변경 방식을 씁니다.
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    media = MediaIoBaseUpload(optimized_file, mimetype='image/jpeg', resumable=False)
    
    try:
        # 1. 파일 생성 시도 (supportsAllDrives=True 필수)
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id',
            supportsAllDrives=True 
        ).execute()
        
        file_id = uploaded_file.get('id')
        
        # 2. [에러 해결의 핵심] 사용자 계정(sangminan1204)을 파일의 'owner'로 변경 시도
        # 개인 계정 간 소유권 이전은 'transferOwnership=True' 옵션이 필요합니다.
        permission = {
            'type': 'user',
            'role': 'owner',  # 편집자(writer)가 아닌 소유자(owner)로 지정
            'emailAddress': USER_EMAIL
        }
        
        # 소유권 이전 실행
        service.permissions().create(
            fileId=file_id, 
            body=permission, 
            transferOwnership=True, # 소유권 강제 이전
            supportsAllDrives=True
        ).execute()
        
        return file_id
        
    except Exception as e:
        # 만약 owner 이전이 막힌다면 writer 권한이라도 부여하여 쿼터를 확보합니다.
        try:
            permission_writer = {'type': 'user', 'role': 'writer', 'emailAddress': USER_EMAIL}
            service.permissions().create(fileId=file_id, body=permission_writer, supportsAllDrives=True).execute()
            return file_id
        except:
            st.error(f"구글 드라이브 할당량 에러 우회 실패: {e}")
            return None

# 데이터 로드
try:
    point_list = pd.read_csv("points.csv")["포인트명"].tolist()
    gear_list = pd.read_csv("gears.csv")["장비명"].tolist()
except:
    point_list, gear_list = [], []

# 폼 구성
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
            with st.spinner("구글 드라이브 전송 중..."):
                drive_ids = []
                upload_success = True
                
                if files:
                    for idx, f in enumerate(files):
                        optimized_f = optimize_image(f)
                        fname = f"{date.strftime('%Y%m%d')}_{fish_type}_{idx}.jpg"
                        fid = upload_to_drive(optimized_f, fname)
                        if fid:
                            drive_ids.append(fid)
                        else:
                            upload_success = False
                            break
                
                if upload_success:
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
                    st.success("기록 완료!")
                    st.balloons()
