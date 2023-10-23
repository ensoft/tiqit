#! /usr/bin/python3
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

import urllib.request, urllib.parse, urllib.error
from tiqit import *

args = Arguments()
prefs = loadPrefs(saveTimestamp=True)

# Cope with Firefox Keyword Bookmark with no bugid specified
if 'bugid' not in args or args['bugid'] in ('%s', ''):
    sendMessage(MSG_WARNING, "No bug ids specified.")
    redirect('home')

bugids = extractBugIds(args['bugid'])

if len(bugids) == 0:
    # Look for a Named Bug name in the bugbox.
    match = []
    for bug in prefs.ofType('namedBug'):
        if bug[8:].lower() == args['bugid'].lower():
            match.append(bug)
    if match:
        if len(match) > 1:
            if 'namedBug%s' % args['bugid'] in match:
                match = 'namedBug%s' % args['bugid']
            else:
                raise TiqitError("'%s' is an ambiguous bug name" % args['bugid'])
        else:
            match = match[0]

        sendMessage(MSG_INFO, "Redirected to named bug.")
        redirect('view/%s' % urllib.parse.quote(match[8:]))

    # Look for a named query
    for search in prefs.ofType('search'):
        if search[6:].lower() == args['bugid'].lower():
            match.append(search)
    if match:
        if len(match) > 1:
            if 'search%s' % args['bugid'] in match:
                match = 'search%s' % args['bugid']
            else:
                raise TiqitError("'%s' is an ambiguous saved search name" % args['bugid'])
        else:
            match = match[0]

        sendMessage(MSG_INFO, "Redirected to saved search.")
        redirect('results/%s' % urllib.parse.quote(match[6:]))

    # Otherwise, no valid bugids found -> error
    raise TiqitError("Invalid bug ids: <tt>%s</tt>" % args['bugid'])

elif len(bugids) == 1:
    # Single bug id -> View page.
    # Only print a message if it was from main BugBox.
    if 'goto' not in args:
        sendMessage(MSG_INFO, "Redirected from the BugBox.")
    redirect("%s" % bugids[0])

else:
    # Generate a query
    bugbox = "&".join(["=".join((x, getattr(prefs, x))) for x in prefs.ofType('selection')])
    bugbox += '&' + "&".join(["=".join((x, prefs[x] and 'true' or '')) for x in prefs.ofType('edit')])
    bugbox += '&' + "&".join(["=".join((x, getattr(prefs, x))) for x in prefs.ofType('sort')])
    bugbox += "&buglist=%s" % ",".join(bugids)

    sendMessage(MSG_INFO, "%d bug ids extracted from the BugBox" % len(bugids))
    redirect("results?%s" % bugbox)
