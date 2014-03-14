#!/usr/bin/env python
"""
Simple python script for attaching files to a redmine page.

Depends on Mechanize:
https://pypi.python.org/pypi/mechanize/

@authors: Alex Drlica-Wagner    <kadrlica@fnal.gov>
"""
import getpass
import argparse

import mechanize
import mimetypes

description = "A simple script to upload files to a Redmine page."
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-b','--base',default='https://cdcvs.fnal.gov/redmine',
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

print "Redmine login..."
username=''
password=''
while (len(username)==0):
    username=raw_input('Username: ')
while (len(password)==0):
    password=getpass.getpass()

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

# Upload files
for filename in files:
    print "Uploading %s..."%filename
    page = browser.open(url)
    browser.select_form(predicate=lambda f: 'action' in f.attrs and f.attrs['action'].endswith('/add_attachment'))
    filedata = open(filename,'rb')
    filetype = mimetypes.guess_type(filename)[0]
    browser.add_file(filedata, content_type=filetype, filename=filename)
    page = browser.submit()
