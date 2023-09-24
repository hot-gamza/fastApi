from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends
from typing import List
import os
import uuid
from utils.upload import handle_upload
from utils.faceswap import faceswap
import logging
import requests
import random

router = APIRouter()

def get_logger():
    logger = logging.getLogger(__name__)
    return logger

# 작업 상태와 결과 파일을 저장할 딕셔너리
task_status = {}


@router.post("/premium")
async def premium(male_files: List[UploadFile] = File(...), female_files: List[UploadFile] = File(...), logger: logging.Logger = Depends(get_logger), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        logger.info("Received a premium request")

        male_filenames = await handle_upload(male_files)
        female_filenames = await handle_upload(female_files)

        if not male_filenames or not female_filenames:
            logger.error("Failed to upload files")
            raise HTTPException(status_code=400, detail="Failed to upload files")
        
        # UUID 생성
        unique_id = str(uuid.uuid4())
        # 작업 상태 저장
        task_status[unique_id] = {'status': 'in-progress'}

        # 템플릿 이미지 경로들을 가져옴
        all_template_img_paths = [os.path.join("template", filename) for filename in os.listdir("template") if filename.endswith('.png')]
        
        # 랜덤으로 3개의 이미지만 선택(중복 방지 == random.sample)
        selected_template_img_paths = random.sample(all_template_img_paths, 3)

        # 비동기 작업으로 등록
        background_tasks.add_task(faceswap_and_update_status_premium, unique_id, selected_template_img_paths, male_filenames, female_filenames, logger)
        
        return {"status": "success", "task_id": unique_id}


    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def faceswap_and_update_status_premium(unique_id, template_img_paths, male_filenames, female_filenames, logger):
    all_result_files = []
    for template_img_path in template_img_paths:
        result_filepath_list = await faceswap(template_img_path, male_filenames, female_filenames)
        if result_filepath_list:
            all_result_files.extend(result_filepath_list)

    if all_result_files:
        task_status[unique_id] = {'status': 'completed'}

        #For img File들 저장 
        files_list = []
        for result_file in all_result_files:
            with open(result_file, 'rb') as f:
                file_content = f.read()
                files_list.append(('files', (os.path.basename(result_file), file_content, 'application/octet-stream')))

        payload = {'task_id': unique_id, 'status': 'completed'}
        requests.post('http://192.168.226.64:8080/api/v1/saveAiImages', data=payload, files=files_list)

        logger.info(f"Task {unique_id} completed")
    else:
        task_status[unique_id] = {'status': 'failed'}

        payload = {'task_id': unique_id, 'status': 'failed'}
        requests.post('http://192.168.226.64:8080/api/v1/saveAiImages', json=payload)
        
        logger.error(f"Task {unique_id} failed")
