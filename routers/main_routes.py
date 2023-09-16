from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
from io import BytesIO
import os
from utils.upload import handle_upload
from utils.faceswap import faceswap
from PIL import Image

router = APIRouter()
template_img_path = os.path.join("template", "template.png")

#TODO downlaod는 안되고, 파일 그 자체를 전송
@router.post("/standard")
async def index(male_files: List[UploadFile] = File(...), female_files: List[UploadFile] = File(...)):
    male_filenames = await handle_upload(male_files)
    female_filenames = await handle_upload(female_files)

    if not male_filenames or not female_filenames:
        raise HTTPException(status_code=400, detail="Failed to upload files")

    template_img = template_img_path
    result_filepath_list = await faceswap(template_img, male_filenames, female_filenames)
    result_filepath = result_filepath_list[0]
    
    # 이미지를 PIL.Image 객체로 로드
    image = Image.open(result_filepath)
    
    # 이미지를 바이트 스트림으로 변환
    image_stream = BytesIO()
    image.save(image_stream, format='JPEG')
    image_stream.seek(0)
    
    # 스트리밍 응답으로 반환
    return StreamingResponse(image_stream, media_type="image/jpeg")


#TODO 파일 다운로드 가능
@router.post("/premium")
async def index(male_files: List[UploadFile] = File(...), female_files: List[UploadFile] = File(...)):
    male_filenames = await handle_upload(male_files)
    female_filenames = await handle_upload(female_files)

    if not male_filenames or not female_filenames:
        raise HTTPException(status_code=400, detail="Failed to upload files")

    template_img = template_img_path
    result_filepath_list  = await faceswap(template_img, male_filenames, female_filenames)
    result_filepath = result_filepath_list[0]

    # 처리된 이미지 파일을 반환
    return FileResponse(result_filepath, headers={"Content-Disposition": f"attachment; filename={os.path.basename(result_filepath)}"})


