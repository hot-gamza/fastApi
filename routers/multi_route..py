from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from typing import List
from utils.upload import handle_upload
from utils.faceswap import faceswap


# app = FastAPI()
# router = APIRouter()

# @router.post("/")
async def upload_files(male_file: List[UploadFile] = File(...), female_file: List[UploadFile] = File(...)):
    male_filenames = await handle_upload(male_file) 
    female_filenames = await handle_upload(female_file) 

    if not male_filenames or not female_filenames:
        raise HTTPException(status_code=400, detail="Failed to upload files")
    template_img = r"template\template.png"
    result_filenames = faceswap(template_img, male_filenames[0], female_filenames[0])

    return {"result_filenames": result_filenames}

# app.include_router(router)
