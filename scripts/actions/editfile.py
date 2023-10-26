#!/usr/bin/python3

from tiqit import *
from backend import *

args = Arguments()

bugid = args['bugid']

if 'deleteTitle' in args:
    deleteAttachment(bugid, args['deleteTitle'])
else:
    renameAttachment(bugid, args['renameTitle'], args['newTitle'])

redirect('%s' % bugid)
