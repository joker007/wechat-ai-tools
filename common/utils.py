import time, os
import requests
from bs4 import BeautifulSoup
import pytesseract
from io import BytesIO
from PIL import Image
import html
import docx
import fitz

from urllib.parse import urlparse
from common.singleton import singleton
from common.log import logger
from common.config import conf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_url_content(query):
    url = html.unescape(query)

    if is_url_in_domains(url) == "mp.weixin.qq.com":
        # print("wechat")
        logger.info("[Wechat] url={}".format(url))
        text = get_url_content_wechat(url)
    elif is_url_in_domains(url) in ["t.wind.com.cn", "m.wind.com.cn", "m.toutiao.com"]:
        logger.info("[Wind] url={}".format(url))
        # crawler_instance = WindClawler()
        # text = crawler_instance.get_url_content_wind(url)
        text = get_url_content_Wind(url)
        #print(text)
    elif is_url_in_domains(url) in ["m.toutiao.com"]:
        logger.info("[TouTiao] url={}".format(url))
    else:
        logger.info("[Other] url={}".format(url))
        text = get_url_content_common(url)
    # token 检测
    return text


def get_file_content(query):
    file_path = os.path.join(os.getcwd(), query)
    suffix = os.path.splitext(file_path)[-1]

    if ".doc" in suffix:
        doc = docx.Document(file_path)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        text = '\n'.join(fullText)
    elif suffix == ".txt":
        with open(file_path, 'r', encoding='utf8') as f:
            lines = f.readlines()
        text = '\n'.join(lines)
    elif suffix == ".pdf":
        full_text = ""
        num_pages = 0
        with fitz.open(file_path) as doc:
            for page in doc:
                num_pages += 1
                text = page.get_text()
                full_text += text + "\n"
        text = f"This is a {num_pages}-page document.\n" + full_text

    return text

def get_url_content_Wind(url, verbose = False):
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    # 等待 JavaScript 执行完成
    wait = WebDriverWait(driver, 10)
    #news-detail
    wait.until(EC.presence_of_element_located((By.ID, "news-detail")))
    #wait.until(EC.presence_of_element_located((By.CLASS_NAME, "article-content")))
    # 获取页面内容
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    content = soup.find('div', id ='news-detail')
    #content = soup.find('div', class_ ='article-content')
    text = content.get_text()
    driver.quit()
    if verbose:
        print(text)
    return text

def get_url_content_common(url, verbose = False):
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