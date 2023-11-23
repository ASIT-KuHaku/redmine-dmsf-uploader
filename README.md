redmine-dmsf-uploader(redmine-attacher)
================

使用python脚本上传文件到redmine的文件库和DMSF（文档管家）。
1. 支持明文保存用户名和密码（不安全）
2. 支持按目录结构上传到指定项目的DMSF（暂时需先在DMSF创建对应文件夹）
3. 支持上传文件夹，对比本地和服务器文件日期，选择性的上传更新的文件
4. 支持读取dmsf网页目录结构，获取文件名、ID、修改日期

Simple python script for attaching files to a Redmine page, and uploading file to dmsf.

Redmine version: 4.2.10.stable

pip install argparse selenium

Examples:
---------
```bash
# 例：指定基本url、上传网址url和文件
> python redmine-dmsf-uploader.py -b https://your.redmine.com -u https://your.redmine.com/projects/test_project/files/new file1

# 上传文件和文件夹到测试项目test_project
> python redmine-dmsf-uploader.py -b https://your.redmine.com  -p test_project file1 folder1 file2

# Specify each file individually with full url for the Redmine page
> python redmine-dmsf-uploader.py -u <full-page-url> file1 file2 ... fileN

# Wildcard expansion is done by the shell
> python redmine-dmsf-uploader.py -u <full-page-url> file*
```
