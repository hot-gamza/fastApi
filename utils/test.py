import base64
import requests


relative_path = '/home/user/Desktop/fastApi/template/template.png'
if relative_path:
    with open(relative_path, "rb") as f:
        file_data_base64 = base64.b64encode(f.read()).decode('utf-8')

payload = {"file_data": file_data_base64}
url = 'http://192.168.0.70:8080/img'
print(f"File has been sent safely")
requests.post(url, json=payload)