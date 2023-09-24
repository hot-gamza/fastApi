import cv2
import insightface
import datetime
import tempfile
from PIL import Image
import numpy as np
from insightface.app import FaceAnalysis
from .gfpgan_model import gfpgan_gogo
import os
from typing import List

current_dir = os.path.dirname(os.path.abspath(__file__))
inswapper_path = os.path.join(current_dir, '..', 'models', 'inswapper_128.onnx')

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))
swapper = insightface.model_zoo.get_model(inswapper_path, download=False, download_zip=False)

async def logoswap(template_img: str, male_face_imgs: List[str], female_face_imgs: List[str]) -> List[str]:
    result_filepaths = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        template_img = cv2.imread(template_img)
        template_faces = app.get(template_img)
        print("Detected number of faces:", len(template_faces))
        
        for male_face_img, female_face_img in zip(male_face_imgs, female_face_imgs):
            print(f"Processing {male_face_img} and {female_face_img}")
            
            # Create a result directory if it doesn't exist
            if not os.path.exists(os.path.join(current_dir, '..', 'images', 'result')):
                os.makedirs(os.path.join(current_dir, '..', 'images', 'result'))
            
            # Generate a unique filename based on current time
            dn = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            fn = f'fs_{dn}.jpg'
            temp_result_path = os.path.join(temp_dir, fn)

            male_img_read = cv2.imread(male_face_img)
            male_copy_face = app.get(male_img_read)[0]

            female_img_read = cv2.imread(female_face_img)
            female_copy_face = app.get(female_img_read)[0]

            cnt = 0
            for find_face in template_faces:
                if find_face['gender'] == 0:
                    result = swapper.get(template_img if cnt == 0 else result, find_face, female_copy_face, paste_back=True)
                else:
                    result = swapper.get(template_img if cnt == 0 else result, find_face, male_copy_face, paste_back=True)
                cnt += 1

            # Save the temporary result
            cv2.imwrite(temp_result_path, result)

            # Run additional model and get the result in memory
            gfp_result = np.array(await gfpgan_gogo(temp_result_path))
            gfp_result = cv2.cvtColor(gfp_result, cv2.COLOR_BGR2RGB)

            # 로고 이미지 로드
            logo_path = os.path.join(current_dir, '..', 'images', 'logo', 'logo.png')            
            logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)  # IMREAD_UNCHANGED로 알파 채널까지 로드

            # 로고의 위치 계산
            x = gfp_result.shape[1] - logo.shape[1]
            y = gfp_result.shape[0] - logo.shape[0]

            # 로고 이미지를 메인 이미지에 추가
            for c in range(0, 3):
                gfp_result[y: logo.shape[0]+y, x: logo.shape[1]+x, c] = gfp_result[y: logo.shape[0]+y, x: logo.shape[1]+x, c] * (1 - logo[:, :, 3] / 255.0) + logo[:, :, c] * (logo[:, :, 3] / 255.0)

            # 결과 이미지 저장
            output_with_logo_path = os.path.join(current_dir, '..', 'images', 'result', f'with_logo_{fn}')
            cv2.imwrite(output_with_logo_path, gfp_result)
            print(f"File with logo saved at: {output_with_logo_path}")

            # Append the file path of the image with logo to the result list
            result_filepaths.append(output_with_logo_path)

    return result_filepaths