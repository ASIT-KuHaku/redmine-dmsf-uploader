#!/usr/bin/env python3

"""
使用python脚本上传文件到redmine。
Simple python script for attaching files to a redmine page.

pip install argparse mechanize

Depends on Mechanize: https://pypi.python.org/pypi/mechanize/

@authors: Alex Drlica-Wagner <kadrlica@fnal.gov> and kuhaku
"""

import getpass
import argparse

import mechanize
import mimetypes

from utils.save_password import *
from utils.print_save import *

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

login = base+'/login'

browser = mechanize.Browser()
browser.set_handle_robots(False)

# Login to Redmine
page = browser.open(login)  
browser.select_form(predicate=lambda f: 'action' in f.attrs and f.attrs['action'].endswith('/login'))
browser["username"] = username
browser["password"] = password

try:
    page = browser.submit()
except:
    raise Exception("Login failed")

# Check if login was successful
if username not in page.get_data():
    raise Exception("Login failed")

# Upload files——file
def uploadFiles_file():
    for filename in files:
        print("Uploading %s..."%filename)
        # 打开页面
        page = browser.open(url)
        # 调试时
        # savePage(page, 'output.html')
        browser.select_form(predicate=lambda f: 'action' in f.attrs and f.attrs['action'].endswith('/files'))
        filedata = open(filename,'rb')
        filetype = mimetypes.guess_type(filename)[0]
        browser.add_file(filedata, content_type=filetype, filename=filename)
        page = browser.submit()

uploadFiles_file()
