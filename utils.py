import threading
import time

import requests
from lxml import html

import re
import logging


def getTree(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    html_content = response.text

    tree = html.fromstring(html_content)

    return tree


def cleanText(text):
    cleaned_text = re.sub(r'\r\n|\xa0|\u3000', ' ', text)
    return cleaned_text


def sleepMonitor(internal: int, event: threading.Event) -> None:
    """
    休眠监测器
    :param internal: 休眠间隔，只能是整数
    :param event: 触发回调的事件，当事件被设置为clear的时候回调
    :return: 无返回
    """
    for i in range(internal):
        if not event.isSet():
            break
        time.sleep(1)


def strConvert(input_str):
    if re.match(r'^\d+$', input_str):
        return int(input_str)
    elif re.match(r'^\d+\.\d+$', input_str):
        return float(input_str)
    else:
        return input_str

def initial_logger(name, log_name, root_logger=False):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if root_logger:
        handler = logging.FileHandler(log_name)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def is_connected(url):
    try:
        requests.get(url, timeout=5)
        return True
    except:
        return False