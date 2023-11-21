#!/usr/bin/env python3

"""
使用python脚本上传文件到redmine。
Simple python script for attaching files to a redmine page.

pip install argparse mechanize

Depends on Mechanize:
https://pypi.python.org/pypi/mechanize/

@authors: Alex Drlica-Wagner <kadrlica@fnal.gov> and kuhaku
"""

import getpass
import argparse

import mechanize
import mimetypes

description = "A simple script to upload files to a Redmine page."
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-b','--base',default='https://your.redmine.com', # 可设置的redmine网址
                    help="Base URL for Redmine.")
parser.add_argument('-u','--url',default=None,type=str,required=True,
                    help="URL of Redmine page for upload.")
parser.add_argument('files',nargs=argparse.REMAINDER)
opts = parser.parse_args(); 
url = opts.url
base = opts.base
files = opts.files

if not len(files):
    raise Exception("No files to upload")

print("Redmine login...")
username = b''
password = b''
while len(username) == 0:
    username = input('Username: ').encode('utf-8') # b''
while len(password) == 0:
    password = getpass.getpass().encode('utf-8') # b''

login = base+'/login'

browser = mechanize.Browser()
browser.set_handle_robots(False)

# Login to Redmine
page = browser.open(login)  
browser.select_form(predicate=lambda f: 'action' in f.attrs and f.attrs['action'].endswith('/login'))
browser["username"] = username #kuhaku
browser["password"] = password
try:
    page = browser.submit()
except:
    raise Exception("Login failed")

# Check if login was successful
if username not in page.get_data():
    raise Exception("Login failed")

# Upload files
for filename in files:
    print("Uploading %s..."%filename)
    # 打开页面
    page = browser.open(url)
    # 调试时
    """
    # 读取页面内容并解码为字符串
    html_content = page.read().decode('utf-8')
    # 将内容写入HTML文件
    with open('output.html', 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)
    print("页面内容已保存到 output.html 文件中。")
    """
    browser.select_form(predicate=lambda f: 'action' in f.attrs and f.attrs['action'].endswith('/files'))
    filedata = open(filename,'rb')
    filetype = mimetypes.guess_type(filename)[0]
    browser.add_file(filedata, content_type=filetype, filename=filename)
    page = browser.submit()
