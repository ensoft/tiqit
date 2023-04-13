#!/usr/bin/python3
#
# Copyright (c) 2017 Ensoft Ltd, 2008-2010 Martin Morrison, Matthew Earl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

# Pretty stack traces but with 500 status codes
import cgitb, sys
sys.path.append("../scripts")
sys.path.append("../scripts/plugins")
sys.path.insert(0, '../scripts/tiqit.zip')
def excHandler(*args):
    print("<!--: spam")
    print("Status: 500")
    cgitb.handler(args)
sys.excepthook = excHandler

from tiqit import *
import os, re, sys, urllib.request, urllib.parse, urllib.error, codecs, subprocess, locale

# Set environment variables so that processes called by Tiqit interpret
# decode/encode input/output as UTF-8.
# @@@ JL: Need to stop output as bytes? 
#for envvar in ['LC_ALL', 'LANG', 'LANGUAGE']:
#    os.environ[envvar] = 'en_US.UTF-8'

#
# Force stdout to encode output as UTF-8. By default Python will try to
# interpret unicode strings as ASCII and will fail when it encounters a byte 
# greater than 127.
# 
# @@@ JL: Need to stop output as bytes? 
#sys.stdout = codecs.getwriter('utf8')(sys.stdout)

#
# Functions
#

def addSlash():
    #
    # They need a trailing slash - redirect them.
    #
    bits = os.environ['REQUEST_URI'].split('?')
    location = bits[0] + '/'
    if len(bits) > 1:
        location += '?' + bits[1]

    redirect(location, 302)

def errorPage(code, msg=""):
    print("""Content-type: text/html
Status: %d

<html>
  <head>
    <title>Error - %d</title>
  </head>
  <body>
    <h1>Error - %d</h1>
    %s
  </body>
</html>""" % (code, code, code, msg))

if 'PATH_INFO' not in os.environ:
    addSlash()

#
# Work around a bug in the mod_rewrite module that expands encoded strings by
# extracting PATH_INFO and QUERY_STRING manually.
# 
scriptSuffix = "/api/api.py"
assert os.environ['SCRIPT_NAME'].endswith(scriptSuffix), "Script name '%s' does not end with '%s'" % (os.environ['SCRIPT_NAME'], scriptSuffix)
basepath = os.environ['SCRIPT_NAME'][0:-len(scriptSuffix)]
assert os.environ['REQUEST_URI'].startswith(basepath), "Request URI '%s' does not start with '%s'" % (os.environ['REQUEST_URI'], basepath)
relativeReqUri = os.environ['REQUEST_URI'][len(basepath):]
parts = relativeReqUri.split('?', 1)
os.environ['PATH_INFO'] = parts[0]
os.environ['QUERY_STRING'] = parts[1] if len(parts) > 1 else ""

# The first path segment MUST be "api", which we want to remove so we can treat
# this page like regular requests from now on
if os.environ['PATH_INFO'].startswith("/api/"):
    os.environ['PATH_INFO'] = os.environ['PATH_INFO'][4:]
else:
    errorPage(500, os.environ['PATH_INFO'])

path = os.environ['PATH_INFO'].lstrip('/').split('/')

# Initialise the database
initialise()

#
# authenticate the user if required
#
authenticate()

#
# So we have a path. Check if it's a known page.
#
# Note: "pages" and "repages" here are the subset of pages from index.py that
# are supported by the tiqit remote API. This can be expanded if required.
#
metasite = bool(re.search('^%s$' % Config().get('general', 'metaurlmatch'), os.environ['HTTP_HOST']))
pages = {
    'results.py': ('pages.results', None),
    'results': ('pages.results', None),
}

repages = [
    (re.compile('results/[a-z0-9]+/.*$'), ('pages.results', ['action', 'fromuser', 'byname'])),
    (re.compile('results/[^/]+$'), ('pages.results', ['action', 'byname'])),
]

# Let plugins register their pages
plugins.addApiPages(repages, pages)

for regex, pagedata in repages:
    if regex.match('/'.join(path)):
        page = pagedata
        break
else:
    if path[0] in pages:
        page = pages[path[0]]
    else:
        errorPage(404, '/'.join(path))
        sys.exit(1)

#
# If they've defined an argument parser, call it now
#
if callable(page[1]):
    page[1](path)
elif page[1]:
    # Resplit the path to to merge superfluous arguments, to allow for example
    # looking up a "TCP/IP" named search where the "/" is unencoded.
    path = os.environ['PATH_INFO'].lstrip('/').split('/', len(page[1]) - 1)
    args = '&'.join(map('='.join, list(zip(page[1], path))))
    if os.environ['QUERY_STRING']:
        os.environ['QUERY_STRING'] += '&%s' % args
    else:
        os.environ['QUERY_STRING'] = args

#
# Now import the required module
#
try:
    mod = __import__(page[0])
except TiqitException:
    raise
except Exception:
    errorPage(500)
    raise
