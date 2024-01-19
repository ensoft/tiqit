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

from backend import *
from tiqit import *

#
# Refine query, if there is one.
#
loadSavedSearch()

args = Arguments()

initSearch = ["Tiqit.search.rowsAdded = false;"]
initSearch.append("function init() {")

initSearch.append("""
showSection("Searcher", true);
showSection("Selector", true);
showSection("Sorter", true);
hideSection("Advanced");
Tiqit.defaults.initURLs(Tiqit.search.getParentFieldValueSearch);
""")

prefs = loadPrefs()

#
# The algorithm for regenerating a query is this:
# 1. Construct the format query. For each row:
#   - add a new row
#   - move the row all the way to level 0
#   - move the row up to the correct level (a full set of opening brackets above it now)
#   - move the opening brackets above it to their correct level.
# 2. Set the content of the query. For each row:
#   - set values of new row
#
# This two stage approach is required to ensure the values of query fields
# and operators are not modified by the restructuring of the query format, so
# they are set afterwards when all structure modifications are complete.
#
i = 1
level = 0
initSearch.append("if (!Tiqit.search.rowsAdded) {");
while 'field%d' % i in args:
    initSearch.append("Tiqit.search.addRow(document.getElementById('adder' + %d));" % (i - 1))
    # Move in to level 0
    while level > 0:
        initSearch.append("Tiqit.search.shiftLeft(document.getElementById('leftShifter' + %d));" % i)
        level -= 1

    # Move to the right level
    targetLevel = int(args['level%d' % i])
    while level < targetLevel:
        initSearch.append("Tiqit.search.shiftRight(document.getElementById('rightShifter' + %d));" % i)
        level += 1

    # Move brackets if needed (only from second row onwards)
    if i > 1:
        targetLevel = int(args['opLevel%d' % (i - 1)])
        bracketLevel = 1
        while bracketLevel <= targetLevel:
            initSearch.append("Tiqit.search.bracketRightShift(document.getElementById('openBracket%d.%d').childNodes[1]);" % (i, bracketLevel))
            bracketLevel += 1
    i += 1

i = 1
while 'field%d' % i in args:
    initSearch.append("Tiqit.search.setRowValues(%d, '%s', '%s', '%s', '%s');" \
          % (i, args['field%d' % i], args['rel%d' % i], args['val%d' % i],
             args['operation%d' % i]))
    i += 1

if i == 1:
    if 'modify' not in args:
        initSearch.append("Tiqit.search.addRow();")
    else:
        initSearch.append("Tiqit.search.showDummyRow(true);")

# Now set up the display fields
initSearch.append("document.getElementById('selectionSelector').appendChild(createFieldsSelector('selection'));")
i = 1
while 'selection%d' % i in args:
    initSearch.append("addFieldSelection('selection', 'edit');")
    initSearch.append("setFieldSelection('selection', %d, '%s');" % (i, args['selection%d' % i]))
    initSearch.append("setFieldEditing('edit', %d, %s);" % (i, 'edit%d' % i in args and 'true' or 'false'))

    i += 1

if i == 1:
    # If the selectionCount attribute is 6, but there are more than 6 selection
    # attributes then this must be an old profile, so force the selectionCount to 
    # match the number of selection attributes.
    selectionCount = int(getattr(prefs, 'selectionCount'))
    selectionFieldsCount = selectionCount
    while hasattr(prefs, 'selection%d' % (selectionFieldsCount + 1)):
        selectionFieldsCount += 1
    if selectionCount == 6 and selectionFieldsCount > 6:
        selectionCount = selectionFieldsCount

    i = 1
    while i <= selectionCount and hasattr(prefs, 'selection%d' % i):
        initSearch.append("addFieldSelection('selection', 'edit');")
        initSearch.append("setFieldSelection('selection', %d, '%s');" % (i, getattr(prefs, 'selection%d' % i)))
        if 'edit%d' % i in prefs:
            initSearch.append("setFieldEditing('edit', %d, %s);" % (i, prefs['edit%d' % i] and 'true' or 'false'))
        i += 1

# Now set up sort fields
i = 1
while 'sort%d' % i in args:
    initSearch.append("Tiqit.search.addSortField('sort');")
    initSearch.append("Tiqit.search.setSortField('sort', %d, '%s', '%s');" \
                      % (i, args['sort%d' % i], args['sortOrder%d' % i]))

    i += 1

if i == 1:
    while hasattr(prefs, 'sort%d' % i):
        initSearch.append("Tiqit.search.addSortField('sort');")
        initSearch.append("Tiqit.search.setSortField('sort', %d, '%s', '%s');" % \
                           (i, getattr(prefs, 'sort%d' % i),
                            getattr(prefs, 'sortOrder%d' % i)))
        i += 1

initSearch.append("Tiqit.search.rowsAdded = true;");
initSearch.append("}");

#
# If this is a refined search, let the user know
#
if args['buglist']:
    queueMessage(MSG_INFO, "Search will be performed within your existing results");
    initSearch.append("showSection('Advanced', true);")

#
# Print the page
#

proj = prefs.miscDefaultSearchProject
if 'Project' in args:
    proj = args['Project']

initSearch.append("}")
printPageHeader(PAGE_SEARCH, "Bug Search", "\n".join(initSearch))
printMessages()

print("""
  <form action='results' method='get'>
  <h1>Bug Search</h1>
    <p>Search within  """)

writeOptions('Project', [("ALL", "All Projects")] + sorted(allFields['Project'].values), proj, 'handleProjChange();')

print(""" and return results as <select name='format'>
<option value='normal'>HTML (default)</option>
<option value='csv'>CSV (spreadsheet)</option>
<option value='rss'>RSS feed</option>
<option value='xml'>XML document</option>
</select>.</p>""")

printSectionHeader("Searcher", "Search Criteria");

print("""<p>
 <img src='images/help.gif' alt='Help:' title='How does this work?'>
 <em>Build up a query using all the whizz-bang buttons below. The [+] and [-]
 buttons add/remove rows from the query. The [<] and [>] buttons out/indent
 the current row, creating bracketing as required. AND binds more tightly than
 OR (so <tt>x AND y OR z</tt> is <tt>(x AND y) OR z</tt>).</em>
</p>
<p>
 <div id='tiqitSearcherDummyRow' style='display: none'>
  <img src='images/warning.gif' alt='Warning' title='No query'>
  <em>There are currently no query rows. Click the [+] button to add a row, or
  restrict the search using the Advanced Options section below.</em>
  <input id="dummyAdder" type="button" onclick='Tiqit.search.addRow();' value="+" />
 </div>
</p>
<div id='tiqitSearcher'></div>
<p><input type='submit' value='Search'></p>""")

printSectionFooter()

# Select fields

printSectionHeader("Selector", "Select Fields")

print("""<p>
 <img src='images/help.gif' alt='Help:' title='How does this work?'>
 <em>Select which columns are shown using the Action buttons below. Tick the
 Editable box to make cells in the column editable.</em>
</p>
  <div id='selectionSelector'>
  </div>
  <div style='clear: both'></div>
  <p><input type='submit' value='Search'></p>
""")

printSectionFooter()

# Select sort order

printSectionHeader("Sorter", "Sort By")

if args['groupby'] or ('groupby' not in args and prefs.miscGroupByPrimaryKey != 'false'):
    groupby = ' checked'
else:
    groupby = ''

print("""
  <p>
    <input type='button' onclick='Tiqit.search.addSortField("sort")' value='Add Field'>
    <input type='button' onclick='Tiqit.search.removeSortField("sort")' value='Remove Field'>
  </p>
  <div id='sortSelector'>
  </div>
  <input id='tiqitGroupBy' type='checkbox' onchange='checkGroupBy(event)' name='groupby'%s> Group by primary key?
  <p><input type='submit' value='Search'></p>
""" % groupby)

printSectionFooter()

#
# Advanced options. Should start off hidden.
#

printSectionHeader("Advanced", "Advanced Options")

print("""
<p>
 <img src='images/help.gif' alt='Help:' title='How does this work?'>
 <em>Restrictions in this section limit the bugs in which the above query is
 performed.</em>
</p>
<p>Restrict search by
""")

writeOptions('UserType',
             (('', 'None'),
              ('Engineer', 'Assigned to'),
              ('Submitter', 'Submitted by')),
             'UserType' in args and args['UserType'] or '')

print("<input type='text' name='UserName' value='%s'></p>" % ('UserName' in args and args['UserName'] or ''))

print("""
<p>To Status(es)
""")

for st, disp in zip(allFields['Status'].values, allFields['Status'].descs):
    print("<label><input type='checkbox' name='Status' value='%s'%s> %s</label>" % (st, st in args.asList('Status') and ' checked' or '', st))

print("</p>")

print("<p>Within bugs")

if 'buglist' in args:
    print("<input type='text' size='100' name='buglist' value='%s'>" % ",".join(extractBugIds(args['buglist'])))
else:
    print("<input type='text' size='100' name='buglist'></p>")

# Let plugins add their own advanced options
for opt in plugins.printSearchOptions(args):
    print(opt)

print("  <p><input type='submit' value='Search'></p>")

printSectionFooter()

print("""
  </form>""")

printPageFooter()
