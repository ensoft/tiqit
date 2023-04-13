#! /usr/bin/python3

import cgi, traceback, subprocess, tempfile, os, stat, urllib.request, urllib.parse, urllib.error, sys
from tiqit import *
from backend import *

args = Arguments()

if 'deleteTitle' not in args:
    if len(args['noteContent']) > 16 * 1024 and 'isUpdate' in args:
        raise TiqitError("Note too large. Must be less than 16kb. Use Attachements instead. Your note is %d bytes long" % len(args['noteContent']))

noteType = args['noteType']
noteTitle = args['noteTitle'].strip()
bugid = args['bugid']
newTitle = args['newNoteTitle'].strip()
deleteTitle = args['deleteTitle'].strip()

# If this is a delete, then delete it
if 'deleteTitle' in args:
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
    noteContent = noteContent.replace('\u2028', '\n')

    # Now update/create the note
    addNote(bugid, noteType, noteTitle, noteContent, 'isUpdate' in args)

redirect('%s' % bugid)
