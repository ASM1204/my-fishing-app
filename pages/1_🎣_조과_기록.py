import streamlit as st
import pandas as pd
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# ... 페이지 설정 생략 (동일) ...

def upload_to_drive(file, filename):
    try:
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build('drive', 'v3', credentials=creds)
        folder_id = st.secrets["google_drive"]["folder_id"]
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        # 504KB라면 굳이 복잡한 업로드 방식을 쓸 필요가 없습니다.
        # 이진 데이터를 그대로 담아 보냅니다.
        media = MediaIoBaseUpload(file, mimetype='image/jpeg', resumable=False)
        
        # supportsAllDrives를 True로 하고, 
        # 서비스 계정이 아닌 부모 폴더의 설정을 따르도록 강제합니다.
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        return uploaded_file.get('id')
    except Exception as e:
        # 에러 메시지를 더 자세히 출력하여 원인을 파악합니다.
        st.error(f"상세 오류 내역: {e}")
        return None

# ... 나머지 폼 로직 동일 ...
