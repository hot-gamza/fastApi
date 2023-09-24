from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends
from typing import List
import os
import random
import uuid
from utils.upload import handle_upload
from utils.logoswap import logoswap
import logging
import requests
from redis import Redis
from rq import Queue
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()


def get_logger():
    logger = logging.getLogger(__name__)
    return logger


# 작업 상태와 결과 파일을 저장할 딕셔너리
task_status = {}

SPRING_URL = os.environ.get('SPRING_URL')
REDIS_CON_IP = os.environ.get('REDIS_CON_IP')


@router.post("/standard")
async def index(male_files: List[UploadFile] = File(...), female_files: List[UploadFile] = File(...), logger: logging.Logger = Depends(get_logger)):
    logger.info("Received a standard request")

    random_number = random.randint(1, 11)
    template_img_path = os.path.join("template", f"{random_number}.png")
    male_filename = await handle_upload(male_files)
    female_filename = await handle_upload(female_files)

    if not male_filename or not female_filename:
        logger.error("Failed to upload files")
        raise HTTPException(status_code=400, detail="Failed to upload files")

    try:
        # UUID 생성
        unique_id = str(uuid.uuid4())

        # 작업 상태 저장
        task_status[unique_id] = {'status': 'in-progress'}

        # 비동기 작업으로 등록
        # background_tasks = BackgroundTasks = BackgroundTasks()
        # background_tasks.add_task(faceswap_and_update_status, unique_id, template_img_path, male_filename, female_filename, logger)

        # redis queue
        redis_queue = Redis(host=REDIS_CON_IP, port=6379)
        task_queue = Queue("task_queue", connection=redis_queue)
        task_queue.enqueue(faceswap_and_update_status, unique_id,
                           template_img_path, male_filename, female_filename, logger)

        return {"status": "success", "task_id": unique_id}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def faceswap_and_update_status(unique_id, template_img_path, male_filename, female_filename, logger):
    try:
        result_filepath_list = await logoswap(template_img_path, male_filename, female_filename)
        print("well")
        if result_filepath_list:
            result_filepath = result_filepath_list[0]

            with open(result_filepath, 'rb') as f:
                files = {'file': (os.path.basename(
                    result_filepath), f, 'application/octet-stream')}
                payload = {'task_id': unique_id, 'status': 'completed'}
                print("go")
                response = requests.post(
                    SPRING_URL+'/api/v1/saveAiImage', data=payload, files=files)

                if response.status_code == 200:
                    if response.text == 'success':
                        logger.info(
                            f"Successfully sent the file for task {unique_id}")
                    else:
                        logger.error(
                            f"Failed to send the file for task {unique_id}. Server responded with: {response.text}")
                else:
                    logger.error(
                        f"Failed to send the file for task {unique_id}. HTTP status code: {response.status_code}")

            task_status[unique_id] = {
                'status': 'completed',
                'result_file': result_filepath
            }
            logger.info(f"Task {unique_id} completed")
            print(f"Task {unique_id} completed")

        else:
            payload = {'task_id': unique_id, 'status': 'failed'}
            requests.post(SPRING_URL+'/api/v1/saveAiImage', json=payload)

            task_status[unique_id] = {'status': 'failed'}
            logger.error(f"Task {unique_id} failed")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        task_status[unique_id] = {'status': 'failed'}