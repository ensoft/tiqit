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

#
# Create a nice form to create a new bug from.
#

import os
from tiqit import *
from backend import *
from frontend import *

fields = Arguments()

prefs = loadPrefs()

class EmptyBugData(DataCommon):
    def _getRawValue(self, key):
        return ''

if fields.has_key('bugid'):
    bugid = fields['bugid']
    bugdata = loadBugs([bugid])[0]
    bugView = getCloneBugViewFromBugData(bugdata, overrides=fields)
else:
    bugdata = EmptyBugData()
    bugView = getBugViewFromArgs(fields)


if fields.has_key('bugid'):
    pageTitle = "Clone Bug %s" % bugid
else:
    pageTitle = "Submit new %s" % bugView.displayname


if fields.has_key('Project'):
    project = fields['Project']
elif fields.has_key('bugid'):
    project = bugdata['Project']
else:
    project = prefs['miscDefaultProject']

bugdata = bugView.initNewBug(bugdata, project)

initScript = """
    function init() {
      checkChildren();
      checkFormValidity();
    }
"""

printPageHeader(PAGE_NEW, pageTitle, initScript, bugView=bugView)
printMessages()

cls = TiqitClass.forName(project)

inFields = extractFieldsFromFormat(cls, bugView.getNewBugSections(project))

args = getFormatArguments(bugdata, inFields=inFields)

print """
<h1>
  %s
</h1>
<form id='tiqitNewBug' action='submit.py' method='post' onsubmit='onSubmitPage(); if (!checkFormValidity()) return confirm("Missing info in form. Submit anyway?");'>""" % pageTitle

print "<p>Creating new "

writeOptions('bugtype', [(x.name, x.displayname) for x in allBugViews if x.submittable], bugView.name, onchange='changeBugType(this)')

print " in project: "

writeOptions('Project', sorted(allFields['Project'].values), project, onchange='changeProject(this)')

print " Note that changing either will cause the page to reload.</p>"

for title, detail, format in bugView.getNewBugSections(project):
    printSectionHeader(title, detail);

    print cls.getFormat(format) % args

    printSectionFooter()

print """<p><input type='submit' value='Submit Bug'></p>
</form>
"""

printPageFooter()
