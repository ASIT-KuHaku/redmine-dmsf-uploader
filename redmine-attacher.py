#!/usr/bin/env python3

"""
使用python脚本上传文件到redmine的文件库和DMSF（文档管家），支持明文保存用户名和密码（不安全）。
Simple python script for attaching files to a Redmine page.

Redmine version: 4.2.10.stable

pip install argparse selenium

@authors: kuhaku, ChatGPT<chat.openai.com>, 文心一言<yiyan.baidu.com>, Alex Drlica-Wagner<kadrlica@fnal.gov>
"""

import getpass
import argparse
import time

from utils.save_password import *
from utils.print_save import *

from selenium import webdriver
from selenium.webdriver.common.by import By

description = "A simple script to upload files to a Redmine page."
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-b', '--base', default='https://your.redmine.com',  # 可设置的redmine网址
                    help="Base URL for Redmine.")
parser.add_argument('-u', '--url', default=None, type=str, required=True,
                    help="URL of Redmine page for upload.")
parser.add_argument('files', nargs=argparse.REMAINDER)
opts = parser.parse_args()
url = opts.url
base = opts.base
files = opts.files

if not len(files):
    raise Exception("No files to upload")

print("Redmine login...")
username = b''
password = b''

# 检测配置文件
config_file_path = 'config.ini'

if check_config_file(config_file_path):
    # 执行其他操作，使用配置文件中的内容
    print("Config file and content are valid.")

    # 读取用户名和密码
    username, password = read_credentials()
    # 打印读取到的用户名和密码
    print(f"Username: {username.decode('utf-8', errors='ignore')}")
    print(f"Password: {'*' * len(password.decode('utf-8', errors='ignore'))}")

while len(username) == 0:
    username = input('Username: ').encode('utf-8')
while len(password) == 0:
    password = getpass.getpass().encode('utf-8')

login = base + '/login'

# 启动浏览器
browser = webdriver.Chrome()

# 登录到Redmine
browser.get(login)
username_input = browser.find_element(By.ID, "username")
password_input = browser.find_element(By.ID, "password")
username_input.send_keys(username.decode('utf-8'))
password_input.send_keys(password.decode('utf-8'))
password_input.submit()

# 等待登录成功
time.sleep(2)  # 根据实际情况调整等待时间

# 确认登录是否成功
if username.decode('utf-8') not in browser.page_source:
    raise Exception("Login failed")

# 上传文件——file
def uploadFiles_file():
    for filename in files:
        print("Uploading %s..." % filename)
        browser.get(url)
        file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        file_path = os.path.abspath(filename)
        file_input.send_keys(file_path)
        time.sleep(2)  # 根据实际情况调整等待时间
        browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

# 上传文件——DMSF
def uploadFiles_dmsf():
    for filename in files:
        print("Uploading %s..." % filename)
        browser.get(url)
        file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        file_path = os.path.abspath(filename)
        file_input.send_keys(file_path)
        time.sleep(2)  # 根据实际情况调整等待时间
        browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        time.sleep(2)  # 根据实际情况调整等待时间

        # 提交
        browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        time.sleep(2)  # 根据实际情况调整等待时间

# uploadFiles_file()
uploadFiles_dmsf()
