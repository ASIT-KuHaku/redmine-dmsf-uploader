#!/usr/bin/env python3

import os
import time
import copy

from urllib.parse import urlparse, parse_qs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

class DmsfFolderInfo:
    def __init__(self, folder_name=None, folder_id=None, memberfolder=None):
        self.folder_name = folder_name
        self.folder_id = folder_id
        self.memberfolder = memberfolder
        if memberfolder==None:
            self.memberfolder = []

    def __str__(self):
        return f"Folder Name: {self.folder_name}, Folder ID: {self.folder_id}"

# 登录到Redmine
def login_redmine(browser, base, username, password):
    login = base + '/login'
    browser.get(login)
    username_input = browser.find_element(By.ID, "username")
    password_input = browser.find_element(By.ID, "password")
    username_input.send_keys(username.decode('utf-8'))
    password_input.send_keys(password.decode('utf-8'))
    password_input.submit()

    # 等待登录成功
    time.sleep(0.1)  # 根据实际情况调整等待时间

    # 确认登录是否成功
    if username.decode('utf-8') not in browser.page_source:
        return False
    else:
        return True

# 上传文件——file
def uploadFiles_file(browser, url, filename):
    browser.get(url)
    file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
    file_path = os.path.abspath(filename)
    file_input.send_keys(file_path)
    time.sleep(0.1)  # 根据实际情况调整等待时间
    browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

# 上传文件——DMSF
def uploadFiles_dmsf(browser, base, project, filename, rootFolderInfo):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'
    uploadUrl = dmsfRootUrl + '/upload/multi_upload'

    if rootFolderInfo==None or rootFolderInfo.folder_id==None:
        pass
    else:
        uploadUrl=uploadUrl + '?folder_id=' + str(rootFolderInfo.folder_id)
    #---------------------------------------------------------------------
    print("uploadUrl:",uploadUrl)
    #---------------------------------------------------------------------

    file_path = os.path.abspath(filename)
    
    browser.get(uploadUrl)
    file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
    #---------------------------------------------------------------------
    print("file_path:",file_path)
    #---------------------------------------------------------------------
    file_input.send_keys(file_path)
    time.sleep(0.1)  # 根据实际情况调整等待时间
    browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    time.sleep(0.1)  # 根据实际情况调整等待时间

    # 提交
    browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    time.sleep(0.1)  # 根据实际情况调整等待时间
    
# 获取DMSF文件夹列表
def getFolderInfo(browser, base, project, rootFolderInfo=None):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'

    if rootFolderInfo==None or rootFolderInfo.folder_id==None:
        workUrl=dmsfRootUrl
        rootFolderInfo=DmsfFolderInfo()
    else:
        workUrl=dmsfRootUrl + '?folder_id=' + str(rootFolderInfo.folder_id)

    browser.get(workUrl)
    
    # 等待文件夹列表加载完成
    try:
        # 等待直到document.readyState为complete
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))  # 选择一个页面上已经存在的元素
        )
    except TimeoutException:
        raise Exception("Timed out waiting for page to load")

    try:
        folder_table = browser.find_element(By.CLASS_NAME, 'list')
    except NoSuchElementException:
        # print(f"[{rootFolderInfo.folder_name}:{workUrl}]Folder table not found. Handle the case accordingly.")
        return rootFolderInfo
    
    folders_elements = folder_table.find_elements(By.XPATH, '//tr[contains(@class, "dmsf-tree") and contains(@class, "dmsf-collapsed")]')

    # 存储文件夹信息的列表
    folder_info_list = []

    for folder in folders_elements:
        folder_name_element = folder.find_element(By.CLASS_NAME, 'icon-folder')
        folder_name = folder_name_element.text

        folder_link_element = folder.find_element(By.XPATH, './/a[contains(@class, "icon-folder")]')
        folder_link = folder_link_element.get_attribute('href')

        parsed_url = urlparse(folder_link)
        query_params = parse_qs(parsed_url.query)
        folder_id = query_params.get('folder_id', [])[0]  # 获取 folder_id 参数的值

        # print(f"folder_name:{folder_name}, folder_id:{folder_id}")
        tmpFolderInfo=DmsfFolderInfo(folder_name, folder_id)
        folder_info_list.append(tmpFolderInfo)

    for folderInfo in folder_info_list:
        if folderInfo==None:
            print('None')
            continue
        # 递归遍历
        tmpFolderInfo=getFolderInfo(browser, base, project, folderInfo)
        if tmpFolderInfo == None or tmpFolderInfo.folder_name==None:
            continue
        else:
            rootFolderInfo.memberfolder.append(tmpFolderInfo)

    browser.get(workUrl)

    return rootFolderInfo

def find_folder_by_name(rootFolderInfo, foldername):  
    # 遍历 rootFolderInfo 的 memberfolder 列表  
    for folder in rootFolderInfo.memberfolder:  
        # 如果 folder 的 folder_name 与指定的 foldername 匹配，返回该folder
        if folder.folder_name == foldername:  
            return folder  
    # 如果没有找到匹配的 folder_name，则返回 None  
    return None

# 上传目录下的所有文件——DMSF
def uploadFolder_dmsf(browser, base, project, folder_path, rootFolderInfo):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'
    uploadUrl = dmsfRootUrl + '/upload/multi_upload'

    if rootFolderInfo==None or rootFolderInfo.folder_id==None:
        pass
    else:
        uploadUrl=uploadUrl + '?folder_id=' + str(rootFolderInfo.folder_id)

    #---------------------------------------------------------------------
    print("uploadUrl:",uploadUrl)
    #---------------------------------------------------------------------

    # 获取文件夹中的所有项目
    all_items = os.listdir(folder_path)
    # 获取文件夹下的所有文件
    subfiles   = [f for f in all_items if os.path.isfile(os.path.join(folder_path, f))]
    # 筛选出子文件夹
    subfolders = [f for f in all_items if os.path.isdir(os.path.join(folder_path, f))]

    for filename in subfiles:
        file_path = os.path.abspath(os.path.join(folder_path, filename))

        browser.get(uploadUrl)
        file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        #---------------------------------------------------------------------
        print("file_path:",file_path)
        #---------------------------------------------------------------------
        file_input.send_keys(file_path)
        time.sleep(0.1)  # 根据实际情况调整等待时间
        browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        time.sleep(0.1)  # 根据实际情况调整等待时间

        # 提交
        browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        time.sleep(0.1)  # 根据实际情况调整等待时间

    for foldername in subfolders:
        file_path = os.path.abspath(os.path.join(folder_path, foldername))
        #---------------------------------------------------------------------
        print("file_path:",file_path)
        #---------------------------------------------------------------------
        dmsfFolder = find_folder_by_name(rootFolderInfo, foldername)
        if dmsfFolder==None:
            print(f"DMSF不存在对应文件夹:{foldername}")
            return
        else:
            uploadFolder_dmsf(browser, base, project, file_path, dmsfFolder)
