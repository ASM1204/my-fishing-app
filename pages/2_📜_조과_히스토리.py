import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io

st.set_page_config(page_title="낚's - 히스토리", layout="wide")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;} [data-testid="stSidebarCollapseButton"] {display: none;}</style>""", unsafe_allow_html=True)

if st.button("🏠 HOME으로 가기"): st.switch_page("app.py")
st.markdown("---")
st.title("📜 조과 히스토리")

# --- 구글 드라이브 인증 및 사진 다운로드 함수 ---
def get_drive_service():
    info = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive"])
    return build('drive', 'v3', credentials=creds)

def download_from_drive(file_id):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = request.execute()
    return downloader

try:
    df = pd.read_csv("fishing_data.csv")
    if df.empty:
        st.info("기록이 없습니다.")
    else:
        df = df.sort_values(by="날짜", ascending=False)
        for i, row in df.iterrows():
            with st.container():
                st.markdown("---")
                c1, c2, c3 = st.columns([1.5, 2, 1])
                
                with c1:
                    if isinstance(row['사진'], str) and row['사진']:
                        first_img_id = row['사진'].split("|")[0]
                        try:
                            # 구글 드라이브 썸네일 링크 활용 (빠른 로딩)
                            # webContentLink를 직접 쓰기보다 가벼운 뷰어 주소 활용
                            img_url = f"https://drive.google.com/thumbnail?id={first_img_id}&sz=w800"
                            st.image(img_url, use_container_width=True)
                        except:
                            st.write("이미지를 불러올 수 없습니다.")
                    else:
                        st.write("📷 사진 없음")
                
                with c2:
                    st.subheader(f"{row['날짜']} | {row['어종']}")
                    st.write(f"📍 {row['포인트']} | 📏 {row['길이']}cm | 🔢 {row['마릿수']}마리")
                    st.info(f"💬 {row['메모']}")
                
                with c3:
                    if st.button("🗑️ 삭제", key=f"del_{i}"):
                        # (참고) 실제 구글 드라이브의 파일도 삭제하려면 추가 코드가 필요하지만, 
                        # 우선 데이터베이스(CSV)에서만 삭제하도록 구현했습니다.
                        df.drop(i).to_csv("fishing_data.csv", index=False)
                        st.rerun()
except:
    st.info("데이터를 불러오는 중 오류가 발생했거나 파일이 없습니다.")
