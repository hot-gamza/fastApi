from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
from io import BytesIO
import os
import random
from utils.upload import handle_upload
from utils.faceswap import faceswap
from PIL import Image
import base64

router = APIRouter()

@router.post("/standard")
async def index(imgFile: List[UploadFile] = File(...)):
    # 랜덤으로 1부터 5까지의 숫자를 선택
    random_number = random.randint(1, 5)
    
    # 랜덤 숫자를 사용하여 템플릿 이미지 경로를 설정
    template_img_path = os.path.join("template", f"{random_number}.png")
    
    male_filename = await handle_upload(imgFile[0])
    female_filename = await handle_upload(imgFile[1])

    if not male_filename or not female_filename:
        raise HTTPException(status_code=400, detail="Failed to upload files")

    template_img = template_img_path
    result_filepath_list = await faceswap(template_img, male_filename, female_filename)
    result_filepath = result_filepath_list[0] if result_filepath_list else None

    if result_filepath:
        with open(result_filepath, "rb") as f:
            file_data = f.read()
        
        file_data_base64 = base64.b64encode(file_data).decode("utf-8")
        return {"file_data": file_data_base64}



#TODO 파일 다운로드 가능

@router.post("/premium")
async def index(male_files: List[UploadFile] = File(...), female_files: List[UploadFile] = File(...)):
    # 랜덤으로 1부터 5까지의 숫자를 선택
    random_number = random.randint(1, 5)

    # 랜덤 숫자를 사용하여 템플릿 이미지 경로를 설정
    template_img_path = os.path.join("template", f"{random_number}.png")

    male_filenames = await handle_upload(male_files)
    female_filenames = await handle_upload(female_files)

    if not male_filenames or not female_filenames:
        raise HTTPException(status_code=400, detail="Failed to upload files")

    template_img = template_img_path
    result_filepath_list = await faceswap(template_img, male_filenames, female_filenames)
    result_filepath = result_filepath_list[0] if result_filepath_list else None

    # 처리된 이미지 파일을 반환
    if result_filepath:
        return FileResponse(result_filepath, headers={"Content-Disposition": f"attachment; filename={os.path.basename(result_filepath)}"})