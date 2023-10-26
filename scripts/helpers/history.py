#!/usr/bin/python3
#
# Output an XML description of a bug's history.

from tiqit import *
from tiqit.printing import *
from backend import *
import os, re, sys, cgi, utils

# Extract ID from the args.
args = Arguments()
if "buglist" not in args:
    raise TiqitError("No Bug ID specified")

# Load the bug and extract the history
bugids = extractBugIds(args['buglist'])
bugData = loadBugs(bugids)

# Produce the output
printXMLPageHeader()
for bugDatum in bugData:
    historyItems = bugDatum.getHistory()
    print(" <history bugid=\"%s\">" % utils.encodeHTML(bugDatum['Identifier']))
    for historyItem in historyItems:
        print("  <historyitem>")
        for key in historyItem:
            print("    <%s><![CDATA[%s]]></%s>" % (key, utils.encodeCDATA(str(historyItem[key])), key))
        print("  </historyitem>")
    print(" </history>")
printXMLPageFooter()

