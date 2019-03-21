#!/usr/bin/python
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

def excHandler(*args):
    print "Content-Type: text/html; charset=utf-8"
    print "\r\n\r\n"
    print "<!--: spam"
    print "Status: 500"
    cgitb.handler(args)
sys.excepthook = excHandler
sys.path.insert(0, 'tiqit.zip')

from tiqit import *
import os, re, sys, urllib, codecs, commands, locale

# Set environment variables so that processes called by Tiqit interpret
# decode/encode input/output as UTF-8.
for envvar in ['LC_ALL', 'LANG', 'LANGUAGE']:
    os.environ[envvar] = 'en_US.UTF-8'

#
# Force stdout to encode output as UTF-8. By default Python will try to
# interpret unicode strings as ASCII and will fail when it encounters a byte 
# greater than 127.
# 
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

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

if not os.environ.has_key('PATH_INFO'):
    addSlash()

#
# Work around a bug in the mod_rewrite module that expands encoded strings by
# extracting PATH_INFO and QUERY_STRING manually.
# 
scriptSuffix = "/scripts/index.py"
assert os.environ['SCRIPT_NAME'].endswith(scriptSuffix), "Script name '%s' does not end with '%s'" % (os.environ['SCRIPT_NAME'], scriptSuffix)
basepath = os.environ['SCRIPT_NAME'][0:-len(scriptSuffix)]
assert os.environ['REQUEST_URI'].startswith(basepath), "Request URI '%s' does not start with '%s'" % (os.environ['REQUEST_URI'], basepath)
relativeReqUri = os.environ['REQUEST_URI'][len(basepath):]
parts = relativeReqUri.split('?', 1)
os.environ['PATH_INFO'] = parts[0]
os.environ['QUERY_STRING'] = parts[1] if len(parts) > 1 else ""

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
metasite = bool(re.search('^%s$' % Config().get('general', 'metaurlmatch'), os.environ['HTTP_HOST']))
pages = {
    '': (metasite and 'pages.homemeta' or 'pages.home', None),
    'home': (metasite and 'pages.homemeta' or 'pages.home', None),
    'index.py': (metasite and 'pages.homemeta' or 'pages.home', None),
    'newbug.py': ('pages.newbug', None),
    'newbug': ('pages.newbug', None),
    'search.py': ('pages.search', None),
    'search': ('pages.search', None),
    'prefs.py': ('pages.prefs', None),
    'prefs': ('pages.prefs', None),
    'news.py': ('pages.news', None),
    'news': ('pages.news', None),
    'results.py': ('pages.results', None),
    'results': ('pages.results', None),
    'submit.py': ('actions.submit', None),
    'edit.py': ('actions.edit', None),
    'bugbox.py': ('actions.bugbox', None),
    'bugbox': ('actions.bugbox', None),
    'addfile.py': ('actions.addfile', None),
    'editfile.py': ('actions.editfile', None),
    'editnote.py': ('actions.editnote', None),
    'error.py': ('pages.error', None),
    'error': ('pages.error', None),
    'fetchDefaults': ('helpers.lookup', None),
    'saveprefs.py': ('actions.saveprefs', None),
    'updateprefs.py': ('helpers.updateprefs', None),
    'multiedit.py': ('helpers.multiedit', None),
    'view.py': ('pages.view', None),
    'saveSearch.py': ('helpers.saveSearch', None),
    'userdetails.py': ('helpers.userdetails', None),
    'history.py': ('helpers.history', None),
    'authtoken': ('helpers.authtoken', None),
    'homemeta': ('pages.homemeta', None),
    'fields': ('pages.fields', None),
    'defaultvals': ('pages.defaultvals', None),
    'updatedefvals': ('actions.updatedefvals', None),
}

repages = [
    (re.compile('results/[a-z0-9]+/.*$'), ('pages.results', ['action', 'fromuser', 'byname'])),
    (re.compile('results/[^/]+$'), ('pages.results', ['action', 'byname'])),
    (re.compile('search/[^/]+$'), ('pages.search', ['action', 'byname'])),
    (re.compile('view/[^/]+$'), ('pages.view', ['action', 'byname'])),
    (re.compile('newbug/[^/]+$'), ('pages.newbug', ['action', 'bugtype'])),
    (re.compile('env.*'), ('pages.env', None)),
    (re.compile('(images|scripts|styles)/.*$'), ('pages.static', ['path'])),
]

# Let plugins register their pages
plugins.addPages(repages, pages)

for regex, pagedata in repages:
    if regex.match('/'.join(path)):
        page = pagedata
        break
else:
    if path[0] in pages:
        page = pages[path[0]]
    else:
        errorPage(404, "Page not found {}".format(path))
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
    args = '&'.join(map('='.join, zip(page[1], path)))
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
