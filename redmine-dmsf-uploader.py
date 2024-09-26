#!/usr/bin/env python3

"""

使用python脚本上传文件到redmine的文件库和DMSF（文档管家）。
1. 支持明文保存用户名和密码（不安全）
2. 支持按目录结构上传到指定项目的DMSF（暂时需先在DMSF创建对应文件夹）
3. 支持上传文件夹，对比本地和服务器文件日期，选择性的上传更新的文件
4. 支持读取dmsf网页目录结构，获取文件名、ID、修改日期
5. 支持.gitignore文件，匹配忽略文件

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
config_file_path = 'redmine-dmsf-uploader-config.ini'

if check_config_file(config_file_path):
    # 执行其他操作，使用配置文件中的内容
    print("Config file and content are valid.")

    # 读取用户名和密码
    username, password = read_credentials(config_file_path)
    # 打印读取到的用户名和密码
    print(f"Username: {username.decode('utf-8', errors='ignore')}")
    print(f"Password: {'*' * len(password.decode('utf-8', errors='ignore'))}")

while len(username) == 0:
    username = input('Username: ').encode('utf-8')
while len(password) == 0:
    password = getpass.getpass().encode('utf-8')

# 启动浏览器 
browser=None 
if False:
# 启动浏览器(无界面模式，待测试)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)
else:
    browser = webdriver.Chrome()
    
# 登录到Redmine
if login_redmine(browser, base, username, password, sleeptime=0.5)==True:
    print("登陆成功.")
else:
    raise Exception("Login failed")

def traverse_and_print(folder_info_list, depth=0):
    for folder_info in folder_info_list:
        if folder_info.type=='folder':
            print("  " * depth + str(folder_info))
            traverse_and_print(folder_info.memberfile, depth + 1)
        else:
            print("  " * depth + str(folder_info))

# 上传
if project==None:
    for filename in files:
        print("Uploading %s..." % filename)
        # uploadFiles_file()
        uploadFiles_dmsf(browser, url, filename)
else:
    print("project:",project)
    
    rootFolderInfo=getPathInfo(browser, base, project, rootFolderInfo=None)
    #---------------------------------------------------------------------
    # 打印结果
    traverse_and_print(rootFolderInfo.memberfile)
    time.sleep(0.1)  # 根据实际加载时间调整等待时间
    #---------------------------------------------------------------------
    for filename in files:
        print("Uploading %s..." % filename)
        # uploadFiles_file()
        if os.path.isfile(filename):
            uploadFiles_dmsf(browser, base, project, filename, rootFolderInfo, sleeptime=0.1)
        elif os.path.isdir(filename):
            uploadFolder_dmsf(browser, base, project, filename, rootFolderInfo, sleeptime=0.1, updateByTime=True)
        else:
            print(f"[{filename}]无效")
