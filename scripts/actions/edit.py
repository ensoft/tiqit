#! /usr/bin/python3

import time
from backend import *
from tiqit import *
from frontend import *

args = Arguments()

#
# First thing we want to do is make sure we're not scribbling over any
# changes made by someone else.
#
bugid = extractBugIds(args['Identifier'])[0]

data = loadBugs([bugid])[0]

lastupdate = time.strptime(args['Sys-Last-Updated'], "%m/%d/%Y %H:%M:%S")
realupdate = time.strptime(data["Sys-Last-Updated"], "%m/%d/%Y %H:%M:%S")

if realupdate > lastupdate:
    raise TiqitWarning("The bug has been edited since you loaded the page. Saving would have overwritten any changes made in between time. Go back to the bug and reload the page to see what fields have been modified (pressing 'Back' and then 'F5' should result in no loss of your own changes - the other modifications will simply appear in blue, alongside your own changes. You may then confirm or revert the changes, as desired).")

#
# What type of bug is this
#
bugView = getBugViewFromBugData(data)

#
# We only want to check fields that are actually present on the page. Parse
# the format strings to work out what they are.
#

changes = {}

cls = TiqitClass.forName(args['Project'])

fieldsInUpdate = extractFieldsFromFormat(cls, bugView.getViewBugSections(data))
fieldsInUpdate = [x.name for x in fieldsInUpdate if x.editable]

if 'S1S2-without-workaround' in args:
    fieldsInUpdate.append('S1S2-without-workaround')

# Make checkboxes into Y's
for field in [x for x in fieldsInUpdate if allFields[x].type == 'Boolean']:
    if field in args and args[field] and args[field] != 'false':
        args[field] = 'Y'
    else:
        args[field] = 'N'

# Now check fields for differences
for field in [x for x in fieldsInUpdate if allFields[x].editable]:
    fieldObj = allFields[field]
    old = data[fieldObj.name]
    new = ''
    if field in args:
        new = args[field]

    if old != new:
        changes[fieldObj.name] = new

# Convert any changed fields to the backend format
for field in changes:
    fieldObj = allFields[field]
    changes[field] = fieldObj.filterEdit(args, args[field])

# Now fix multi value fields
for field in list(changes.keys()):
    if field in [x for x in fieldsInUpdate if allFields[x].mvf]:
        changes[field] =  ",".join(changes[field].split(' '))

# Recheck at this point that all the fields being sent are valid given
# the current values. This handles cases where a field is sent from
# the browser but the backend will not let it be updated. This is true
# for e.g. greyed out fields like forwarded to
newData = OverriddenData(data, changes)
for field in list(changes.keys()):
    if not isValidField(allFields[field], newData):
        del changes[field]

# Boolean values can change from '' to 'N' if the field was not previously set
# in the bug data and the user has not ticked the text box.
#
# Boolean values can change from 'N' to '' if the field was previously set to
# 'N' in the bug data, and the user still hasn't checked the box and is using a
# browser that reports unchecked checkboxes as ''. 
#
# In both of these cases ignore the change. Mandatory fields will be fixed up
# in the next step.
for fieldname in [x for x in fieldsInUpdate if allFields[x].type == 'Boolean']:
    if fieldname in changes and \
        (changes[fieldname], data[fieldname]) in [('N', ''), ('', 'N')] and \
          fieldname != 'S1S2-without-workaround':
        # 'S1S2-without-workaround' is a special case: it was intentionally
        # changed earlier in this file. A better solution could be to have
        # a flag that can be set to signify that a change was on-purpose.
        del changes[fieldname]

# Boolean fields that are mandatory should be sent if a value hasn't already
# been set in the bug.
for fieldname in [x for x in fieldsInUpdate if allFields[x].type == 'Boolean']:
    if fieldname not in changes and data[fieldname] == '' and \
        allFields[fieldname].isMandatory(OverriddenData(data, changes)):
        changes[fieldname] = 'N'

if 'newRelates' in args:
    changes['Related-bugs'] = extractBugIds(args['newRelates'])
    if not changes['Related-bugs']:
        del changes['Related-bugs']

bugView.prepareUpdateBug(changes, fieldsInUpdate, data)

changes_save = dict([(allFields[field].savename, changes[field]) for field in list(changes.keys())])

updateBug(args['Identifier'], changes_save)
redirect('%s' % args['Identifier'])
