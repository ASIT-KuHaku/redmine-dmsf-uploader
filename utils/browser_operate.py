#!/usr/bin/env python3

import os
import time
import re
import fnmatch

from datetime import datetime
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

class DmsfFileInfo:
    def __init__(self, file_name=None, file_id=None, memberfile=None, type=None, modificationDate=None):
        self.file_name = file_name
        self.file_id = file_id
        self.memberfile = memberfile
        self.modificationDate = modificationDate
        self.type = type
        if memberfile==None:
            self.memberfile = []

    def __str__(self):
        if self.type=='file':
            return f"File Name: {self.file_name}, ID: {self.file_id}, Date: {self.modificationDate}"
        elif self.type=='folder':
            return f"Folder Name: {self.file_name}, ID: {self.file_id}, Date: {self.modificationDate}"
        else:
            return f"NoneType Name: {self.file_name}, ID: {self.file_id}, Date: {self.modificationDate}"

# 登录到Redmine
def login_redmine(browser, base, username, password, sleeptime=0.1):
    login = base + '/login'
    browser.get(login)
    username_input = browser.find_element(By.ID, "username")
    password_input = browser.find_element(By.ID, "password")
    username_input.send_keys(username.decode('utf-8'))
    password_input.send_keys(password.decode('utf-8'))
    password_input.submit()

    # 等待登录成功
    time.sleep(sleeptime)

    # 确认登录是否成功
    if username.decode('utf-8') not in browser.page_source:
        return False
    else:
        return True

# 上传文件——file
def uploadFiles_file(browser, url, filename, sleeptime=0.1):
    browser.get(url)
    file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
    file_path = os.path.abspath(filename)
    file_input.send_keys(file_path)
    time.sleep(sleeptime)
    browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

# 上传文件——DMSF
def uploadFiles_dmsf(browser, base, project, filename, rootFolderInfo=None, sleeptime=0.1):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'
    uploadUrl = dmsfRootUrl + '/upload/multi_upload'

    if rootFolderInfo==None or rootFolderInfo.file_id==None:
        pass
    else:
        if rootFolderInfo.type=='file':
            raise Exception("错误：非文件夹")
        uploadUrl=uploadUrl + '?folder_id=' + str(rootFolderInfo.file_id)
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
    time.sleep(sleeptime)
    browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    time.sleep(sleeptime)

    # 提交
    browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    time.sleep(sleeptime)

# 获取DMSF文件夹列表
def getFolderInfo(browser, base, project, rootFolderInfo=None):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'

    if rootFolderInfo==None or rootFolderInfo.file_id==None:
        workUrl=dmsfRootUrl
        rootFolderInfo=DmsfFileInfo(type='folder')
    else:
        if rootFolderInfo.type=='file':
            raise Exception("错误：非文件夹")
        workUrl=dmsfRootUrl + '?folder_id=' + str(rootFolderInfo.file_id)

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
        # print(f"[{rootFolderInfo.file_name}:{workUrl}]Folder table not found. Handle the case accordingly.")
        return rootFolderInfo
    
    folders_elements = folder_table.find_elements(By.XPATH, '//tr[contains(@class, "dmsf-tree") and contains(@class, "dmsf-collapsed")]')

    # 存储文件夹信息的列表
    folder_info_list = []

    for folder in folders_elements:
        # 文件夹名
        folder_name_element = folder.find_element(By.CLASS_NAME, 'icon-folder')
        folder_name = folder_name_element.text

        # 文件夹id
        folder_link_element = folder.find_element(By.XPATH, './/a[contains(@class, "icon-folder")]')
        folder_link = folder_link_element.get_attribute('href')

        parsed_url = urlparse(folder_link)
        query_params = parse_qs(parsed_url.query)
        folder_id = query_params.get('folder_id', [])[0]  # 获取 folder_id 参数的值

        # 文件夹日期
        dateelement = folder.find_element(By.CSS_SELECTOR, "td.modified span:first-child")
        date_from_web = dateelement.text

        # 创建文件夹信息对象
        print(f"folder_name:{folder_name}, folder_id:{folder_id}, date:{date_from_web}")
        tmpFolderInfo=DmsfFileInfo(file_name=folder_name, file_id=folder_id, type='folder', modificationDate=date_from_web)
        folder_info_list.append(tmpFolderInfo)

    for folderInfo in folder_info_list:
        if folderInfo==None:
            print('None')
            continue
        # 递归遍历
        tmpFolderInfo=getFolderInfo(browser, base, project, folderInfo)
        if tmpFolderInfo == None or tmpFolderInfo.file_name==None:
            continue
        else:
            rootFolderInfo.memberfile.append(tmpFolderInfo)

    browser.get(workUrl)

    return rootFolderInfo

# 获取DMSF目录列表（文件夹和文件）
def getPathInfo(browser, base, project, rootFolderInfo=None):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'

    if rootFolderInfo is None or rootFolderInfo.file_id is None:
        workUrl = dmsfRootUrl
        rootFolderInfo = DmsfFileInfo(type='folder')
    else:
        if rootFolderInfo.type == 'file':
            raise Exception("错误：非文件夹")
        workUrl = dmsfRootUrl + '?folder_id=' + str(rootFolderInfo.file_id)

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
        return rootFolderInfo
    
    folders_elements = folder_table.find_elements(By.XPATH, '//tr[contains(@class, "dmsf-tree") and contains(@class, "dmsf-collapsed")]')
    files_elements = folder_table.find_elements(By.XPATH, '//tr[contains(@class, "dmsf-tree") and contains(@class, "dmsf-child")]')

    # 存储文件夹信息的列表
    folder_info_list = []
    file_info_list = []

    for folder in folders_elements:
        # 文件或文件夹名
        file_name_element = folder.find_element(By.CLASS_NAME, 'dmsf-title')
        file_name = file_name_element.text.strip()

        # 文件或文件夹链接
        file_link_element = file_name_element.find_element(By.TAG_NAME, 'a')
        file_link = file_link_element.get_attribute('href')

        parsed_url = urlparse(file_link)
        query_params = parse_qs(parsed_url.query)
        file_id = query_params.get('folder_id', [None])[0]  # 获取 folder_id 参数的值，对于文件则为 None

        # 文件或文件夹日期
        date_element = folder.find_element(By.CSS_SELECTOR, "td.modified span:first-child")
        date_from_web = date_element.text.strip()

        # 创建文件夹信息对象
        #---------------------------------------------------------------------
        # print(f"folder_name:{file_name}, file_id:{file_id}, date:{date_from_web}")
        #---------------------------------------------------------------------
        tmpFileInfo = DmsfFileInfo(file_name=file_name, file_id=file_id, type='folder', modificationDate=date_from_web)
        folder_info_list.append(tmpFileInfo)

    for file in files_elements:
        # 文件或文件夹名
        file_name_element = file.find_element(By.CLASS_NAME, 'dmsf-title')
        file_name = file_name_element.find_element(By.CLASS_NAME, 'dmsf-filename').text.strip()

        # 文件或文件夹链接
        file_link_element = file_name_element.find_element(By.TAG_NAME, 'a')
        file_link = file_link_element.get_attribute('href')

        match = re.search(r'files/(\d+)/view', file_link)
        if match:
            file_id = match.group(1)
        else:  
            file_id=None

        # 文件或文件夹日期
        date_element = file.find_element(By.CSS_SELECTOR, "td.modified span:first-child")
        date_from_web = date_element.text.strip()

        # 创建文件信息对象
        #---------------------------------------------------------------------
        # print(f"file_name:{file_name}, file_id:{file_id}, date:{date_from_web}, file_link:{file_link}")
        #---------------------------------------------------------------------
        tmpFileInfo = DmsfFileInfo(file_name=file_name, file_id=file_id, type='file', modificationDate=date_from_web)
        file_info_list.append(tmpFileInfo)

    for folderInfo in folder_info_list:
        if folderInfo==None:
            # print('None')
            continue
        # 递归遍历
        tmpFolderInfo=getPathInfo(browser, base, project, folderInfo)
        if tmpFolderInfo == None or tmpFolderInfo.file_name==None:
            continue
        else:
            rootFolderInfo.memberfile.append(tmpFolderInfo)

    for fileInfo in file_info_list:
        if fileInfo==None:
            continue
        rootFolderInfo.memberfile.append(fileInfo)

    browser.get(workUrl)

    return rootFolderInfo

# 遍历rootFolderInfo找到对应文件，返回其FileInfo
def findFileByName(rootFolderInfo, filename):
    if rootFolderInfo==None:
        raise Exception("FolderInfo is None.")
    # 文件检测
    if rootFolderInfo.type=='file':
        raise Exception("文件不支持遍历。")
    elif rootFolderInfo.type=='folder':
    # 遍历 rootFolderInfo 的 memberfile 列表  
        for fileInfo in rootFolderInfo.memberfile:  
            # 如果 fileInfo 的 filename 与指定的 filename 匹配，返回该folder
            if fileInfo.file_name == filename:  
                return fileInfo  
    # 如果没有找到匹配的 file_name，则返回 None
    else:
        return None

# 使用os.path模块的basename函数来提取文件夹名称
def extract_folder_name(path):
    return os.path.basename(os.path.normpath(path))

# 创建文件夹
def mkfolder_dmsf(browser, base, project, inputFolder, rootFolderInfo=None, sleeptime=0.1):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'
    uploadUrl = dmsfRootUrl + '/new'

    if rootFolderInfo==None or rootFolderInfo.file_id==None:
        pass
    else:
        if rootFolderInfo.type=='file':
            raise Exception("错误：非文件夹")
        uploadUrl=uploadUrl + '?parent_id=' + str(rootFolderInfo.file_id)
    #---------------------------------------------------------------------
    # print("uploadUrl:",uploadUrl)
    #---------------------------------------------------------------------
    foldername=extract_folder_name(inputFolder)
    
    browser.get(uploadUrl)
    #---------------------------------------------------------------------
    # print("folder_path:",folder_path)
    #---------------------------------------------------------------------
    dmsf_folder_title = browser.find_element(By.ID, "dmsf_folder_title")
    # dmsf_folder_description = browser.find_element(By.ID, "dmsf_folder_description") #textarea
    dmsf_folder_title.send_keys(foldername)
    time.sleep(sleeptime)
    dmsf_folder_title.submit()
    time.sleep(sleeptime)
    
    return True

# 在dmsf根据文件夹名找到文件夹
def findFolderInfo(browser, base, project, findFoldName, rootFolderInfo=None):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'

    if rootFolderInfo==None or rootFolderInfo.file_id==None:
        workUrl=dmsfRootUrl
        rootFolderInfo=DmsfFileInfo(type='folder')
    else:
        if rootFolderInfo.type=='file':
            raise Exception("错误：非文件夹")
        workUrl=dmsfRootUrl + '?folder_id=' + str(rootFolderInfo.file_id)

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
        # print(f"[{rootFolderInfo.file_name}:{workUrl}]Folder table not found. Handle the case accordingly.")
        return None
    
    folders_elements = folder_table.find_elements(By.XPATH, '//tr[contains(@class, "dmsf-tree") and contains(@class, "dmsf-collapsed")]')

    # 存储文件夹信息的列表
    folder_info_list = []

    for folder in folders_elements:
        folder_name_element = folder.find_element(By.CLASS_NAME, 'icon-folder')
        folder_name = folder_name_element.text

        if findFoldName==folder_name:
            folder_link_element = folder.find_element(By.XPATH, './/a[contains(@class, "icon-folder")]')
            folder_link = folder_link_element.get_attribute('href')

            parsed_url = urlparse(folder_link)
            query_params = parse_qs(parsed_url.query)
            folder_id = query_params.get('folder_id', [])[0]  # 获取 folder_id 参数的值

            # 文件夹日期
            dateelement = folder.find_element(By.CSS_SELECTOR, "td.modified span:first-child")
            date_from_web = dateelement.text

            # 创建文件夹信息对象
            # print(f"folder_name:{folder_name}, folder_id:{folder_id}, date:{date_from_web}")
            tmpFolderInfo=DmsfFileInfo(file_name=folder_name, file_id=folder_id, type='folder', modificationDate=date_from_web)
            
            return tmpFolderInfo
        else:
            pass
    
    return None

# 上传目录下的所有文件——DMSF
def uploadFolder_dmsf(browser, base, project, folder_path, rootFolderInfo, sleeptime=0.1, updateByTime=False):
    dmsfRootUrl = base + '/projects/' + project + '/dmsf'
    uploadUrl = dmsfRootUrl + '/upload/multi_upload'

    if rootFolderInfo==None or rootFolderInfo.file_id==None:
        pass
    else:
        if rootFolderInfo.type=='file':
            raise Exception("错误：非文件夹")
        uploadUrl=uploadUrl + '?folder_id=' + str(rootFolderInfo.file_id)

    #---------------------------------------------------------------------
    print("uploadUrl:",uploadUrl)
    #---------------------------------------------------------------------

    # 获取文件夹中的所有项目
    all_items = os.listdir(folder_path)
    # 获取文件夹下的所有文件
    subfiles   = [f for f in all_items if os.path.isfile(os.path.join(folder_path, f))]
    # 筛选出子文件夹
    subfolders = [f for f in all_items if os.path.isdir(os.path.join(folder_path, f))]

    # 读取gitignore
    with open('.gitignore', 'r', encoding='utf-8') as f:
        inputGitignoreInfo = f.readlines()
    # 去除每行的换行符
    inputGitignoreInfo = [line.strip() for line in inputGitignoreInfo]
    inputGitignoreInfo.append('redmine-dmsf-uploader-config.ini')
    inputGitignoreInfo.append('.gitignore')

    # 使用glob模块匹配文件
    gitignoreInfo=[]

    for ignoreInfo in inputGitignoreInfo:
        gitignoreInfo.append(ignoreInfo)
        for root, dirs, files in os.walk('.'):  
            # 匹配文件  
            for file in fnmatch.filter(files, ignoreInfo):  
                gitignoreInfo.append(file)
            # 匹配文件夹  
            for folder in fnmatch.filter(dirs, ignoreInfo):  
                gitignoreInfo.append(folder)
            
    for filename in subfiles:
        # 判断是否需要忽略文件
        if filename in gitignoreInfo:
            continue

        file_path = os.path.abspath(os.path.join(folder_path, filename))
        
        # 判断是否需要更新
        if updateByTime==True:
            # 获取本地文件的修改日期
            fileModifiedtime = os.path.getmtime(file_path)
            modified_time_str = time.ctime(fileModifiedtime)
            local_modified_date = datetime.strptime(modified_time_str, '%a %b %d %H:%M:%S %Y')
            #---------------------------------------------------------------------
            # print(f"本地文件[{filename}]修改时间：", modified_time_str)
            #---------------------------------------------------------------------
            
            web_file=findFileByName(rootFolderInfo, filename)
            if web_file==None:
                # 文件不存在，直接上传
                pass
            else:
                # 文件存在，比较两个日期
                web_date = datetime.strptime(web_file.modificationDate, '%Y-%m-%d %H:%M')
                #---------------------------------------------------------------------
                # print(f"WEB文件[{filename}]修改时间：", web_date)
                #---------------------------------------------------------------------
                # 根据两边修改时间，选择最新的
                if web_date > local_modified_date:
                    # 网页上的日期更新，不上传
                    continue
                elif web_date < local_modified_date:
                    # 本地文件的修改时间更新，上传
                    pass
                else:
                    # 两者日期相同，不上传
                    continue

        browser.get(uploadUrl)
        file_input = browser.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        #---------------------------------------------------------------------
        print("update file_path:",file_path)
        #---------------------------------------------------------------------

        # 传输文件
        file_input.send_keys(file_path)

        # 计算等待时间
        filesize=os.path.getsize(file_path)
        netspeed=1 #MB/s
        waittime=filesize/1024/1024/netspeed
        waittime=waittime*2
        if waittime<10:
            waittime=waittime+10 # 根据运行环境调整

        # 等待完成上传
        try:
            # 等待直到document.readyState为complete
            WebDriverWait(browser, waittime).until(
                EC.presence_of_element_located((By.NAME, 'dmsf_attachments[1][token]'))  # 选择一个页面上已经存在的元素
            )
        except TimeoutException:
            raise Exception("Timed out waiting for page to load")
        time.sleep(sleeptime)

        # 点击上传
        browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        time.sleep(sleeptime)

        # 提交
        browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        time.sleep(sleeptime)

    for foldername in subfolders:
        # 判断是否需要忽略文件
        if foldername in gitignoreInfo:
            continue
        
        file_path = os.path.abspath(os.path.join(folder_path, foldername))
        #---------------------------------------------------------------------
        # print("folder_path:",file_path)
        #---------------------------------------------------------------------
        dmsfFolder = findFileByName(rootFolderInfo, foldername)
        if dmsfFolder==None:
            print(f"DMSF不存在对应文件夹:{foldername}")
            if mkfolder_dmsf(browser, base, project, foldername, rootFolderInfo, sleeptime=sleeptime)==False:
                raise Exception(f"创建DMSF文件夹失败:{foldername}")
            
            dmsfFolder=findFolderInfo(browser, base, project, foldername, rootFolderInfo)
        elif dmsfFolder.type=='file':
            raise Exception(f"创建DMSF文件夹失败:{foldername}, 已存在同名文件.")

        uploadFolder_dmsf(browser=browser, base=base, project=project, folder_path=file_path, rootFolderInfo=dmsfFolder, sleeptime=sleeptime, updateByTime=updateByTime)
