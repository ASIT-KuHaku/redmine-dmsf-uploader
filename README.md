redmine-attacher
================

使用python脚本上传文件到redmine的文件库，支持明文保存用户名和密码（不安全）。
Simple python script for attaching files to a Redmine page.

Redmine version: 4.2.10.stable

Depends on Mechanize:
https://pypi.python.org/pypi/mechanize/

Examples:
---------
```bash
# 例：指定基本url、上传网址url和文件
> python redmine-attacher.py -b https://your.redmine.com -u https://your.redmine.com/projects/test_project/files/new file1

# Specify each file individually with full url for the Redmine page
> python redmine-attacher.py -u <full-page-url> file1 file2 ... fileN

# Wildcard expansion is done by the shell
> python redmine-attacher.py -u <full-page-url> file*
```