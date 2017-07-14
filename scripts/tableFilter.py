#! /usr/bin/python

from utils import *

#
# Provides a class to do filtering on a table. To be used in conjunction with
# filter.js, or some filtering functions of your own.
#

__all__ = ['Filter']

class Filter(dict):
    def __init__(self, name, columns, filterfunc=None, showCount=None,
                 clearbutton=False, allowMulti=False, allowInvert=False,
                 allowGroupBy=False, initialGroupBy='', filterArgs=None):
        """
        Initialise a Filter object. Arguments are the id of the table to
        filter; a sequence of column names to allow filtering on; and,
        optionally, the name of a JS function to do the filtering for you.
        """
        self.name = name
        for c in columns:
            self[c] = []
        self.columns = columns
        if filterfunc:
            self.filterfunc = filterfunc
        else:
            self.filterfunc = 'tiqitFilterTable'
        if filterArgs:
            self.filterArgs = filterArgs
        else:
            self.filterArgs = '"%s", tiqitFilterDefault, tiqitFilterPrepare' % self.name
        self.showCount = showCount
        self.clearbutton = clearbutton
        self.allowMulti = allowMulti
        self.allowInvert = allowInvert
        self.allowGroupBy = allowGroupBy
        self.initialGroupBy = initialGroupBy

    def add(self, vals):
        """
        Add values held in the given dict to the filters. vals must be a dict,
        the keys of which are column names, and the values possible values to
        filter on.
        """
        for key in vals:
            if key in self:
                if (vals[key], vals[key]) not in self[key]:
                    self[key].append((vals[key], vals[key]))

    def write(self):
        """
        Print out a line of <select> objects to allow filtering. These
        will call the specified function to perform the filtering, or
        the default in filter.js if the function was not specified.
        """
        args = {'name': self.name, 'func': self.filterfunc, 'args': self.filterArgs}
        print "<div id='%(name)sFilters' name='%(name)s'>" % args

        # Write header
        print "<div>Filter on: <span>"

        for f in self.columns:
            args['field'] = f
            self[f].sort()
            
            self[f].insert(0, ("NOFILTER", f))
            print """ <select name='%(field)s' id='%(name)sFilter%(field)s' onchange='%(func)s(%(args)s);'>""" % args

            for t in self[f]:
                print '<option value="%s">%s</option>' % (t[0].replace('"', '&quot;'), t[1])

            print "</select>"

        print "</span>"

        if self.allowMulti:
            print """<input id='%sFilterAddRow' type='button' value=' + ' onclick='tiqitFilterAddRow(%s);'> """ % (self.name, encodeJS(self.name))

        if self.clearbutton:
            print """<input type='button' value='Clear Filters' onclick='tiqitFilterClear("%s");'> """ % self.name

        if self.allowGroupBy:
            print """Group by: <select id='%(name)sGroupBy' onchange='filterGroupBy("%(name)s", this);'><option value='NOFILTER'></option>""" % args
            for f in self.columns:
                print '<option value="%s"%s>%s</option>' % (f.replace('"', '&quot;'), f == self.initialGroupBy and ' selected' or '', f)
            print "</select> "

        if self.allowInvert:
            print "<label for='%(name)sFilterNeg'>Invert Filter:</label>" % args
            print "<input type='checkbox' title='Invert Filter' id='%(name)sFilterNeg' name='%(name)sFilterNeg' onchange='%(func)s(%(args)s)'>" % args

        print "</div>"
        print "</div>"
