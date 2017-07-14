#
# Copyright (c) 2017 Ensoft Ltd, 2011 Martin Morrison
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
from tiqit.defaults import *
from backend import allFields, getFormatArguments

args = Arguments()

def showFieldChoices():
    printPageHeader(PAGE_DEFVALS, "Default Field Values")
    printMessages()

    fields = [f for f in allFields.values() if f.defaultsWith]

    print """<h1>Default Field Values</h1>
<form action='updatedefvals' method='POST'>
  <div id='tiqitDefaultVals'>"""

    print "<h3><strong style='font-size: 150%; color: darkred;'>Step 1:</strong> Select Field</h3>"


    if fields:
        print "<p><em>Select field you want to view defaults for:</em> "
        writeOptions('tiqitDefaultField', [(x.name, x.name) for x in fields], '', onchange='Tiqit.defaults.selectField(event)', optional=True)
        print "</p>"
    else:
        print "<p><em>There are no fields that trigger default values in other fields.</em></p>"

    print "  </div>\n</form>"

    printPageFooter()

showFieldChoices()
