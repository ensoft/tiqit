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

from tiqit import *
from backend import allFields
from frontend import allBugViews

prefs = loadPrefs()
cfg = Config().section('general')

initScript = "function init() {\n"
initScript += "document.getElementById('selectionSelector').appendChild(createFieldsSelector('selection'));"

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
    initScript += "addFieldSelection('selection', 'edit');\n" 
    initScript += "setFieldSelection('selection', %d, '%s');\n" % (i, getattr(prefs, 'selection%d' % i))
    if prefs.has_key('edit%d' % i):
        initScript += "setFieldEditing('edit', %d, %s);\n" % (i, prefs['edit%d' % i] and 'true' or 'false')
    i += 1

i = 1
while hasattr(prefs, 'sort%d' % i):
    initScript += "Tiqit.search.addSortField('sort');\n"
    initScript += "Tiqit.search.setSortField('sort', %d, '%s', '%s');\n" % \
                  (i, getattr(prefs, 'sort%d' % i),
                   getattr(prefs, 'sortOrder%d' % i))

    i += 1

# Allow plugins to add to the init script
initScript += "\n".join(plugins.getPrefsInitScript(prefs))

# Sections on the prefs page
prefsSections = ('General', 'View', 'Submit', 'Searches', 'Search', 'NamedBug')
pluginSections = plugins.getPrefsSections(prefs)
prefsSections += tuple(title for title, anchor, desc, text in pluginSections)

for s in prefsSections:
    initScript += "showSection('%s', true);\n" % s

initScript += "}\n"

printPageHeader(PAGE_PREFS, "User Preferences", initScript)
printMessages()

print """
<h1>User Preferences</h1>
<p><em>Preferences fall into the following categories:</em></p>
<ul>
  <li><a href='prefs#anchorGeneral'>General</a> - properties affecting %s as a whole</li>
  <li><a href='prefs#anchorView'>View</a> - properties affecting the Bug View page</li>
  <li><a href='prefs#anchorSubmit'>Submit</a> - default field values when submitting new bugs</li>
  <li><a href='prefs#anchorSearches'>Searches</a> - properties affecting searches and the results page</li>
""" % cfg.get('sitename')
for title, anchor, desc, text in pluginSections:
    print "<li><a href='prefs#anchor{}'>{}</a> - {}</li>".format(
        anchor, title, desc)
print """
  <li><a href='prefs#anchorSearch'>Saved Searches</a> - rename and delete Saved Searches</li>
  <li><a href='prefs#anchorNamedBug'>Named Bugs</a> - rename and delete Named Bugs</li>
</ul>
<form method='post' action='saveprefs.py'>
"""

# General properties
printSectionHeader('General')

print """
<p><em>General options affecting all %s pages.</em></p>
<table>
<tr><td colspan='2'>On the toolbar, show: <select name='miscToolbar'><option value='both'%s>Text and Icons</option><option value='text'%s>Text only</option><option value='icons'%s>Icons only</option></select></td></tr>""" % \
  (cfg.get('sitename'),
   prefs.miscToolbar == 'both' and ' selected' or '',
   prefs.miscToolbar == 'text' and ' selected' or '',
   prefs.miscToolbar == 'icons' and ' selected' or '')

print """<tr><td colspan='2'>Default Project for new bugs: """
writeOptions('miscDefaultProject', sorted(allFields['Project'].values), prefs.miscDefaultProject)
print """</td></tr>"""

print """<tr><td colspan='2'>Default Project for searches: """
writeOptions('miscDefaultSearchProject', [("ALL", "All Projects")] +
        sorted(allFields['Project'].values), prefs.miscDefaultSearchProject)
print """</td></tr>"""

print """</td></tr>
<tr><td><input type='checkbox' name='miscHideSavedSearches'%s></td><td>Hide Saved Search bar always.</td></tr>
<tr><td><input type='checkbox' name='miscHideNamedBugs'%s></td><td>Hide Named Bug bar always.</td></tr>
<tr><td><input type='checkbox' name='miscShowRecentBugs'%s></td><td>Show my recently visited in the toolbar.</td></tr>
<tr><td><input type='checkbox' name='miscHideWatermark'%s></td><td>Hide the background watermark.</td></tr>
%s
</table>
<p><input type='submit' value='Save Prefs'></p>
""" % (prefs.miscHideSavedSearches != 'false' and ' checked' or '',
       prefs.miscHideNamedBugs != 'false' and ' checked' or '',
       prefs.miscShowRecentBugs != 'false' and ' checked' or '',
       prefs.miscHideWatermark != 'false' and ' checked' or '',
       '\n'.join(plugins.printGeneralPrefs(prefs)))

printSectionFooter()

# View page properties
printSectionHeader('View')

print """
<p><em>Configure section display order.</em></p>
<table id='viewTable' class='tiqitTable'>
<thead>
 <tr><th>Section Name</th><th>Show</th><th>Hide</th><th>Remove</th><th>Move</th></tr>
</thead>
<tbody>
"""

viewOrder = prefs.ofType('viewOrder')
viewOrder = [(prefs[x], x[9:]) for x in viewOrder]
viewOrder.sort()

for i, s in viewOrder:
    p = getattr(prefs, 'display%s' % s)
    
    print """  <tr>
    <td>%s</td>
    <td align='center'><input type='radio' name='display%s' value='show'%s></td>
    <td align='center'><input type='radio' name='display%s' value='hide'%s></td>
    <td align='center'><input type='radio' name='display%s' value='remove'%s></td>
    <td>
     <div align='center'>
      <img src="images/hamburger-blue.png" title="Move field" alt="[Move field]" class="hamburger-move">
    </div>
     <input type='hidden' name='viewOrder%s' value='%s' id='viewOrder%s'>
    </td>
  </tr>
    """ % (s, s, p == 'show' and ' checked' or '',
           s, p == 'hide' and ' checked' or '',
           s, p == 'remove' and ' checked' or '', s, i, s)

print """
</tbody>
</table>
<script>makeSortable()</script>
"""

print """
<p><em>Additional bug view options.</em></p>
<table>
<tr><td><input type='checkbox' name='miscAlwaysFullView'%s></td><td>Always show full view, no matter the type of bug.</td></tr>
<tr><td colspan='2'>Maximum size of attachments to load inline: <input type='text' size='25' maxlength='30' name='miscMaxAutoloadSize' value='%s'/></td></tr>
<tr><td><input type='checkbox' name='miscGetDupedToRelates'%s></td><td>Display Duped-to relations in 'Related Bugs' section (slows down page load).</td></tr>
%s
</table>
<p><input type='submit' value='Save Prefs'></p>
""" % (prefs.miscAlwaysFullView != 'false' and ' checked' or '',
       encodeHTML(prefs.miscMaxAutoloadSize),
       prefs.miscGetDupedToRelates != 'false' and ' checked' or '',
       '\n'.join(plugins.printViewPrefs(prefs)))

printSectionFooter()

# Submit options
printSectionHeader('Submit')

print """
<table>
<tr><td colspan='2'>Default type for new bugs: """
writeOptions('miscDefaultBugType', [(x.name, x.displayname) for x in allBugViews if x.submittable], prefs.miscDefaultBugType)
print """</td></tr>
</table>
"""
print """
<p><em>Default field values when submitting new bugs (overridden by bug-type-specific defaults below, if present).</em></p>
<table>
%s
</table>
""" % ('\n'.join(plugins.printSubmitPrefs(prefs)))


# New per-bug-view default values
for bugView in allBugViews:
    if bugView.submittable:
        print """
<p><em>Default field values when submitting '%s' bugs.</em></p>
<table>
%s
</table>
""" % (bugView.displayname,
       bugView.printDefaultValuesPrefsTable())


print """
<p><input type='submit' value='Save Prefs'></p>
"""

printSectionFooter()

# Search options
printSectionHeader('Searches')

print """
  <p><em>Select your default search fields, both for the search page, and BugBox lists.</em></p>
  <input type='hidden' name='selectionCount' value=%s id='selectionCount'>
  <div id='selectionSelector'>
  </div>
  <div style='clear: both'></div>
""" % getattr(prefs, 'selectionCount')

print """
  <p><em>Select default sort order for queries, both from the search page, and for BugBox lists.</em></p>
  <p>
    <input type='button' onclick='Tiqit.search.addSortField("sort")' value='Add Field'>
    <input type='button' onclick='Tiqit.search.removeSortField("sort")' value='Remove Field'>
  </p>
  <div id='sortSelector'>
  </span>
  </div>
"""

print """
<p><em>Miscellaneous options regarding searches.</em></p>
<table>"""

print prefs.printBool("miscGroupByPrimaryKey",
                      "Group By Primary Key by default on new searches."),
print prefs.printBool("miscOneBugResults",
                      "Display Results page for single bug (instead of redirecting to view page)."),
print prefs.printBool("miscHideFortunes",
                      "Hide Fortune Cookies while waiting for search results."),
print prefs.printBool("miscShowSearchName",
                      "Show Saved Search name as title of results page instead of result count."),
print prefs.printBool("miscNeverAutoRefreshResults",
                      "Suppress automatically refresh of search results every 30 minutes."),
print prefs.printBool("miscHidePerRowAutoUpdateClear",
                      "Don't allow marked changes to be cleared individually for each bug."),
print prefs.printBool("miscDisableDblclkEdit",
                      "Disable double-click-to-edit."),
print '\n'.join(plugins.printSearchPrefs(prefs))

print """</table>
<p><input type='submit' value='Save Prefs'></p>"""

printSectionFooter()

# Allow plugins to insert their own sections.
for sectionName, sectionAnchor, sectionDesc, sectionText in pluginSections:
    printSectionHeader(sectionAnchor, sectionName)
    print sectionText
    print """<p><input type='submit' value='Save Prefs'></p>"""
    printSectionFooter()

# saved searches
searches = prefs.ofType('search')

if searches:
    printSectionHeader('Search', 'Saved Searches')
    print """
    <p><em>Click on the name in the table to rename the Saved Search.</em></p>
    <table class='tiqitTable'>
    <tr><th>(Re)name</th><th>Delete?</th></tr>
    """

    for search in searches:
        url = getattr(prefs, search)

        search = search.replace("'", "&apos;")

        print """
    <tr>
     <td><input id='%s' type='hidden' name='%s' value='%s'><input class='hidden' type='text' value='%s' size='30' onchange='document.getElementById(%s).name = "search" + this.value;'></td>
     <td><input type='checkbox' onchange='document.getElementById(%s).disabled = this.checked;'></td>
    </tr>""" % (search, search, url, search[6:], encodeJS(search), encodeJS(search))

    print """
    </table>
    <p><input type='submit' value='Save Prefs'></p>
    """

    printSectionFooter()

# named bugs
bugs = prefs.ofType('namedBug')
if bugs:
    printSectionHeader('NamedBug', 'Named Bugs')
    
    print """
    <p><em>Click on the name in the table to rename the Named Bug.</em></p>
    <table class='tiqitTable'>
    <tr><th>Identifier</th><th>(Re)name</th><th>Delete?</th></tr>
    """

    for search in bugs:
        url = getattr(prefs, search)

        search = search.replace("'", "&apos;")

        print """
    <tr>
     <td><a href='%s'>%s</td>
     <td><input id='%s' type='hidden' name='%s' value='%s'><input class='hidden' type='text' value='%s' size='30' onchange='document.getElementById(%s).name = "namedBug" + this.value;'></td>
     <td><input type='checkbox' onchange='document.getElementById(%s).disabled = this.checked;'></td>
    </tr>""" % (url, url[14:], search, search, url, search[8:], encodeJS(search), encodeJS(search))

    print """
    </table>
    <p><input type='submit' value='Save Prefs'></p>
    """

    printSectionFooter()

print "</form>"

printPageFooter()
