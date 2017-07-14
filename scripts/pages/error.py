#! /usr/bin/python

from tiqit import *
from utils import *

args = Arguments()

printPageHeader(PAGE_VIEW, "Error")
printMessages()

errType = int(args['type'])

errTitles = { MSG_ERROR:   'An Error Occured',
              MSG_WARNING: 'Invalid Input',
              MSG_INFO:    'Informational Page' }

title = errTitles[errType]
icon = "<img alt='%s' src='%s'>" % msgIcons[errType]

print """
<h1>%s</h1>
<p>%s %s</p>
""" % (title, icon, encodeHTML(args['msg']))

if args.has_key('output'):
    print "<h3>Command Output</h3>"
    print "<pre>%s</pre>" % encodeHTML(args['output'])

if args.has_key('cmd'):
    print "<h3>Command Line</h3>"
    print "<p>The command that was run was:</p>"
    print "<pre>%s</pre>" % encodeHTML(args['cmd'])


print """
<p>Go <a href='javascript:history.go(-1);'>back</a> and try again.</p>
"""

printPageFooter()
