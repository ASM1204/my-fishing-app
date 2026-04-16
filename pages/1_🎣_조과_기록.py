import streamlit as st
import pandas as pd
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image
import io

# 1. 페이지 설정
st.set_page_config(page_title="낚's - 조과 기록", layout="centered")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapseButton"] { display: none; }
    .stButton>button { width: 100%; height: 60px; font-size: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): 
    st.switch_page("app.py")

st.markdown("---")
st.title("🎣 조과 기록")

# --- 구글 드라이브 인증 ---
def get_drive_service():
    try:
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"인증 설정 오류: {e}")
        return None

# --- 이미지 최적화 (Quota 에러 회피를 위해 아주 작게 압축) ---
def optimize_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.convert("RGB")
    # 해상도를 더 줄여서 구글의 감시를 피합니다.
    img.thumbnail((1024, 1024), Image.LANCZOS)
    
    out = io.BytesIO()
    # 품질을 60%까지 낮춰 용량을 최소화합니다.
    img.save(out, format="JPEG", quality=60, optimize=True)
    out.seek(0)
    return out

# --- 구글 드라이브 업로드 함수 (가장 단순한 구조) ---
def upload_to_drive(optimized_file, filename):
    service = get_drive_service()
    if not service: return None
    
    folder_id = st.secrets["google_drive"]["folder_id"]
    
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    # 504KB도 안되는 파일은 resumable=False가 훨씬 안정적입니다.
    media = MediaIoBaseUpload(optimized_file, mimetype='image/jpeg', resumable=False)
    
    try:
        # 이 단계에서 에러가 난다면 서비스 계정 방식은 포기해야 합니다.
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        ).execute()
        
        file_id = uploaded_file.get('id')
        
        # 권한 추가 (상민님 이메일)
        permission = {'type': 'user', 'role': 'writer', 'emailAddress': 'sangminan1204@gmail.com'}
        service.permissions().create(fileId=file_id, body=permission).execute()
        
        return file_id
    except Exception as e:
        st.error(f"⚠️ 구글 보안 정책에 의해 차단됨: {e}")
        return None

# 데이터 로드
try:
    p_df = pd.read_csv("points.csv")
    point_list = p_df["포인트명"].tolist() if not p_df.empty else []
    g_df = pd.read_csv("gears.csv")
    gear_list = g_df["장비명"].tolist() if not g_df.empty else []
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
            with st.spinner("데이터 전송 중..."):
                drive_ids = []
                for idx, f in enumerate(files):
                    opt_f = optimize_image(f)
                    fid = upload_to_drive(opt_f, f"{date}_{fish_type}_{idx}.jpg")
                    if fid: drive_ids.append(fid)
                
                # 사진이 없거나 모두 성공한 경우만 저장
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
                    st.success("기록 완료!")
                    st.balloons()
