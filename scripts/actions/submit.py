#! /usr/bin/python3

from tiqit import *
from backend import *
from frontend import *

#
# Creating a new bug
#
args = Arguments()

#
# What type of bug is this
#
bugView = getBugViewFromArgs(args)

#
# We go through every known field, and save it if it is specified
#

fields = {'Project': args['Project']}

fieldsInUpdate = extractFieldsFromFormat(TiqitClass.forName(args['Project']), bugView.getNewBugSections(args['Project']))
fieldsInUpdate = [x.name for x in fieldsInUpdate if x.editable]

# Make checkboxes into Y's
for field in [x for x in fieldsInUpdate if allFields[x].type == 'Boolean']:
    if field in args and args[field] != 'N':
        args[field] = 'Y'
    else:
        args[field] = 'N'

# Convert values if appropriate
for arg in args:
    if arg in allFields:
        args[arg] = allFields[arg].filterEdit(args, args[arg])

# Now look for fields
for field in fieldsInUpdate:
    if allFields[field].savename is not None and                              \
      (field in args or allFields[field].req):
        if allFields[field].mvf:
            fields[allFields[field].savename] = ','.join(args[field].split(' '))
        else:
            fields[allFields[field].savename] = args[field]

# Do any pre-processing the View or Plugins want
bugView.prepareNewBug(fields)
plugins.prepareNewBug(fields)

# Now create the bug
newid = createBug(fields)

# And do any post-processing
bugView.doNewBug(newid, args)
plugins.doNewBug(newid, args)

redirect('%s' % newid)
