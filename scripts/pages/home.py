#! /usr/bin/python

import os, urllib
from tiqit import *

printPageHeader(PAGE_HOME, hideSavedSearches=True)
printMessages()

cfg = Config().section('general')

print """
  <h1>%s</h1>
   <p><em>%s</em></p>
   <h3>BugBox</h3>
   <form method='post' action='bugbox' class='tiqitBugsyLogo'>
   <p>Enter some text, press go, get a list of all the bugs mentioned in the text.</p>
   <textarea name='bugid' cols='60' rows='10'></textarea>
   <p><input type='submit' value='Go'></p>
   </form>
""" % (cfg.get('sitetitle'), cfg.get('siteintro'))

savedSearches, needSave = getSavedSearches()

if savedSearches:
    print """
    <h3>Saved Searches</h3>
    <table>
    """

    for name, url in savedSearches:
        ename = urllib.quote(name, '')
        print """
        <tr>
         <td>%s:</td>
         <td>
          <a href='%s'>Run Query</a> |
          <a href='%s'>Modify Query</a> |
          <a href='%s'>Publishable Link</a></td>
        </tr>""" % (name, 'results/%s/%s' % (os.environ['REMOTE_USER'], ename),
                    'search/%s' % ename,
                    'results/%s/%s' % (os.environ['REMOTE_USER'], ename))

    print "</table>"
else:
    sampleSearches = plugins.getSampleSearches()
    if sampleSearches:
        rows = "\n".join("<tr><td>%s:</td><td><a href='%s'>Run Query</a></td></tr>" %
            (k, encodeHTML(v)) for k, v in sampleSearches.iteritems())

        print """
        <h3>Sample Queries</h3>
        <p><em>Here are a couple of sample queries to get you started.</em></p>
        <table>
        %s
        </table>
        """ % rows

printPageFooter()
