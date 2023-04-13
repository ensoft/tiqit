#! /usr/bin/python3

import re, time, os, urllib.request, urllib.parse, urllib.error, json
from backend import *
from tiqit import *
from tiqit import PageLink
from tiqit.printing import *
from tiqit.queries import *
from tableFilter import *
from fortune import *

prefs = loadPrefs()

# Load saved search before parsing the arguments (cos it's nasty like that)
searchName, searchUser = loadSavedSearch()

args = Arguments()

#
# Some plugins may be able to load a query here (and possibly recursively, even
# if we've already loaded one).
# Note: since plugins are called in an effectively random order, this isn't
# actually very robust if ever there are multiple plugins.
#
othernames = plugins.loadSearch(args)

if not searchName and othernames:
    searchname = othernames[0]

#
# Build the query string - do different things depending on whether we want
# pretty HTML output, or plain CSV output.
#

FORMAT_NORMAL = 1
FORMAT_CSV = 2
FORMAT_RSS = 3
FORMAT_XML = 4
FORMAT_JSON = 5

outputType = FORMAT_NORMAL
if "format" in args:
    if args["format"] == "csv":
        outputType = FORMAT_CSV
    elif args['format'] == 'rss':
        outputType = FORMAT_RSS
    elif args['format'] == 'xml':
        outputType = FORMAT_XML
    elif args['format'] == 'json':
        outputType = FORMAT_JSON

#
# We largely use the queries module to do all the parsing here
#

query = parseQuery(args)

if outputType != FORMAT_RSS:
    selection = parseSelection(args)
else:
    selection = [allFields['Identifier'], allFields['Headline'],
                 allFields['Submitter'], allFields['Submitted-on'],
                 allFields['Summary']]

sort = parseSort(args)

#
# Build up the list of fields we need for correct operation
# These are parent fields and bannedIf fields of all the selected fields
#
parents = set()
for field in selection:
    for parent in field._parentFields:
        parents.add(allFields[parent])

    for bannedIf in list(field._bannedIf.keys()):
        parents.add(allFields[bannedIf])

    for defWith in field.defaultsWith:
        parents.add(allFields[defWith])

# We actually request the selected ones, and their dependees
requested = selection + list(parents)

states, proj, buglist, usertype, username = parseAdvanced(args)

#
# Let's go!
#

#
# Print the headers first
#
if outputType == FORMAT_NORMAL:
    # HTML output
    initScript = """
    function init() {
      tiqitFilterInit("results");
      tiqitTableInit("results", true, true);
    }
    tiqitSearchName = "%s";
    tiqitSearchQuery = %s;
    """ % (searchName and encodeHTML(searchName) or "",
           encodeJS(os.environ['QUERY_STRING']))

    initScript += '\n'.join(plugins.printJSInitScript(PAGE_RESULTS))

    # Add links to modify the search
    pages['results'].links.append(PageLink('search?modify=1&%s' % encodeHTML(os.environ['QUERY_STRING']), 'images/find_again-small.png', 'Modify this query', 'Modify'))
    pages['results'].links.append(PageLink('javascript:refineQuery()', 'images/find_selection-small.png', 'Refine this query by searching within the current results', 'Refine'))

    printPageHeader(PAGE_RESULTS, searchName and searchName or "Searching...",
                    initScript,
                    ['<link rel="alternate" type="application/rss+xml" title="Search results - %s" href="%s&amp;format=rss">' % (Config().section('general').get('sitetitle'), os.environ['REQUEST_URI'].replace('format=normal', ''))], showSavedSearchSaver=True)

    if prefs.miscHideFortunes == 'false':
        startFortunes()

# Here's where we actually do the query - in the backend
matches = performQuery(query, requested, sort, states, proj, buglist, usertype,
        username, outputType == FORMAT_NORMAL)
prikeytype = sort[0].field

# Some regular expressions to convert the output
tagre = re.compile(r"<.*?>")                     # Remove tags for filters

#
# Right, tell the world about it.
#
if outputType == FORMAT_NORMAL:
    # Stop the fortune thread
    stopFortunes()
    
    numres = str(len(matches))

    if numres == "10000":
        # This means there were more than 10000, only 10000 returned.
        numres = "10000+"
    elif numres == '1' and prefs.miscOneBugResults == 'false' and False:
        # Only one result. May as well forward straight to it.
        sendMessage(MSG_INFO, "Redirected: single search result only")
        redirect("%s\n" % matches[0]['Identifier'])

    printMessages()

    # Add a place for menus to add themselves
    print("<div id='tiqitMenus'></div>")

    # Print some other links
    otherlinks = [('results.py?%s&amp;format=csv' % re.sub('&?format=\w+', '', encodeHTML(os.environ['QUERY_STRING'])),
                   '',
                   'Import into Excel',
                   'Download results as CSV and import into your spreadsheet application',
                   ('images/excel-small.png', '[Excel]'))]

    if searchName and not searchUser:
        otherlinks.insert(0, ('results/%s/%s' % (os.environ['REMOTE_USER'], urllib.parse.quote(searchName)),
                              '',
                              'Publishable Link',
                              'Link to this named query usable by anyone',
                              ('images/publish-small.png', '[Publish]')))

    print("        <div id='tiqitOtherLinks'>")

    for url, onclick, string, title, image in otherlinks:
        print("""
         <div><a href='%s' onclick='%s' title='%s'><img src='%s' alt='%s'>%s</a></div>""" % (url, onclick, title, image[0], image[1], string))

    print("        </div>")

    print("<h1>Search Results - <span id='resultsFilterCount'>%s matching entr%s</span></h1>" % (numres, numres == "1" and 'y' or 'ies'))

    if len(matches) == 0:
        print("<p id='noResultsWarning'><img src='images/warning-small.png' alt='/!\\'> No results returned.</p>")

    if 'groupby' not in args:
        groupby = ''
    else:
        groupby = sort[0].field.name
    filters = Filter('results',
                     [x.name for x in selection if x.filterable],
                     showCount='resultsFilterCount', clearbutton=True,
                     allowMulti=True, allowInvert=True, allowGroupBy=True,
                     initialGroupBy=groupby)

    for bug in matches:
        filterArgs = {}
        for i in range(len(selection)):
            # Strip any HTML tags out of the strings
            field = selection[i].name
            filterArgs[field] = tagre.sub("", bug.getSanitisedValue(field, outputType == FORMAT_NORMAL))
        filters.add(filterArgs)

    filters.write()

    tableNameCounter = 1
    def printTableHeader(caption, num):
        tabid = 'results'
        if 'groupby' in args:
            tabid = 'results%d' % num
        print("<table id='%s' style='margin-bottom: 2em; width: 100%%;' class='tiqitTable'>" % tabid)
        if caption and 'groupby' in args:
            print("<caption><span class='tiqitTableCount'></span>%s: %s</caption>" % (prikeytype.name, caption))
        else:
            print("<caption><span class='tiqitTableCount'></span></caption>")
        print("<colgroup span='%d'></colgroup>" % len(selection))
        print("<colgroup></colgroup>")
        print("<thead>")
        print("<tr>%s</tr>" % "".join(["<th field='%s'><a onclick='sortResults(event);'>%s</a></th>" % (encodeHTML(f.name), encodeHTML(f.shortname)) for f in selection]))
        print("</thead>")
        print("<tbody>")

    def printTableFooter():
        print("</tbody>\n</table>")

    # Get the first primary key and start the first table
    prikey = ""
    print("<div id='resultsTableContainer'>")
    if len(matches) > 0:
        prikey = matches[0][prikeytype.name]
        printTableHeader(prikey, tableNameCounter)
    else:
        printTableHeader(prikey, tableNameCounter)
        # Insert an empty table row to keep the table rendered
        print("<tr id='resultsTablePlaceholderRow'>%s</tr>" % "".join(["<td></td>" for f in selection]))

    # We'll be adding attributes to each row, so get the names once
    attr_names = [x.name for x in parents]

    for bug in matches:
        # Check whether we need to start a new table
        newprikey = bug[prikeytype.name]
        if prikey != newprikey and 'groupby' in args:
            printTableFooter()
            prikey = newprikey
            tableNameCounter += 1
            printTableHeader(prikey, tableNameCounter)

        #
        # Construct the parent list. All parents should be there as
        # attributes whether their values are empty or not
        #
        attr_values = ["'%s'" % encodeHTML(bug[x.name]) for x in parents]
        attributes = list(map("=".join, list(zip(attr_names, attr_values))))

        pretty_vals = [bug.getSanitisedValue(x.name, outputType == FORMAT_NORMAL) for x in selection]

        print("<tr id='%s' lastupdate='%s'%s><td>%s</td></tr>" % (bug['Identifier'], bug['Sys-Last-Updated'], " ".join(attributes), "</td><td>".join(pretty_vals)))

    printTableFooter()
    print("</div>")

    printPageFooter()

elif outputType == FORMAT_CSV:
    print("Content-Disposition: attachment; filename=results.csv")
    print("Content-Type: text/csv\n")

    # Print header
    print("%s" % ','.join([x.shortname for x in selection]))

    for bug in matches:
        print('"%s"' % '","'.join([bug[x.name] for x in selection]))

elif outputType == FORMAT_RSS:
    print("""Content-Type: application/xml

<?xml version='1.0' encoding='utf-8' ?>
<rss version='2.0'>
 <channel>
  <title>Search results - %s</title>
  <link>%s</link>
  <description>Some search results</description>
  <language>en-gb</language>
  <lastBuildDate>%s</lastBuildDate>
  <generator>%s v%s</generator>
  <ttl>30</ttl>""" % (Config().section('general').get('sitetitle'), os.environ['REQUEST_URI'].replace('&', '&amp;').replace('format=rss', 'format=normal'), time.strftime("%a, %d %b %Y %H:%M:%S GMT"), Config().section('general').get('sitename'), VERSION_STRING))

    # Summary is in the output, so there could be more newlines than just the
    # ones between rows. So split more cleverly.
    for bug in matches:
        print("""
  <item>
   <title><![CDATA[%s - %s]]></title>
   <link>%s%s</link>
   <description><![CDATA[%s]]></description>
   <author>%s</author>
   <guid permaLink='false'>%s</guid>
   <pubDate>%s</pubDate>
  </item>""" % (bug['Identifier'], encodeCDATA(bug['Headline']), getBaseHost(), bug['Identifier'], encodeCDATA(bug['Summary']), bug['Submitter'], bug['Identifier'], time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.strptime(bug['Submitted-on'], "%m/%d/%Y %H:%M:%S"))))

    print("""
 </channel>
</rss>""")

elif outputType == FORMAT_XML:
    printXMLPageHeader()
    printXMLMessages()

    print("\n".join(plugins.printXMLSection(PAGE_RESULTS)))

    printXMLSectionHeader("buglist")

    for bug in matches:
        print("  <bug identifier='%s' lastupdate='%s'>" % (bug['Identifier'], bug['Sys-Last-Updated']))

        for i in range(len(requested)):
            print("   <field name='%s'><![CDATA[%s]]></field>" % (requested[i].name.replace("'", "&apos;"), encodeCDATA(bug[requested[i].name])))

        print("  </bug>")

    printXMLSectionFooter("buglist")
    printXMLPageFooter()

elif outputType == FORMAT_JSON:
    printJSONPageHeader()

    json_list = []
    for bug in matches:
        json_obj = {}
        for i in range(len(requested)):
            json_obj[requested[i].name] = bug[requested[i].name]
        json_list.append(json_obj)

    print(json.dumps(json_list))
