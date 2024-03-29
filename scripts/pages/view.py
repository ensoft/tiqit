#! /usr/bin/python3

#
# Create a nice form to view the content of a bug.
#

import os, cgi, subprocess, sys, urllib.request, urllib.parse, urllib.error, time
from backend import *
from tiqit import *
from tableFilter import *
from frontend import *
import backend

prefs = loadPrefs()

#
# Some functions
#
#
# Get the bugid requested
#
loadNamedBug()

fields = Arguments()

if 'bugid' not in fields:
    raise TiqitError("You must specify a Bug ID")

bugid = extractBugIds(fields['bugid'])

if not bugid:
    raise TiqitWarning("No bug ID was requested.")
else:
    bugid = bugid[0]
    fields['bugid'] = bugid

# Let plugins know we're viewing this bug
plugins.viewingBug(bugid)

#
# Better look up this bug then. This bit is the slow bit.
#
theDom = loadBugs([bugid])[0]
project = theDom['Project']
cls = TiqitClass.forName(project)

#
# What type of bug is this
#
bugView = getBugViewFromBugData(theDom)

#
# Now extract all the field values from the bug data
#
inFields = extractFieldsFromFormat(cls, bugView.getViewBugSections(theDom))
inFields += [allFields[x] for x in ['Related-bugs']]

args = getFormatArguments(theDom, inFields=inFields)
args['Severity'] = args['Severity'].replace('checkFormValidity(event)', 'checkS1S2Downgrade(); checkFormValidity(event)')
args['Identifier'] = bugid

#
# Extra Note/Attachment information
#

#
# A couple of classes to deal with the differences between Notes and Files.
#

class Note(object):
    def __init__(self, info):
        self.info = info

    def printLine(self):
        return """
        <tr>
          <td onclick='showEnclosure(this.parentNode);'>
            <img src='images/plus.gif' alt='[+]' title='Show Enclosure'> %(Title)s
         </td>
         <td>%(Type)s</td>
         <td><a onclick='showUserDropDown(event);'>%(Creator)s</a></td>
         <td><a onclick='showUserDropDown(event);'>%(Updater)s</a></td>
         <td>%(Date)s</td><td>%(Size)s</td>
         <td>
           <input type='button' onclick='editEnclosure(this);' value='Edit'><input style='display: none;' type='submit' value='Save'><input style='display: none;' type='button' onclick='cancelEnclosureEdit(this.previousSibling.previousSibling);' value='Cancel'><input type='button' onclick='deleteEnclosure(this);' value='Delete'>
         </td>
        </tr>
        <tr class='note' style='display: none;'>
         <td colspan='7'>
            <pre>%(Note)s</pre>
            <textarea style='display: none;' class='edit' rows='18'>%(Note)s</textarea>
            <textarea style='display: none;' class='send'></textarea>
         </td>
        </tr>
        """ % self.info

class File(object):
    def __init__(self, info):
        self.info = info
        self.info['Url'] = encodeHTML(backend.attachmentUrl(info))
        self.info['UrlDownload'] = encodeHTML(backend.attachmentDownloadUrl(info))
    def printLine(self):
        if self.info['Type'][1:7] != 'binary' and self.info['Size'] and int(loadPrefs()['miscMaxAutoloadSize']) >= int(self.info['Size']):
            self.info['Frame'] = "<iframe fileloc='%(Url)s'></iframe>" % self.info
            self.info['FrameLink'] = self.info["Url"]
        else:
            self.info['Frame'] = "<a href='%(UrlDownload)s'>Download attachment</a>" % self.info
            self.info['FrameLink'] = self.info["UrlDownload"]
        return """
        <tr>
         <td onclick='showEnclosure(this.parentNode);'>
          <img src='images/plus.gif' alt='[+]' title='Show Enclosure'>
          %(Title)s
         </td>
         <td>%(Type)s</td>
         <td><a onclick='showUserDropDown(event);'>%(Creator)s</a></td>
         <td><a onclick='showUserDropDown(event);'>%(Updater)s</a></td>
         <td>%(Date)s</td><td>%(Size)s</td>
         <td>
          <input type='button' onclick='renameAttachment(this);' value='Rename'><input style='display: none;' type='button' onclick='saveAttachmentRename(this);' value='Save'><input style='display: none;' type='button' onclick='cancelAttachmentRename(this);' value='Cancel'><input type='button' onclick='deleteAttachment(this);' value='Delete'><a href='%(FrameLink)s'>Link</a>
         </td>
        </tr>
        <tr class='file' style='display: none;'>
         <td colspan='7'>
          %(Frame)s
         </td>
        </tr>
        """ % self.info

#
# Now load the Notes
#

encFilters = Filter('encTable',
                    ('Type', 'Creator', 'Updater'),
                    'encTableFilter')

encs = []

encs.extend([Note(n) for n in theDom.getEnclosures()])
encs.extend([File(f) for f in theDom.getAttachments()])

for enc in encs:
    encFilters.add(enc.info)

#
# Extract the Audit Trail (a.k.a. History Items)
#

auditargs = theDom.getHistory()
hisFilters = Filter('history', ('User', 'Operation', 'Field'))

for historyArgs in auditargs:
    hisFilters.add(historyArgs)

#
# Finally ready to start printing the page
#

def showPage():
    initScript = """
    function init() {
    """

    # Sections on the view page
    viewSections = [('General', displayGeneral),
                    ('Extra', displayExtra),
                    ('Notes', displayNotes),
                    ('Graphs', displayGraphs),
                    ('History', displayHistory),
                    ('Relates', displayRelates)]

    viewSections.extend(plugins.getViewSections())

    # Show/hide sections as requested by prefs
    for s, f in viewSections:
        if prefs['display%s' % s] in ('show', 'hide'):
            initScript += "%sSection('%s', true);\n" % (prefs['display%s' % s], s)


    if prefs['displayHistory'] in ('show', 'hide'):
        initScript += 'tiqitFilterInit("history");\n'
    initScript += """

      checkChildren();
      checkFormValidity();
      setTimeout(loadAttachments, 500);
      Tiqit.defaults.initURLs(getFieldValueView);
    }
    """

    initScript += '\n'.join(plugins.printJSInitScript(PAGE_VIEW))

    printPageHeader(PAGE_VIEW, "%s - %s" % (bugid, args['HeadlineRaw']),
                    initScript, showNamedBugSaver=True, bugView=bugView, bugid=bugid)

    printMessages()

    # Other links section
    print(""" <div id='tiqitOtherLinks'>""")

    # View links first
    otherlinks = Config().section('otherlinks')
    viewlinks = ["<a href='%s'>%s</a>" % (encodeHTML(v % args), o) for o, v in otherlinks.items(raw=True)]

    if viewlinks:
        print("  <div>View in %s</div>" % ', '.join(viewlinks))

    # Now let any plugins do their thing
    print("""
%s
 </div>
<h1>
 %s %s
</h1>
""" % ('\n'.join(plugins.printOtherLinks(PAGE_VIEW, fields, prefs)),
       bugView.displayname, args['Identifier']))

    sections = [(prefs['viewOrder%s' % x[0]], x) for x in viewSections]
    sections.sort()

    for pos, (name, func) in sections:
        func(getattr(prefs, 'display%s' % name) == 'remove')

    printPageFooter()

view_sections = bugView.getViewBugSections(theDom)

def displayGeneral(hide=False):
    primarytitle, primarytitleDetail, primaryformat = view_sections[0]
    printSectionHeader(primarytitle, primarytitleDetail, hide);

    print("<form id='tiqitBugEdit' action='edit.py' method='post' onSubmit='return prepareForm();'>")
    print(cls.getFormat(primaryformat) % args)

    print("""
<div id='extraCopies'></div>
<p>
 <input type='submit' value='Save Changes'>
 <input type='button' value='Reset Form' onclick='resetForm();'>
 <input type='button' onclick='if (!amEditing || confirm("You&apos;ve made changes to this bug. Cloning it will throw them away. Are you sure you want to continue?")) document.location = "newbug.py?bugid=%(Identifier)s";' value='Clone Bug'>
</p>
</form>""" % args)

    printSectionFooter()

def displayExtra(hide=False):
    print("<form onsubmit='return false;' id='tiqitExtraFormData'>")
    for title, titleDetail, format in view_sections[1:]:
        printSectionHeader(title, titleDetail, hide)
        print(cls.getFormat(format) % args)
        print("""

<p><input type='button' value='Save Changes' onClick='if (prepareForm()) document.getElementById("tiqitBugEdit").submit();'></p>
""")

        printSectionFooter()
    print("</form>")
#
# Text Notes and File Attachments are printed in the same section.
#

def displayNotes(hide=False):
    printSectionHeader("Notes", "Enclosures/Attachments", hide)

    # Write out the filter line
    if len(encs) > 1:
        print("<p>")
        encFilters.write()
        print("""
        <input type='button' value='Show All' onclick='showAllEnclosures();'>
        <input type='button' value='Hide All' onclick='hideAllEnclosures();'>
        </p>""")

    # Now the main table
    if not encs:
        print("<p>No Enclosures or Attachments.</p>")
    else:
        print("""
    <form action='editnote.py' onsubmit='onSubmitEnclosure()' method='post'>
    <input type='hidden' name='bugid' value='%s'>
    <input type='hidden' name='isUpdate' value='true'>
    <div id='encTableContainer'>
    <table id='encTable' class='tiqitTable' style='width: 90%%'>
     <tr>
      <th>Title</th>
      <th>Type</th>
      <th>Creator</th>
      <th>Updater</th>
      <th>Updated-on</th>
      <th>Size</th>
      <th>Action</th>
     </tr>""" % bugid)

        for enc in encs:
            print(enc.printLine())

        print("</table></div></form>")

    # And the 'new' section, for adding enclosures
    # Note the textareas are split into "Edit", which is visible to the user
    # but it's value isn't sent directly to the server, and a hidden "Send",
    # which has its value sent to the server. When the form is submitted, the
    # value of the "Edit" textarea has the newlines replaced with unicode
    # characters and this new value is inserted into the "Send" textarea.
    # This works around a known auth issue with OIDC.
    # Having separate boxes avoids issues where the note fails submit, the user
    # navigates back to edit the note again but now sees it with the unicode
    # characters present instead of the newlines. Most browsers don't render
    # the unicode characters at all.
    print("""
<p id='newencbuttons'>
 <input type='button' value='New Note' onclick='showNewNote();'>
 <input type='button' value='Attach File' onclick='showNewFile();'>
</p>
<div id='newnote' class='note' style='display: none;'>
 <p>Add new Enclosure:</p>
 <form action='editnote.py' onsubmit='onSubmitEnclosure()' method='post'>
  <input type='hidden' name='bugid' value='%s'>
  <table>
   <tr>
    <td>Type: </td>
    <td><select id='newnotetype' name='noteType' onchange='newNoteTitle(this);'>%s</select></td>
    <td>Title: </td>
    <td><input name='noteTitle' id='newnotetitle' type='text' size='50' value='%s'></td>
   </tr>
   <tr>
    <td colspan='4'>
     <textarea class="edit" style='width: 100%%' rows='18'></textarea>
     <textarea class="send" name='noteContent' style='display: none'></textarea>
    </td>
   </tr>
  </table>
  <p>
  <input type='submit' value='Save'>
   <input type='button' onclick='hideNewNote();' value='Cancel'>
  </p>
 </form>
</div>
<div id='newfile' class='note' style='display: none;'>
 <p>Attach new File:</p>
 <form action='addfile.py' method='post' enctype='multipart/form-data'>
  <input type='hidden' name='bugid' value='%s'>
  <p>
   Title: <input id='fileTitle' name='fileTitle' type='text' size='50' value="" onchange='unsetDefault()'>
<!--
   Type: <select name='fileType'>
    <option value='Auto'>Auto</option>
    <option value='Text'>Text</option>
   </select>
-->
   <input type='file' id='theFile' name='theFile' size='30' onchange='updateFileName()'>
  </p>
  <p>
   <input type='submit' value='Save'>
   <input type='button' onclick='hideNewFile();' value='Cancel'>
  </p>
 </form>
</div>
""" % (bugid, "".join(["<option value='%s'>%s</option>" % (x, x) for x in noteTypes if x != "Unknown-type"]), noteTypes[0], bugid))

    printSectionFooter()

#
# Histogram section
#
def displayGraph(status, numstates, changes, value, printCurrent=True, endtime=None, showTags=False, overrideBackground=True):
    # Date range goes from Submitted-on until now by default
    starttime = time.mktime(time.strptime(args['Submitted-onRaw'],
                                          "%m/%d/%Y %H:%M:%S"))
    nowtime = time.mktime(time.localtime())
    if endtime is None:
        endtime = nowtime
    totaltime = endtime - starttime

    print("<p>{}:</p>".format(status))
    print("<div class='tiqitGraph' style='height: %dem'>" % (numstates + 1))
    print("<div class='header'>")
    # Print row headers
    for i in range(len(changes)):
        if showTags:
            print("<div class='row' style='top: %dem;'>%s -&gt; %s</div>" % \
                  (i, changes[i]['OldValue'], changes[i]['NewValue']))
        else:
            print("<div class='row' style='top: %dem;'><!--%s -&gt; %s --></div>" % \
                  (i, changes[i]['OldValue'], changes[i]['NewValue']))

    # Bonus row header for current value if required
    if printCurrent:
        i += 1
        if showTags:
            print("<div class='row' style='top: %dem;'>%s -&gt;</div>" % (i, value))
        else:
            print("<div class='row' style='top: %dem;'><!--%s -&gt;--></div>" % (i, value))

    print("</div>")
    print("<div class='graph' style='height: %dem'>" % numstates)
    sofar = 0
    width = 0
    currtime = starttime
    for i in range(len(changes)):
        width = (changes[i]['DateVal'] - currtime) / totaltime * 100
        if overrideBackground:
            print("<div title='Changed by %s' class='row %s' style='text-align: center; background-color: %s; top: %dem; left: %.2f%%; width: %.2f%%;'>%s</div>" % (changes[i]['User'], changes[i]['OldValue'], stringToColour(changes[i]['OldValue']), i, sofar, width, changes[i]['OldValue']))
        else:
            print("<div title='Changed by %s' class='row %s' style='top: %dem; left: %.2f%%; width: %.2f%%;'>%s</div>" % (changes[i]['User'], changes[i]['OldValue'], i, sofar, width, changes[i]['OldValue']))
        currtime = changes[i]['DateVal']
        sofar += width

    # if required, print current value line
    if printCurrent:
        i += 1
        width = (endtime - currtime) / totaltime * 100
        if overrideBackground:
            print("<div title='Currently %s' class='row %s' style='text-align: center; background-color: %s; top: %dem; left: %.2f%%; width: %.2f%%;'>%s</div>" % (value, value, stringToColour(value), i, sofar, width, value))
        else:
            print("<div title='Currently %s' class='row %s' style='top: %dem; left: %.2f%%; width: %.2f%%;'>%s</div>" % (value, value, i, sofar, width, value))

    # Print a scale for the graph
    section = (endtime - starttime) / 5
    for s in range(6):
        thistime = starttime + s * section
        print("<div class='ruleline' style='left: %d%%'></div>" % (s * 20))
        print("<div class='row scale' style='top: %dem; left: %d%%'>%s</div>" % (i + 1, s * 20, time.strftime("%d/%m/%Y", time.localtime(thistime))))

    print("</div>")
    print("</div>")

def displayGraphs(hide=False):
    printSectionHeader("Graphs", hide=hide)

    # Go through history, looking for 'Status' changes
    statusChanges = [x for x in auditargs if x['Field'] == 'Status']
    statusChanges.reverse()

    # Go through history, looking for 'Component' changes
    compChanges = [x for x in auditargs if x['Field'] == 'Component']
    compChanges.reverse()

    # Go through history, looking for 'Severity' changes
    sevChanges = [x for x in auditargs if x['Field'] == 'Severity-desc']
    sevChanges.reverse()

    starttime = time.mktime(time.strptime(args['Submitted-onRaw'],
                                          "%m/%d/%Y %H:%M:%S"))
    nowtime = time.mktime(time.localtime())
    endtime = nowtime
    # Unless current state is 'closed' in which case until last transition
    if statusChanges and \
       statusChanges[-1]['NewValue'] in ('R', 'V', 'C', 'D', 'J'):
        endtimes = list()
        if statusChanges:
            endtimes.append(statusChanges[-1]['DateVal'])
        if compChanges:
            endtimes.append(compChanges[-1]['DateVal'])
        if sevChanges:
            endtimes.append(sevChanges[-1]['DateVal'])
        endtimes.sort()

        # Get the latest endtime
        if endtimes:
            endtime = endtimes[-1]
        totaltime = endtime - starttime
        print("<p>Graphs cover %d days and are now closed.</p>" % \
              (totaltime / 60 / 60 / 24))
    else:
        totaltime = endtime - starttime
        print("<p>Graphs cover %d days and counting.</p>" % \
              (totaltime / 60 / 60 / 24))

    # Draw status graph
    if statusChanges:
        # Only print the last column if the endtime is not the time of the
        # last status change
        printCurrent = (endtime != statusChanges[-1]['DateVal'])
        displayGraph("Status", len(statusChanges) + int(printCurrent), statusChanges, args['StatusRaw'],
                     printCurrent=printCurrent, endtime=endtime, showTags=True, overrideBackground=False)
    else:
        print("<p><img src='images/warning-small.png' alt='/!\\'> No status history available.</p>")

    # Draw component graph
    if compChanges:
        displayGraph("Component", len(compChanges) + 1, compChanges, args['ComponentRaw'], endtime=endtime)
    else:
        print("<p><img src='images/warning-small.png' alt='/!\\'> No component history available.</p>")

    # Draw severity graph
    if sevChanges:
        displayGraph("Severity", len(sevChanges) + 1, sevChanges, args['SeverityRaw'], endtime=endtime)
    else:
        print("<p><img src='images/warning-small.png' alt='/!\\'> No severity history available.</p>")

    printSectionFooter()

#
# Print the History section
#

def displayHistory(hide=False):
    printSectionHeader("History", hide=hide)

    # Filters
    hisFilters.write()

    # The table itself
    print("""
<div id='historyTableContainer'>
<table id='history' class='tiqitTable' style='width: 90%;'>
 <thead>
  <tr>
   <th field='User'>User</th>
   <th field='Operation'>Operation</th>
   <th field='Field'>Field</th>
   <th field='Old Value'>Old Value</th>
   <th field='New Value'>New Value</th>
   <th field='Date'>Date</th>
  </tr>
 </thead>
 <tbody>""")

    for args in auditargs:
        print("""
    <tr>
     <td><a onclick='showUserDropDown(event);'>%(User)s</a></td>
     <td>%(Operation)s</td>
     <td>%(Field)s</td>
     <td>%(OldValue)s</td>
     <td>%(NewValue)s</td>
     <td>%(Date)s</td>
    </tr>""" % args)

    print("""
 </tbody>
</table>
</div>
""")

    printSectionFooter()

#
# Print Related Defects section
#
# NOTE: Changes in this function to support related bug changes are a
# quick fix only. They should not be merged into 2.2+ branches.
# MAM: continued breakage meant they had to be. Hopefully fixed in next
# backend release. Ha!
def displayRelates(hide=False):
    # Since this can be slow, only display if requested
    if hide:
        return
    else:
        sys.stdout.flush()

    relates = theDom.getRelates()

    # Now add the other known relationships
    dup = args['Duplicate-ofRaw']
    if dup:
        relates.append((dup, 'Duplicate of', False))

    if 'BadcodefixIdRaw' in args:
        bad = args['BadcodefixIdRaw']
        if bad:
            relates.append((bad, 'Bad Code Fix for', False))

    if 'Previous-commit-idRaw' in args:
        bad = args['Previous-commit-idRaw']
        if bad:
            relates.append((bad, 'Bad Code Fix for', False))

    # Now we have all the relates. Get their data, so we can print a nice table
    printSectionHeader('Relates', 'Related Bugs', hide=hide)

    if relates:
        doms = loadBugs([x[0] for x in relates])

        print("""
    <table id='tiqitRelatesTable' class='tiqitTable' style='width: 90%;'>
    <tr><th>Del?</th><th>Identifier</th><th>Relationship</th><th>St</th><th>Headline</th></tr>""")

        for bug in doms:
            identifier = bug['Identifier']
            (rel, editable) = [(x[1],x[2]) for x in relates if x[0] == identifier][0]
            print("<tr><td><input type='checkbox'%s></td><td><a href='%s'>%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>" % \
                  ('' if editable else ' disabled', identifier,
                   identifier, rel, bug['Status'],
                   encodeHTML(bug['Headline'])))

        print("</table>")
    else:
        print("<p>No related bugs.</p>")

    # Adding new related bugs disabled until backends support it.
    print("""<!--
    <p>
     <table>
      <tr>
       <td style='vertical-align: text-top;'>Add new related bugs:</td>
       <td><textarea id='tiqitNewRelates' rows='2' style='width: 150%%'></textarea></td>
      </tr>
     </table>
    </p>
    <p><input type='button' value='Save Changes' onClick='if (prepareForm()) document.getElementById("tiqitBugEdit").submit();'></p>
    -->
    """)

    printSectionFooter()

# This is where we actually go and do the work
showPage()
