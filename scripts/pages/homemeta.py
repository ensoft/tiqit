#!/usr/bin/python3

from tiqit import *

printPageHeader(PAGE_HOMEMETA, hideSavedSearches=True, hideNamedBugs=True)

printMessages()

cfg = Config().section('general')

print("""
  <h1>%s</h1>
  <p><em>This is the metadata store for the <a href='%s'>%s</a>
  bug tracking system</em></p>
  <p><strong>It is still somewhat under construction.</strong> You can view and set <a href='defaultvals'>default value relationships</a> between fields, and in future will be able to access meta data about the known fields.</p>
""" % (cfg['metatitle'], cfg['siteurl'], cfg['sitename']))

printPageFooter()
