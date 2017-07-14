#! /usr/bin/python

import cgi, os
from tiqit import *
from tiqit.printing import *

prefs = loadPrefs(saveTimestamp=True)

fields = cgi.FieldStorage()

query = os.environ['QUERY_STRING']

if query.find('bugid=') == -1:
    saveType = ('search', 'search', 'results.py')
else:
    saveType = ('namedBug', 'bug', 'view.py')

if hasattr(prefs, saveType[0] + fields['name'].value) and \
       not fields.has_key('overwrite'):
    # Item exists and "overwrite" has not been specified, so just set the
    # response vars.
    existsNum = 1
    savedNum = 0
else:
    # Set the response vars.
    if hasattr(prefs, saveType[0] + fields['name'].value):
        existsNum = 1
    else:
        existsNum = 0
    savedNum = 1

    # Do the save.
    saveQuery = query.replace('&overwrite=true', '')
    saveQuery = saveQuery[:saveQuery.rfind('&')]

    setattr(prefs, saveType[0] + fields['name'].value,
            '%s?%s' % (saveType[2], saveQuery))
    savePrefs(prefs)

# Send the response XML
printXMLPageHeader()
print """<saveSearchResponse exists="%d" saved="%d" />""" % (existsNum, savedNum)
printXMLPageFooter()

