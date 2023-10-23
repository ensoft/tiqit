#! /usr/bin/python3

from tiqit import *
from tiqit.printing import *
import os, cgi, urllib.request, urllib.parse, urllib.error

newPrefs = loadPrefs(saveTimestamp=True)

args = Arguments()
dels = set()
sets = {}

# Map arguments into a set() of deletes, and a dict() of sets.
# A deleted item has the form "key<N>=<prefName>".
# A changed item has the form "key<N>=<prefName>&val<N>=<prefVal>"
for kArg in [x for x in args if x.startswith("key")]:
    vArg = kArg.replace("key", "val", 1)
    if vArg in args:
        sets[args[kArg]] = str(args[vArg])
    else:
        dels.add(args[kArg])
        
# Apply the deletes first to avoid conflict if there is a simultaneous delete
# and set.
for prefName in dels:
    setattr(newPrefs, prefName, None)

# Now apply the sets.
for prefName in sets:
    setattr(newPrefs, prefName, sets[prefName])
    
savePrefs(newPrefs)

printXMLPageHeader()
printXMLMessages()
printXMLSectionHeader("preferences")
 
for f in args:
    print("""<update><name><![CDATA[%s]]></name><value><![CDATA[%s]]></value></update>""" % (encodeCDATA(f), encodeCDATA(args[f])))

printXMLSectionFooter("preferences")
printXMLPageFooter()

