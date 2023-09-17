from fastapi import UploadFile
from werkzeug.utils import secure_filename
import os
from typing import Union, List

UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def handle_upload(file: UploadFile) -> str:
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 파일을 비동기적으로 읽고 저장
        file_bytes = await file.read()
        with open(filepath, "wb") as buffer:
            buffer.write(file_bytes)
            
        return filepath  # 단일 파일 경로를 문자열로 반환
    else:
        return None

async def multi_upload(files: List[UploadFile]) -> List[str]:
    filepaths = []
    for file in files:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # 파일을 비동기적으로 읽고 저장
            file_bytes = await file.read()
            with open(filepath, "wb") as buffer:
                buffer.write(file_bytes)

            filepaths.append(filepath)
        else:
            # 이 부분은 파일이 허용되지 않은 경우에 대한 처리
            # 필요에 따라 예외를 발생 or 로깅
            pass

    return filepaths
