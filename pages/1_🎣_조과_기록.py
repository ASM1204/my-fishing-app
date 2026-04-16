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

# --- 이미지 최적화 (Quota 에러 회피를 위해 용량을 극소화) ---
def optimize_image(uploaded_file):
    img = Image.open(uploaded_file)
    # 이미지 회전 방지 (EXIF 반영)
    try:
        if hasattr(img, '_getexif'):
            from PIL import ExifTags
            exif = img._getexif()
            if exif:
                orientation = next((k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
                if orientation in exif:
                    if exif[orientation] == 3: img = img.rotate(180, expand=True)
                    elif exif[orientation] == 6: img = img.rotate(270, expand=True)
                    elif exif[orientation] == 8: img = img.rotate(90, expand=True)
    except: pass

    img = img.convert("RGB")
    # 해상도를 1280px로 조정 (모바일 확인용으로 충분하며 용량이 작음)
    img.thumbnail((1280, 1280), Image.LANCZOS)
    
    out = io.BytesIO()
    # 품질 70% 및 최적화 옵션으로 용량을 수백 KB 이내로 강제 축소
    img.save(out, format="JPEG", quality=70, optimize=True)
    out.seek(0)
    return out

# --- 구글 드라이브 업로드 및 권한 부여 함수 ---
def upload_to_drive(optimized_file, filename):
    service = get_drive_service()
    if not service: return None
    
    folder_id = st.secrets["google_drive"]["folder_id"]
    USER_EMAIL = "sangminan1204@gmail.com" # 사용자님의 이메일 적용
    
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    media = MediaIoBaseUpload(optimized_file, mimetype='image/jpeg', resumable=False)
    
    try:
        # 1. 파일 생성 시도
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        file_id = uploaded_file.get('id')
        
        # 2. 업로드 직후 사용자 계정(sangminan1204@gmail.com)에 편집 권한 부여
        # 이를 통해 소유권 분쟁으로 인한 할당량 문제를 완화합니다.
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': USER_EMAIL
        }
        service.permissions().create(fileId=file_id, body=permission, supportsAllDrives=True).execute()
        
        return file_id
        
    except Exception as e:
        # 여전히 Quota 에러가 난다면 상세 내용을 화면에 표시
        st.error(f"구글 드라이브 전송 실패: {e}")
        return None

# 기초 데이터 로드
try:
    point_df = pd.read_csv("points.csv")
    point_list = point_df["포인트명"].tolist() if not point_df.empty else []
    gear_df = pd.read_csv("gears.csv")
    gear_list = gear_df["장비명"].tolist() if not gear_df.empty else []
except:
    point_list, gear_list = [], []

# 조과 기록 폼
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
    
    files = st.file_uploader("📸 사진 업로드 (최대 10개)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    
    if st.form_submit_button("저장하기 🚀"):
        if not fish_type:
            st.error("어종을 입력해주세요.")
        else:
            with st.spinner("이미지 최적화 및 구글 드라이브 전송 중..."):
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
                        "날짜": date.strftime("%Y-%m-%d"),
                        "포인트": point,
                        "어종": fish_type,
                        "마릿수": count,
                        "길이": length,
                        "무게": weight,
                        "사용장비": gear,
                        "메모": memo,
                        "사진": "|".join(drive_ids)
                    }])
                    
                    try:
                        df = pd.read_csv("fishing_data.csv")
                        df = pd.concat([df, new_data], ignore_index=True)
                    except:
                        df = new_data
                    
                    df.to_csv("fishing_data.csv", index=False)
                    st.success("기록이 성공적으로 저장되었습니다!")
                    st.balloons()
                else:
                    st.error("사진 업로드 중 할당량 문제가 발생했습니다. 이미지 크기를 더 줄여 시도하거나 설정을 점검하세요.")
