#! /usr/bin/python

import cgi, traceback, commands, tempfile, os, stat, urllib, sys
from tiqit import *
from backend import *

args = Arguments()

if not args.has_key('deleteTitle'):
    if len(args['noteContent']) > 16 * 1024 and args.has_key('isUpdate'):
        raise TiqitError("Note too large. Must be less than 16kb. Use Attachements instead. Your note is %d bytes long" % len(args['noteContent']))

noteType = args['noteType']
noteTitle = args['noteTitle'].strip()
bugid = args['bugid']
newTitle = args['newNoteTitle'].strip()
deleteTitle = args['deleteTitle'].strip()

# If this is a delete, then delete it
if args.has_key('deleteTitle'):
    deleteNote(bugid, args['deleteTitle'].strip())
else:

    # Try to rename the note if required first
    if newTitle and newTitle != noteTitle:
        renameNote(bugid, noteType, noteTitle, newTitle)

        # Save the new name for the next step
        noteTitle = newTitle

    # Replace unicode line-separator characters with standard newlines
    # These are inserted by the JS to avoid newlines being urlencoded and lost
    # during redirects through OIDC.
    noteContent = args['noteContent']
    noteContent = noteContent.replace(u'\u2028', '\n')

    # Now update/create the note
    addNote(bugid, noteType, noteTitle, noteContent, args.has_key('isUpdate'))

redirect('%s' % bugid)
