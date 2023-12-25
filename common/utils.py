
from urllib.parse import urlparse
from common.singleton import singleton
from common.log import logger
from common.config import conf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
import pytesseract
from io import BytesIO
from PIL import Image

def get_url_content_Wind(url, verbose = False):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    # 等待 JavaScript 执行完成
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "news-detail")))
    # 获取页面内容
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    content = soup.find('div', id='news-detail')
    text = content.get_text()
    driver.quit()
    if verbose:
        print(text)
    return text

def get_url_content(url, verbose = False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    response = requests.get(
        url,
        headers=headers
    )

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        #text = " ".join(text.split())
        if verbose:
            print(text)
        return text
    else:
        raise ValueError(f"Invalid URL! Status code {response.status_code}.")

def get_url_content_wechat(url, verbose = False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    response = requests.get(
        url,
        headers=headers
    )

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        content = soup.find('div', id='js_content')
        text = content.get_text(separator='\r\n', strip=True)

        config = conf()

        ocrflag = config.get("ocr", False)

        if ocrflag:
            imgs_c = content.find_all('img')
            imgs = [i['data-src'] for i in imgs_c]

            pytesseract.pytesseract.tesseract_cmd = config.get("ocr_tool_path", r'D:\Program Files\Tesseract-OCR\tesseract.exe')

            for img in imgs:
                image_data = get_image_data(img)
                # 打开图像
                image = Image.open(image_data)
                # 进行 OCR
                t = pytesseract.image_to_string(image, lang='chi_sim')
                text = text + t
                logger.debug("[OCR] url={}".format(img))
                logger.debug("[OCR] text={}".format(t))

        if verbose:
            print(text)
        return text
    else:
        raise ValueError(f"Invalid URL! Status code {response.status_code}.")

def is_url_in_domains(url):
    # 解析 URL
    parsed_url = urlparse(url)
    # 获取域名
    return parsed_url.netloc

def get_image_data(image_url):
    # 发送请求获取图片
    response = requests.get(image_url)

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用 BytesIO 将获取到的二进制数据包装成文件对象
        image_data = BytesIO(response.content)
        return image_data

    return