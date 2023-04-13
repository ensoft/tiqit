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

import os, time
from tiqit import *
from backend import allFields

__all__ = [
    'parseQuery',
    'parseSelection',
    'parseSort', 'ORDER_ASC', 'ORDER_DESC',
    'parseAdvanced',
    ]

def parseQuery(args):
    """
    Parses a query out of the given arguments (which are likely the Arguments
    object, but can be any dict-like object).
    """
    row = 1
    level = 0
    query = ''
    status = None

    # Some fields should be mapped to equivalent names. The main use of this is to
    # support legacy searches.
    aliases = plugins.getFieldAliases()

    while 'field%d' % row in args:
        field = args['field%d' % row]
        rel = args['rel%d' % row]
        val = args['val%d' % row]
        special = None
        negate = False
        mvv = False # Multi Value Value

        if field in aliases:
            field = aliases[field]

        mvf = allFields[field].mvf

        # Check for negation
        if rel[0] == '!':
            negate = True
            rel = rel[1:]

        # Check for special relationships
        if rel == 'startswith':
            rel = 'LIKE'
            val = '%s*' % val
        elif rel == 'endswith':
            rel = 'LIKE'
            val = '*%s' % val
        elif rel == 'notstartswith':
            rel = 'LIKE'
            val = '%s*' % val
            negate = not negate
        elif rel == 'notendswith':
            rel = 'LIKE'
            val = '*%s' % val
            negate = not negate
        elif rel == 'contains':
            rel = 'LIKE'
            val = '*%s*' % val
        elif rel == 'doesnotcontain':
            rel = 'LIKE'
            val = '*%s*' % val
            negate = not negate
        elif rel == 'isoneof':
            # Note! Careful when using this one. Only use with non-special
            # fields.
            rel = '='
            mvv = True
        elif rel == 'isnotoneof':
            rel = '<>'
            mvv = True
        elif rel == 'withinlast':
            rel = '>='
            thetime = time.time()

            splitup = val.split(' ')
            if len(splitup) == 1:
                try:
                    num = int(splitup[0])
                    unit = 'day'
                except:
                    num = 1
                    unit = splitup[0]
            else:
                num, unit = splitup
                num = int(num)

            if unit.startswith('hour'):
                thetime -= (num * (60 * 60))
            elif unit.startswith('week'):
                thetime -= (num * (60 * 60 * 24 * 7))
            elif unit.startswith('month'):
                thetime -= (num * (60 * 60 * 24 * 30))
            elif unit.startswith('day'):
                thetime -= (num * (60 * 60 * 24))
            else:
                raise TiqitError("Unknown unit of time: '%s'" % unit)

            val = time.strftime('%d/%m/%y', time.localtime(thetime))

        # Invert order relations if the field is inverted
        if allFields[field].invertsort:
            if rel == '<':
                rel = '>'
            elif rel == '>':
                rel = '<'
            elif rel == '>=':
                rel = '<='
            elif rel == '<=':
                rel = '>='

        # Check for special fields.
        # The only generic special field is dates (soon to be made even better!)
        if allFields[field].type == 'Date':
            day, mon, year = list(map(int, val.split('/')))
            val = '%02u/%02u/%02u' % (mon, day, year)

        # Do any filtering
        try:
            val = allFields[field].filterEdit(args, val)
        except:
            # If there was a problem with the filtering, then don't go on
            sendMessage(MSG_ERROR, "Failed to convert %s value '%s' for search.</p>" % (field, val))
            redirect('search?%s' % os.environ['QUERY_STRING'])

        # Do Multi-Value values.
        if mvv and len(val.split(',')) > 1:
            # Lots of values in this query. Make a 'special' string.
            special = '('
            for value in val.split(','):
                if special[-1] != '(':
                    if rel == "<>":
                        special += ' AND '
                    else:
                        special += ' OR '
                special += '[%s] %s "%s"' % (allFields[field].viewnames[0], rel, value)
            special += ')'

        # Add required close brackets
        if row > 1:
            while level > int(args['opLevel%d' % (row - 1)]):
                query += ')'
                level -= 1

            query += ' %s ' % args['operation%d' % (row - 1)]

        # And open brackets.
        while level < int(args['level%d' % row]):
            query += '('
            level += 1

        if negate:
            query += 'NOT '

        if special:
            query += special
        else:
            if mvf:
                query += 'EXISTS('
            else:
                query += '('

            query += '[%s] ' % allFields[field].viewnames[0]
            query += rel
            query += ' "%s" ' % val

            # The backend is assumed to use three-valued logic. We don't want to
            # expose this at the front end, so map all potential unknown values to
            # either true or false appropriately.
            if (rel in ("NOT LIKE", "<>") and not negate):
                query += 'OR [%s] = "" ' % allFields[field].viewnames[0]
            elif (rel in ("LIKE", "=") and negate):
                query += 'AND [%s] <> "" ' % allFields[field].viewnames[0]
                
            query += ') '

        row += 1

    while level > 0:
        query += ')'
        level -= 1

    #
    # Check for the default query string, which we should just ignore
    #
    if query == '[Component] = "" ':
        query = ""

    return query

def parseSelection(args):
    """
    Parse out the fields that the user selected from the given arguments.
    """

    nextSelection = 1
    selection = []

    while 'selection%d' % nextSelection in args:
        field = args['selection%d' % nextSelection]

        selection.append(allFields[field])
        nextSelection += 1

    return selection

ORDER_ASC = 'ASC'
ORDER_DESC = 'DESC'

def parseSort(args):
    nextSort = 1
    sort = []

    class SortOrder(object):
        def __init__(self, field, order):
            self.field = field
            self.order = order

    while 'sort%d' % nextSort in args:
        field = args['sort%d' % nextSort]
        order = args['sortOrder%d' % nextSort]

        fieldObj = allFields[field]

        if not order in (ORDER_ASC, ORDER_DESC):
            raise ValueError("%s is not a valid sort order" % order)
        if fieldObj.invertsort:
            order = order == ORDER_ASC and ORDER_DESC or ORDER_ASC

        sort.append(SortOrder(fieldObj, order))
        nextSort += 1

    return sort

def parseAdvanced(args):
    # First status
    if 'Status' in args:
        states = args.asList('Status')
        valid = allFields['Status'].getAllValues()
        
        states = list(set(states) & set(valid))
    else:
        states = None

    # Project
    if args['Project'] and args['Project'] != 'ALL':
        project = args['Project']
        if project not in allFields['Project'].getAllValues():
            raise ValueError("%s is not a valid Project" % project)
    else:
        project = None

    # Buglist
    if 'buglist' in args and args['buglist']:
        buglist = extractBugIds(args['buglist'])
    else:
        buglist = None

    # UserType
    if 'UserType' in args and args['UserType']:
        usertype = args['UserType']
    else:
        usertype = None

    # UserName
    if 'UserName' in args and args['UserName']:
        username = args['UserName']
    else:
        username = None

    return (states, project, buglist, usertype, username)
