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

from utils.save_password import *
from utils.print_save import *
from utils.browser_operate import *

from selenium import webdriver

# 传入参考
description = "A simple script to upload files to a Redmine page."
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-b', '--base', default='https://your.redmine.com',  # 可设置的redmine网址
                    help="Base URL for Redmine.")
parser.add_argument('-u', '--url', default=None, type=str,
                    help="URL of Redmine page for upload.")
parser.add_argument('-p', '--project', default=None, type=str,
                    help="URL of Redmine page for upload.")
parser.add_argument('files', nargs=argparse.REMAINDER)
opts = parser.parse_args()
url = opts.url
base = opts.base
project = opts.project
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

# 启动浏览器
browser = webdriver.Chrome()
    
# 登录到Redmine
if login_redmine(browser, base, username, password)==True:
    print("登陆成功.")
else:
    raise Exception("Login failed")

def traverse_and_print(folder_info_list, depth=0):
    for folder_info in folder_info_list:
        print("  " * depth + str(folder_info))
        traverse_and_print(folder_info.memberfolder, depth + 1)

# 上传
if project==None:
    for filename in files:
        print("Uploading %s..." % filename)
        # uploadFiles_file()
        uploadFiles_dmsf(browser, url, filename)
else:
    print("project:",project)
    
    #---------------------------------------------------------------------
    rootFolderInfo=getFolderInfo(browser, base, project, rootFolderInfo=None) #, 27
    # 打印结果
    traverse_and_print(rootFolderInfo.memberfolder)
    time.sleep(0.1)  # 根据实际加载时间调整等待时间
    #---------------------------------------------------------------------

    for filename in files:
        print("Uploading %s..." % filename)
        # uploadFiles_file()
        if os.path.isfile(filename):
            uploadFiles_dmsf(browser, base, project, filename, rootFolderInfo)
        elif os.path.isdir(filename):
            uploadFolder_dmsf(browser, base, project, filename, rootFolderInfo)
        else:
            print(f"[{filename}]无效")
