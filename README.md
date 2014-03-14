redmine-attacher
================

Simple python script for attaching files to a Redmine page.

Depends on Mechanize:
https://pypi.python.org/pypi/mechanize/

Examples:
---------
```bash
# Specify each file individually with full url for the Redmine page
> python redmine-attacher.py -u <full-page-url> file1 file2 ... fileN

# Wildcard expansion is done by the shell
> python redmine-attacher.py -u <full-page-url> file*
```