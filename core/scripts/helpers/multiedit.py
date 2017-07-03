#
# We're saving a few limited fields for a single bug.
#

import time, sys
from tiqit import *
from tiqit.printing import *
from backend import *

args = Arguments()

#
# First check for scribbling
#
data = loadBugs([args['Identifier']])[0]

lastupdate = time.strptime(args['Sys-Last-Updated'], '%m/%d/%Y %H:%M:%S')
realupdate = time.strptime(data["Sys-Last-Updated"], '%m/%d/%Y %H:%M:%S')

if realupdate > lastupdate:
    queueMessage(MSG_WARNING, "%s has been modified by someone else. Revert your changes and refresh the bug list before attempting changes again." % args['Identifier'])
    printXMLPageHeader(extraheaders=['Status: 409'])
    printXMLMessages()
    printXMLPageFooter()

else:
    #
    # Now build up arguments
    #

    fields = args['fields'].split(',')
    changes = {}

    for f in fields:
        # The value should be really filterEdited. This logic is missing and
        # should be added to fix changing the inability to save Component
        # on the multiedit page.
        changes[allFields[f].savename] = args[f]

    try:
        updateBug(args['Identifier'], changes)

        data = loadBugs([args['Identifier']])[0]

        printXMLPageHeader()
        printXMLMessages()
        printXMLSectionHeader("buglist")
        print """
  <bug identifier='%s' lastupdate='%s'>""" % (args['Identifier'], data['Sys-Last-Updated'])

        for f in fields:
            print "<field name='%s'><![CDATA[%s]]></field>" % (encodeHTML(f), encodeCDATA(args[f]))

        print """  </bug>"""
        printXMLSectionFooter("buglist")
        printXMLPageFooter()

    except TiqitException, e:
        queueMessage(e.type, "Backend Error: %s" % e.output)
        printXMLPageHeader(extraheaders=['Status: 500'])
        printXMLMessages()
        printXMLPageFooter()
