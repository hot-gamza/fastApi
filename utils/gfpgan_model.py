from fastapi import UploadFile
from typing import Union
from gfpgan import GFPGANer
import torch
import numpy as np
from PIL import Image
import os
from io import BytesIO

# 함수를 비동기 함수로 변경
def gfpgan_gogo(file: Union[UploadFile, str]):
    if isinstance(file, UploadFile):
        file_contents = file.read()
    else:  # str이라고 가정
        with open(file, 'rb') as f:
            file_contents = f.read()

    original_img = Image.open(BytesIO(file_contents))    
    '''
        gfp 업스케일링 적용
        gfpgan_gogo(페이스 스왑한 이미지)
    '''
    np_img = np.array(original_img)

    # current_directory = os.getcwd()
    model_path = os.path.join('models', 'GFPGANv1.4.pth')

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model = GFPGANer(model_path=model_path, upscale=1, arch='clean', channel_multiplier=2, bg_upsampler=None, device=device)
    
    np_img_bgr = np_img[:, :, ::-1]
    _, _, gfpgan_output_bgr = model.enhance(np_img_bgr, has_aligned=False, only_center_face=False, paste_back=True)
    np_img = gfpgan_output_bgr[:, :, ::-1]

    restored_img = Image.fromarray(np_img)
    result_img = Image.blend(
        original_img, restored_img, 1
    )

    return result_img