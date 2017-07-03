#! /usr/bin/python

from backend import *
from tiqit import Arguments
from tiqit.printing import *
from tiqit.defaults import fetchDefaults, fetchReverseDefaults

args = Arguments()

field = allFields[args['field']]
defs = {}

# We should have been given all the values. Gather then up, then check the DB
def getDefaultsForField(field):
    vals = []
    other = []
    for f in field.defaultsWith:
        if not args.has_key(f):
            return

    more = fetchDefaults(field, args)

    for key in more:
        if key not in defs:
            defs[key] = more[key]
            other.append(key)

    for key in other:
        if allFields[key].defaultsWith:
            getDefaultsForField(allFields[key])

getDefaultsForField(field)

revs = fetchReverseDefaults(field, args[field.name])

# OK, now let's print out the defaults we have obtained
printXMLPageHeader()
printXMLMessages()
printXMLSectionHeader('defaults')
for key in defs:
    print "<field name='%s'><![CDATA[%s]]></field>" % (key.replace("'", "&apos;"), encodeCDATA(defs[key]))
printXMLSectionFooter('defaults')
printXMLSectionHeader('reversedefaults')
print revs
for key in revs:
    print "<defaultfrom name='%s'>" % key.replace("'", "&apos;")
    for entry in revs[key]:
        print "<entry>"
        for k, v in entry.items():
            print "<field name='%s'><![CDATA[%s]]></field>" % (k.replace("'", '&apos;'), encodeCDATA(v))
        print "</entry>"
    print "</defaultfrom>"
printXMLSectionFooter('reversedefaults')
printXMLPageFooter()
