#! /usr/bin/python
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

import os, pickle, time
from tiqit import *

args = Arguments()
prefs = loadPrefs()
cfg = Config().section('general')

if os.environ['REMOTE_USER'] in getAdministrators() and args.has_key('news'):
    try:
        fd = open(NEWS_PATH + 'latest', 'rb')
        oldnews = pickle.load(fd)
        fd.close()
    except:
        oldnews = []
    oldnews.append((time.time(), args['news']))
    fd = open(NEWS_PATH + 'latest', 'wb')
    pickle.dump(oldnews, fd)
    fd.close()

printPageHeader(PAGE_NEWS, "News")

# Update the news time stamp before printing messages, but save the value so we
# can work out what news to mark as "new" on this page.
news_time_stamp = prefs["newsTimeStamp"]
prefs["newsTimeStamp"] = time.time()
savePrefs(prefs)

printMessages()

print "<h1>%s News</h1>" % cfg.get('sitename')

if os.environ['REMOTE_USER'] in getAdministrators():
    printSectionHeader("NewNews", "New News")

    print """
    <form action='news.py' method='post'>
      <table border='0' width='50%'>
        <tr><td><textarea cols='60' rows='5' name='news'></textarea></td></tr>
        <tr><td><input type='submit' value='Submit News'></td></tr>
      </table>
    </form>
    """

    printSectionFooter()

try:
    fd = open(NEWS_PATH + 'latest', 'rb')
    news = pickle.load(fd)
    fd.close()
except:
    news = []

news.reverse()

print "<dl>"

old_header_printed = False
for when, what in news:
    if not old_header_printed and when < news_time_stamp:
        print "</dl>"
        printSectionHeader("OldNews", "Old News")
        print "<dl>"
        old_header_printed = True
    print "<dt>%s</dt><dd>%s</dd>" % (time.strftime("%H:%M %d/%m/%Y", time.localtime(when)), what)

print "</dl>"

printSectionFooter()

printPageFooter()
