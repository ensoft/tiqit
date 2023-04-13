#!/usr/bin/python3
#
# Copyright (c) 2017 Ensoft Ltd, 2010 Martin Morrison
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from tiqit import *
from backend import allFields
from tableFilter import *

printPageHeader(PAGE_FIELDS, hideSavedSearches=True, hideNamedBugs=True)
printMessages()

print("<h1>Fields</h1>")

fields = list(allFields.keys())
fields.sort()

filters = Filter('fields', ('Type', 'MVF', 'Sys', 'Desc', 'Requires'), clearbutton=True, allowMulti=True)

for f in fields:
    f = allFields[f]
    filterArgs = {'Type': f.type, 'MVF': f.mvf and '*' or '', 'Sys': f.editable and '*' or '', 'Desc': f.descripted and '*' or '', 'Requires': ' '.join(map(str, f.requires))}
    filters.add(filterArgs)

filters.write()

print("<table class='tiqitTable' width='75%' id='fields'>")
print("<thead>")
print("<tr><th>%s</th></tr>" % "</th><th>".join(["Name", "Type", "Len", "MVF", "Sys", "States", "Allow", "Desc", "Requires", "Values"]))
print("</thead><tbody>")
for f in fields:
    f = allFields[f]
    print("<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>" % (f.name, f.type, f.flen, f.mvf and "*" or '', f.editable and "*" or '', f.descripted and '*' or '', ' '.join(map(str, f.requires))))
    if f.values:
        print("<select>")
        for v, d in zip(f.values, f.descs):
            if d != v:
                print("<option>%s - %s</option>" % (v, d))
            else:
                print("<option>%s</option>" % v)
        print("</select></td></tr>")
    else:
        print("</td></tr>")
print("</tbody></table>")

printPageFooter()
