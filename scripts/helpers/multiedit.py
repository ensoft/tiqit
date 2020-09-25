#
# We're saving a few limited fields for a single bug.
#

import time, sys
from tiqit import *
from tiqit.printing import *
from backend import *

args = Arguments()

#
# First check for changes the user is not aware of.
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
    # Determine the changes the user has requested. Convert each change to
    # its backend format.
    #

    fields = args['fields'].split(',')
    changes = {}

    is_get_changes_success = True
    for f in fields:
        if not is_get_changes_success:
            break

        try:
            changes[allFields[f].savename] = allFields[f].filterEdit(args, args[f])
        except Exception as err:
            # There's an issue with the conversion to the backend format.
            is_get_changes_success = False
            queueMessage(MSG_ERROR,
                         "Failed to save changes to {}. Unable to convert {} value '{}': {}".format(
                             args['Identifier'], f, args[f], str(err)))
            printXMLPageHeader(extraheaders=['Status: 500'])
            printXMLMessages()
            printXMLPageFooter()

    if is_get_changes_success:
        #
        # Attempt to save the changes
        #
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
