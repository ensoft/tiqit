#!/usr/bin/python

from tiqit.defaults import *
from tiqit import *
from backend import allFields

args = Arguments()

field = allFields[args['tiqitDefaultField']]

if not field.defaultsWith:
    raise TiqitError("%s is not a field that supports defaults" % field.name)

withs = {}
for w in field.defaultsWith:
    withs[w] = args[w]

defs = {}
for d in args['defaultFields'].split(','):
    allFields[d] # Check it's actually a field
    defs[d] = args[d]

saveDefaults(field, withs, defs)

redirect('defaultvals?tiqitDefaultField=%s&%s' % (field.name, '&'.join(['%s=%s' % (w, encodeHTML(withs[w])) for w in withs])))
