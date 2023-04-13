#
# Copyright (c) 2017 Ensoft Ltd, 2008-2010 Martin Morrison, Matthew Earl
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

import time
from tiqit import *
from fields import TiqitField

__all__ = [
    'addCustomFields',
    ]

def filterDisplayAge(field, data, val):
    return val and str(int(time.time() - time.mktime(time.strptime(val.strip(), "%m/%d/%Y %H:%M:%S"))) / 86400)

def filterEditAge(field, data, val):
    return time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(time.time() - (int(val) * 86400)))

def filterDisplayLink(field, data, id):
    return "<a href='%s' title='%s'><img src='images/bug-tiny.png'></a>" % (encodeHTML(id), encodeHTML(id))

bugNumber = 1
bugNumbers = {}

def getBugNumber(id):
    global bugNumber, bugNumbers
    if id not in bugNumbers:
        bugNumbers[id] = bugNumber
        bugNumber += 1

    return bugNumbers[id]

def filterDisplayBugNumber(field, data, id):
    return "%s %d" % (id, getBugNumber(id))
def filterDisplayBugNumberHtml(field, data, id):
    return "<span style='display: none'>%s </span><a href='%s' title='%s'>%d</a>" % (encodeHTML(id), encodeHTML(id), encodeHTML(id), getBugNumber(id))

def addCustomFields(fields):
    fields['Age'] = TiqitField('Age', 'Submitted-on', ('Submitted-on',), 'Age', 'Age',
                                'Number', 0, 10, True,
                                invertsort=True,
                                editable=False,
                                filterable=False,
                                volatile=True)
    fields['Age']._filterView = filterDisplayAge
    fields['Age']._filterHtml = filterDisplayAge
    fields['Age']._filterEdit = filterEditAge

    fields['Link'] = TiqitField('Link', 'Identifier', ('Identifier',), 'Link', 'Id',
                                 'Text', 0, 0, False,
                                 searchable=False,
                                 editable=False,
                                 filterable=False,
                                 volatile=True)
    fields['Link']._filterHtml = filterDisplayLink

    fields['Bug-number'] = TiqitField('Bug-number', 'Identifier', ('Identifier',), 'Bug-number', '#',
                                       'Number', 0, 5, False,
                                       searchable=False,
                                       editable=False,
                                       filterable=False,
                                       volatile=True)
    fields['Bug-number']._filterHtml = filterDisplayBugNumberHtml
    fields['Bug-number']._filterView = filterDisplayBugNumber

