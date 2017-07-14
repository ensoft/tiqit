#! /usr/bin/python

from tiqit import *
import os, cgi, urllib, copy

oldPrefs = loadPrefs(saveTimestamp=True)
newPrefs = Prefs()

fields = cgi.FieldStorage(keep_blank_values=True)

defsPerBugView = copy.deepcopy(Prefs.defaults['miscDefaultsPerBugView'])

for f in fields.keys():
    # If this is a per-bug-view pref, extract the bug view and pref name
    if f.startswith('miscDefaultsPerBugView'):
        (junk, bugView, prefName) = f.split('.')

        defsPerBugView[bugView][prefName] = fields[f].value

        val = defsPerBugView
        f = 'miscDefaultsPerBugView'
    else:
        val = fields[f].value

    if not Prefs.defaults.has_key(f) or Prefs.defaults[f] != val:
        setattr(newPrefs, f, val)

# Some classes of pref are preserved though
for f in oldPrefs.ofType('list'):
    setattr(newPrefs, f, oldPrefs[f])

savePrefs(newPrefs)

sendMessage(MSG_INFO, "Preferences saved.")
redirect('prefs')
