import streamlit as st
import pandas as pd
import datetime
import json
import io
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image

# 1. 페이지 기본 설정
st.set_page_config(page_title="낚's - 조과 기록", layout="centered")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} [data-testid="stSidebarCollapseButton"] {display: none;}</style>""", unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): 
    st.switch_page("app.py")

st.markdown("---")
st.title("🎣 조과 기록")

# --- 구글 인증 및 서비스 생성 함수 ---
def get_drive_service():
    # Secrets에서 설정값 불러오기
    client_config = json.loads(st.secrets["google_oauth"]["client_secrets_json"])
    scopes = ['https://www.googleapis.com/auth/drive.file']
    # 배포된 앱의 실제 리디렉션 주소 (JSON 파일 내의 주소와 일치해야 함)
    redirect_uri = "https://my-fishing.streamlit.app/" 

    flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_uri)

    # URL 파라미터에서 인증 코드 추출
    auth_code = st.query_params.get("code")

    # 세션에 인증 정보가 없고, URL에도 코드가 없다면 로그인 버튼 표시
    if 'creds' not in st.session_state and not auth_code:
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        st.warning("⚠️ 사진 저장을 위해 구글 계정 인증이 필요합니다.")
        st.link_button("🔑 구글 로그인 (5TB 권한 사용)", auth_url)
        return None

    # URL에 코드가 들어왔다면 세션에 저장 (인증 처리)
    if auth_code and 'creds' not in st.session_state:
        try:
            flow.fetch_token(code=auth_code)
            st.session_state.creds = flow.credentials
            st.query_params.clear() # 주소창 코드 제거
            st.rerun() # 즉시 재실행하여 기록창 띄우기
        except Exception as e:
            st.error(f"인증 처리 중 오류 발생: {e}")
            st.query_params.clear()
            return None

    # 인증 정보가 세션에 있다면 서비스 객체 생성
    if 'creds' in st.session_state:
        return build('drive', 'v3', credentials=st.session_state.creds)
    
    return None

# --- 이미지 처리 함수 ---
def process_photo(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((1600, 1600), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf

# --- 드라이브 업로드 함수 ---
def upload_file(service, buf, filename):
    folder_id = st.secrets["google_drive"]["folder_id"]
    meta = {'name': filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(buf, mimetype='image/jpeg')
    try:
        res = service.files().create(body=meta, media_body=media, fields='id').execute()
        return res.get('id')
    except Exception as e:
        st.error(f"전송 실패: {e}")
        return None

# --- 메인 실행 로직 ---
service = get_drive_service()

# 서비스가 확보되면(인증 완료 시) 바로 기록 창을 띄웁니다.
if service:
    st.success("✅ 구글 드라이브 연결됨 (상민님 계정)")
    
    # 기초 데이터 로드
    try:
        p_list = pd.read_csv("points.csv")["포인트명"].tolist()
        g_list = pd.read_csv("gears.csv")["장비명"].tolist()
    except:
        p_list, g_list = [], []

    # [조과 기록 폼 구현]
    with st.form("record_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            date = st.date_input("📅 날짜", datetime.date.today())
            point = st.selectbox("📍 포인트", p_list) if p_list else st.text_input("📍 포인트 직접 입력")
            fish = st.text_input("🐟 어종")
            cnt = st.number_input("🔢 마릿수", min_value=1, step=1)
        with c2:
            length = st.number_input("📏 길이(cm)", min_value=0.0)
            weight = st.number_input("⚖️ 무게(kg)", min_value=0.0)
            gear = st.selectbox("🎣 장비", g_list) if g_list else st.text_input("🎣 장비 입력")
            memo = st.text_area("💬 메모")
        
        up_files = st.file_uploader("📸 사진 업로드", type=['jpg','jpeg','png'], accept_multiple_files=True)
        
        if st.form_submit_button("기록 저장하기 🚀"):
            if not fish:
                st.error("어종을 입력해주세요.")
            else:
                with st.spinner("구글 드라이브에 사진 저장 중..."):
                    photo_ids = []
                    for i, f in enumerate(up_files):
                        p_buf = process_photo(f)
                        fname = f"{date}_{fish}_{i}.jpg"
                        pid = upload_file(service, p_buf, fname)
                        if pid: photo_ids.append(pid)
                    
                    # CSV 데이터 저장
                    new_row = pd.DataFrame([{
                        "날짜": date.strftime("%Y-%m-%d"), "포인트": point, "어종": fish,
                        "마릿수": cnt, "길이": length, "무게": weight,
                        "사용장비": gear, "메모": memo, "사진": "|".join(photo_ids)
                    }])
                    
                    try:
                        df = pd.read_csv("fishing_data.csv")
                        df = pd.concat([df, new_row], ignore_index=True)
                    except:
                        df = new_row
                    
                    df.to_csv("fishing_data.csv", index=False)
                    st.success("기록이 성공적으로 저장되었습니다!")
                    st.balloons()
