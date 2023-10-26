#!/usr/bin/python3
#
# Copyright (c) 2017 Ensoft Ltd, 2010 Martin Morrison
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

from tiqit import *
from tiqit.toolbars import *

__all__ = [
    'getDefaultPrefs',
    'viewingBug',
    'printToolbars',
    ]

def getDefaultPrefs():
    return {
        'listRecentBugs': [],
        'miscShowRecentBugs': 'false',
        }

def viewingBug(bugid):
    prefs = loadPrefs()
    if not prefs.listRecentBugs:
        prefs.listRecentBugs = [bugid]
    else:
        if bugid in prefs.listRecentBugs:
            prefs.listRecentBugs.remove(bugid)
        prefs.listRecentBugs.append(bugid)
        if len(prefs.listRecentBugs) > 8:
            prefs.listRecentBugs = prefs.listRecentBugs[-8:]
    prefs = savePrefs(prefs)

def printToolbars(page):
    prefs = loadPrefs()
    if prefs.miscShowRecentBugs != 'on' or page.site == SITE_META:
        return

    if prefs.listRecentBugs:
        bugs = ("<a class='recentBug' href='%s'>%s</a>" % (b, b) for b in prefs.listRecentBugs)

        return ''.join([printToolbarHeader("Recent Bugs"),
                        "Recently Visited: %s" % " | ".join(bugs),
                        printToolbarFooter()])
    else:
        return None
