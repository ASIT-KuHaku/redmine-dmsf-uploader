#!/usr/bin/env python3

# 保存page
def savePage(page, path):
    # 读取页面内容并解码为字符串
    html_content = page.read().decode('utf-8')
    # 将内容写入HTML文件
    with open(path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)
    print("页面内容已保存")

# 打印页面表单
def print_browserforms(browser):
    # 获取页面中的所有表单
    forms = list(browser.forms())
    # 遍历每个表单
    for form in forms:
        print(f"Form Action: {form.action}")
        
        # 遍历表单中的每个控件
        for control in form.controls:
            print(f"  Control Name: {control.name}, Type: {control.type}, Value: {control.value}")
