redmine-attacher
================

使用python脚本上传文件到redmine的文件库和DMSF（文档管家），支持明文保存用户名和密码（不安全），支持按目录结构上传到指定项目的DMSF（暂时需先在DMSF创建对应文件夹）。
Simple python script for attaching files to a Redmine page.

Redmine version: 4.2.10.stable

pip install argparse selenium

Examples:
---------
```bash
# 例：指定基本url、上传网址url和文件
> python redmine-attacher.py -b https://your.redmine.com -u https://your.redmine.com/projects/test_project/files/new file1

# 上传文件和文件夹到测试项目test_project
> python redmine-attacher.py -b https://your.redmine.com  -p test_project file1 folder1 file2

# Specify each file individually with full url for the Redmine page
> python redmine-attacher.py -u <full-page-url> file1 file2 ... fileN

# Wildcard expansion is done by the shell
> python redmine-attacher.py -u <full-page-url> file*
```
