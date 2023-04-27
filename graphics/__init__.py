import cv2
import json
import requests
import io
import os


async def photo_input():
    img = cv2.imread('C:/Users/t106o/PycharmProjects/UchiDomaProject/test_imgs/img.jpg')
    url_api = "https://api.ocr.space/parse/image"

    # Сжимаем изображение, т.к. api не принимает больше 1mb
    _, compressedimage = cv2.imencode(".jpg", img, [1, 90])
    file_bytes = io.BytesIO(compressedimage)

    result = requests.post(url_api,
                           files={"some_img.jpg": file_bytes},
                           data={"apikey": "K89439205688957",
                                 "language": "rus"})

    result = result.content.decode()
    result = json.loads(result)
    text = result["ParsedResults"][0]["ParsedText"]
    os.remove('C:/Users/t106o/PycharmProjects/UchiDomaProject/test_imgs/img.jpg')
    return text