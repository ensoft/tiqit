#!/usr/bin/python

from tiqit import *
from backend import *

args = Arguments()

bugid = args['bugid']

if args.has_key('deleteTitle'):
    deleteAttachment(bugid, args['deleteTitle'])
else:
    renameAttachment(bugid, args['renameTitle'], args['newTitle'])

redirect('%s' % bugid)
