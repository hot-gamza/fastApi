import cv2
import insightface
import datetime
import uuid
import tempfile
import shutil
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


async def faceswap(template_img: str, male_face_imgs: List[str], female_face_imgs: List[str]) -> List[str]:
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
            male_faces = app.get(male_img_read)
            
            if not male_faces:
                raise ValueError(f"No face detected in the male image: {male_face_img}")
            
            male_copy_face = male_faces[0]

            female_img_read = cv2.imread(female_face_img)
            female_faces = app.get(female_img_read)
            
            if not female_faces:
                raise ValueError(f"No face detected in the female image: {female_face_img}")
            
            female_copy_face = female_faces[0]

            cnt = 0
            for find_face in template_faces:
                if cnt == 0:
                    if find_face['gender'] == 0:
                        result = swapper.get(template_img, find_face, female_copy_face, paste_back=True)
                    else:
                        result = swapper.get(template_img, find_face, male_copy_face, paste_back=True)
                else:
                    if find_face['gender'] == 0:
                        result = swapper.get(result, find_face, female_copy_face, paste_back=True)
                    else:
                        result = swapper.get(result, find_face, male_copy_face, paste_back=True)
                cnt += 1

            # Save the temporary result
            cv2.imwrite(temp_result_path, result)

            # Run additional model and save the result in the temporary directory
            gfp_result = np.array(await gfpgan_gogo(temp_result_path))
            gfp_result = cv2.cvtColor(gfp_result, cv2.COLOR_BGR2RGB)

            # Copy the result to the permanent result directory
            permanent_result_path = os.path.join(current_dir, '..', 'images', 'result', fn)
            cv2.imwrite(permanent_result_path, gfp_result)
            print(f"File saved at: {permanent_result_path}")
            
            result_filepaths.append(permanent_result_path)

    return result_filepaths