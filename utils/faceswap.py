import cv2
import insightface
import datetime
import numpy as np
from insightface.app import FaceAnalysis
from .gfpgan_model import gfpgan_gogo
import os
import base64
import requests


current_dir = os.path.dirname(os.path.abspath(__file__))
inswapper_path = os.path.join(current_dir,'..' ,'models', 'inswapper_128.onnx')
result_path = os.path.join(current_dir, '..','images', 'result', 'result.jpg')

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))
swapper = insightface.model_zoo.get_model(inswapper_path, download=False, download_zip=False)


def faceswap(template_img, male_face_img, female_face_img):
    if not os.path.exists(os.path.join(current_dir, '..', 'images', 'result')):
        os.makedirs(os.path.join(current_dir, '..', 'images', 'result'))

    print(f"Current working directory: {os.getcwd()}")
    print(type(male_face_img), male_face_img)

    # 커플 템플릿
    template_img = cv2.imread(template_img)
    template_faces = app.get(template_img)
    print("detected number of faces: ", len(template_faces))
    dn = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fn = f'fs_{dn}.jpg'

    # 얼굴 이미지
    male_img_read = cv2.imread(male_face_img)
    male_copy_face = app.get(male_img_read)[0]

    female_img_read = cv2.imread(female_face_img)
    female_copy_face = app.get(female_img_read)[0]

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
        cnt+=1

    cv2.imwrite(result_path, result)
    gfp_result = np.array(gfpgan_gogo(result_path))  # await 사용
    gfp_result = cv2.cvtColor(gfp_result, cv2.COLOR_BGR2RGB)

    relative_path = os.path.join('images', 'result', fn)
    cv2.imwrite(relative_path, gfp_result)
    print(f"File saved at: {relative_path}")

    # IMAGE TO ASCII CODE(BASE64)
    if relative_path:
        with open(relative_path, "rb") as f:
          file_data_base64 = base64.b64encode(f.read()).decode('utf-8')

    payload = {"file_data": file_data_base64}
    url = 'http://192.168.0.70:8080/img'
    print(f"File has been sent safely")
    requests.post(url, json=payload)
    


    # return [os.path.join('images', 'result', fn)]