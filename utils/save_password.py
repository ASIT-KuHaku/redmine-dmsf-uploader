#!/usr/bin/env python3

import os
import getpass
import configparser

# 保存用户名密码到文件
def save_credentials(username, password, config_file='config.ini'):
    # 创建一个配置解析器对象
    config = configparser.ConfigParser()

    # 将用户名和密码保存到配置文件中
    config['Credentials'] = {'Username': username, 'Password': password}

    # 打开配置文件并写入配置信息
    with open(config_file, 'w') as configfile:
        config.write(configfile)

# 保读取配置文件的用户名密码
def read_credentials(config_file='config.ini'):
    # 创建一个配置解析器对象
    config = configparser.ConfigParser()

    # 读取配置文件中的用户名和密码
    config.read(config_file)
    username = config.get('Credentials', 'Username', fallback=None).encode('utf-8')
    password = config.get('Credentials', 'Password', fallback=None).encode('utf-8')

    return username, password

# 检测配置文件有效性
def check_config_file(file_path):
    # 检查文件是否存在
    if not os.path.isfile(file_path):
        print(f"Error: Config file '{file_path}' not found.")
        return False

    # 读取配置文件
    config = configparser.ConfigParser()
    try:
        config.read(file_path)
        # 检查配置文件中是否包含必要的部分
        if 'Credentials' in config and 'username' in config['Credentials'] and 'password' in config['Credentials']:
            return True
        else:
            print("Error: Config file is missing required sections or keys.")
            return False
    except configparser.Error as e:
        print(f"Error reading config file '{file_path}': {e}")
        return False

"""
# 检测配置文件
config_file_path = 'config.ini'

if check_config_file(config_file_path):
    # 执行其他操作，使用配置文件中的内容
    print("Config file and content are valid.")

    # 读取用户名和密码
    stored_username, stored_password = read_credentials()
    # 打印读取到的用户名和密码
    print(f"Stored Username: {stored_username}")
    print(f"Stored Password: {'*' * len(stored_password)}")
else:
    # 处理配置文件不存在或内容不符合预期的情况
    print("配置文件不存在或内容不符合预期，重新配置")
    
    username = input('Username: ')
    password = getpass.getpass()
    # 保存用户名和密码
    save_credentials(username, password)

    print("配置结束")
"""