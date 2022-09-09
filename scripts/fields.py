#
# This defines what a 'Field' is
#

import time, re
from StringIO import StringIO
from utils import writeOptions, encodeHTML
from tiqit import *

__all__ = [
    "TiqitField",
    "load",
    "crossListsOfTuples",
    "filterDisplayDateOnly",
    "filterEditDateOnly",
    "filterDisplayIdentifier",
    "filterDisplayDefect",
    "filterDisplayUser",
]

TEXT_TYPES = ('Component', 'AcmeComponent', 'Text', 'Number', 'ForeignID', 'Character', 'Varchar')

# This function calculates the cross product of 2 lists of tuples to give
# another list of tuples as per the following example:
# lista = [(I,J), (K,L)]
# listb = [(M,N), (O,P)]
# returns: [(I,J,M,N), (I,J,O,P), (K,L,M,N), (K,L,O,P)]
def crossListsOfTuples(lista, listb):
    if len(lista) == 0:
        new_tuple = listb
    elif len(listb) == 0:
        new_tuple = lista
    else:
        new_tuple = []
        for a in lista :
            for b in listb:
                new_tuple.append(a + b)
    return new_tuple

FLAG_REQ = 1<<0
FLAG_MVF = 1<<1
FLAG_INVERT = 1<<2
FLAG_SEARCH = 1<<3
FLAG_EDIT = 1<<4
FLAG_VIEW = 1<<5
FLAG_FILTER = 1<<6
FLAG_VOLATILE = 1<<7

VARFIELDS = ('searchvals', 'searchrels', 'values', 'descs', '_parentFields', '_perParentFieldDescs', '_perParentFieldValues', '_childFields', '_mandatoryIf', '_bannedIf', 'defaultsWith', 'defaultsFor', '_projFilterView', '_projFilterHtml', '_projFilterEdit', '_projFilterEditableHtml')

class TiqitField(object):
    """
    A Field is single displayable, searchable, and potentially editable entity.

    It has a number of properties:
    - an internal name: the name used to write to the backends
    - a view name: the name used to read from the backends
    - a long display name: used normally
    - a short display name: for displaying column headers in search results
    - a type: determines how it will be displayed
    - mvf: whether it is multi valued or single valued
    - a maximum length: 0 indicates unlimited
    - a display length: how wide fields to display it should be
    - whether it should be reverse sorted
    - whether the field is searchable
    - whether the field is editable
    - whether the field is viewable (e.g. Org is not)
    - whether the field is filterable (non-filterable means varies too much)
    - whether the field is a basic requirement for a new bug
    - the internal names that are required when searching
    
    There are some special search properties:
    - searchvals: extra vals/desc pair you can search on
    - searchrels: the relationships that it can be searched on (if special)
    - searchnames: the names to read from the backend to pretty print it
    
    There are a set of fields to describe the allowed values of the field
    where the allowed values may depend on the current value of various
    other fields:
    - values: for fields with values that do not depend on another field
    - descs: optional descriptions for the values
    - parentFields: Fields whose value affects the allowed values of this field
    - perParentFieldValues: dictionary of allowed value lists keyed by a 
                            tuple of parent field values
    - childFields: Fields whose allowed values are affected by the value taken
                   by this field

    Fields defining when this field is mandatory or banned based on the values
    taken by other fields:
    - mandatoryIf: This field is mandatory if ALL of the fields have a value
                   given in the mandatoryif list
    - bannedIf: This field is banned if any of these fields have a value 
                given in the bannedif list. Note that the banned nature 
                overrides the mandatory nature under all circumstances

    Fields used to automatically update other field values:
    - defaultsWith: Tuple of associated fields (usually parent fields) whose
                    values, when taken with the value of this field, can be
                    used as a lookup key in the database for default values of
                    other fields.
    - defaultsFor: Tuple of fields for which defaults are available when the
                   value of this field changes.

    There are also some functions, dependent on the class:
    - convert value for display (search results plain)
    - convert value for HTML display (search results pretty view)
    - back convert displayed value into back end value
    - convert value into an editor object
    """

    def __init__(self, fname, savename, viewnames, longname, shortname,
                 ftype, maxlen, displaylen,
                 req,
                 mvf=False, invertsort=False,
                 searchable=True, editable=True, viewable=True,
                 filterable=True, volatile=False):
        self.name = fname
        assert savename == viewnames[0], "Internal name %s must be the first view name %s" % (savename, viewnames[0])
        self.viewnames = viewnames
        self.longname = longname
        self.shortname = shortname
        self.type = ftype
        self.maxlen = maxlen and int(maxlen) or 0
        self.displaylen = displaylen
        self.req = req
        self.mvf = mvf
        self.invertsort = invertsort
        self.searchable = searchable
        self.editable = editable
        self.viewable = viewable
        self.filterable = filterable
        self.volatile = volatile

        self._initStatics()

    def _initStatics(self):
        self.searchvals = None
        self.searchrels = None

        self.values = []
        self.descs = []
        self._parentFields = []
        self._perParentFieldValues = {}
        self._perParentFieldDescs = {}
        self._childFields = []

        self._mandatoryIf = {}
        self._bannedIf = {}

        self.defaultsWith = ()
        self.defaultsFor = []

        self.showVals = True

        self._projFilterView = {}
        self._projFilterHtml = {}
        self._projFilterEdit = {}
        self._projFilterEditableHtml = {}

        self._filterView = filterNone
        self._filterHtml = filterNone
        self._filterEdit = filterNone

        # Now let's set up the editable display function
        if self.name == 'Summary':
            self._filterEditableHtml = filterDisplayEditableSummary
            self.rows = 20
        elif self.type in TEXT_TYPES and not self.editable:
            self._filterEditableHtml = filterNone
        elif (self.type in TEXT_TYPES or self.type == 'Userid' and self.mvf) and self.editable:
            self._filterEditableHtml = filterDisplayEditableText
        elif self.type == 'Date' and not self.editable:
            self._filterEditableHtml = filterNone
        elif self.type == 'Date' and self.editable:
            self._filterEditableHtml = filterDisplayEditableDate
            self._filterHtml = filterDisplayDateOnly
            self._filterView = filterDisplayDateOnly
        elif self.type == 'DefectID':
            self._filterEditableHtml = filterDisplayEditableDefect
            self._filterHtml = filterDisplayDefect
        elif self.type == 'Userid' and self.editable and not self.mvf:
            self._filterEditableHtml = filterDisplayEditableUser
            self._filterHtml = filterDisplayUser
        elif self.type == 'Userid' and not self.editable:
            self._filterEditableHtml = filterDisplayUser
            self._filterHtml = filterDisplayUser
        elif self.type == 'Boolean':
            self._filterEditableHtml = filterDisplayEditableCheckbox
        else:
            raise KeyError, "Unknown field type for field '%s' (type is %s)" % (self.name, self.type)

    def _getSaveName(self):
        return self.viewnames[0]
    savename = property(_getSaveName)

    def __getstate__(self):
        state = {}
        state['name'] = self.name
        state['type'] = self.type
        if len(self.viewnames) > 1 or self.viewnames[0] != self.name:
            state['viewnames'] = self.viewnames
        if self.longname != self.name:
            state['longname'] = self.longname
        if self.shortname != self.longname:
            state['shortname'] = self.shortname
        if self.maxlen:
            state['maxlen'] = self.maxlen
        if self.displaylen:
            state['displaylen'] = self.displaylen
        flags = 0
        if self.req:
            flags |= FLAG_REQ
        if self.mvf:
            flags |= FLAG_MVF
        if self.invertsort:
            flags |= FLAG_INVERT
        if self.searchable:
            flags |= FLAG_SEARCH
        if self.editable:
            flags |= FLAG_EDIT
        if self.viewable:
            flags |= FLAG_VIEW
        if self.filterable:
            flags |= FLAG_FILTER
        if self.volatile:
            flags |= FLAG_VOLATILE
        state['FLAGS'] = flags
        for attr in VARFIELDS:
            if getattr(self, attr):
                state[attr] = getattr(self, attr)

        return state

    def __setstate__(self, state):
        if 'FLAGS' not in state:
            self.__dict__.update(state)
            return
        self.name = state['name']
        self.type = state['type']
        self.viewnames = 'viewnames' in state and state['viewnames'] or (self.name,)
        self.longname = 'longname' in state and state['longname'] or self.name
        self.shortname = 'shortname' in state and state['shortname'] or self.longname
        self.maxlen = 'maxlen' in state and state['maxlen'] or 0
        self.displaylen = 'displaylen' in state and state['displaylen'] or 0
        flags = state['FLAGS']
        self.req = bool(flags & FLAG_REQ)
        self.mvf = bool(flags & FLAG_MVF)
        self.invertsort = bool(flags & FLAG_INVERT)
        self.searchable = bool(flags & FLAG_SEARCH)
        self.editable = bool(flags & FLAG_EDIT)
        self.viewable = bool(flags & FLAG_VIEW)
        self.filterable = bool(flags & FLAG_FILTER)
        self.volatile = bool(flags & FLAG_VOLATILE)

        self._initStatics()

        for attr in VARFIELDS:
            if state.has_key(attr):
                setattr(self, attr, state[attr])

    def hasParentDependency(self):
        return bool(self._perParentFieldValues)

    def getAllValues(self):
        if self.hasParentDependency():
            vals = []
            for more in self._perParentFieldValues.values():
                vals.extend(more)
            vals = list(dict.fromkeys(vals))
            vals.sort()
        else:
            vals = self.values
        return vals

    def _lookupParentArray(self, parent_array, data):
        import backend
        # Need to find all of the valid parent keys based on the parent values
        parent_keys = []
        for parent in self._parentFields:
            parent_tuples = []
            parent_val = data[parent]
            if parent_val:
                parent_vals = [parent_val]
            else:
                parent_vals = backend.allFields[parent].getAllValues()
            for val in parent_vals:
                parent_tuples.append((val,))
            # We have a list of allowed parent values for this parent.
            # Combine it with previous found parent values to get the full
            # list of keys
            parent_keys = crossListsOfTuples(parent_keys, parent_tuples)
            
        # Now use the parent keys to build up a list of allowed values
        vals = []
        for parent_key in parent_keys:
            if parent_key in parent_array:
                vals.extend(parent_array[parent_key])
        values = list(dict.fromkeys(vals))
        values.sort()
        return values

    def getValues(self, data):
        if self.hasParentDependency():
            return self._lookupParentArray(self._perParentFieldValues, data)
        else:
            return self.values

    # Return either an array of values, or an array of descriptions and values,
    # joined with a hyphen.
    def getDisplayValues(self, data):
        if self.hasParentDependency():
            if self._perParentFieldDescs and self.showVals:
                assert set(self._perParentFieldDescs.keys()) == set(self._perParentFieldValues.keys())
                def getOptions(vals, descs):
                    assert len(vals) == len(descs)
                    return ["%s - %s" % (v, d) if v != "" and d != "" else "" for v, d in zip(vals, descs)]
                a = dict((k, getOptions(self._perParentFieldValues[k],
                                        self._perParentFieldDescs[k])) for k in
                                self._perParentFieldDescs.keys())
                return self._lookupParentArray(a, data)
            else:
                return self.getValues(data)
        else:
            if self.descs == self.values:
                return self.values
            else:
                return map(" - ".join, zip(self.values, self.descs))

    def filterView(self, data, *val):
        """ 
        filterView: Transforms the value(s) provided for this field into its
                    viewable format.
        val: The value must be the raw value(s) of the view names of this field
        data: The data provided must be an instance of a concrete subclass of 
              DataCommon and is provided incase the transform requires
              knowledge of the value of other fields. e.g. the transform 
              required may be different depending on the Project in which we
              are working.
        """
        if self._projFilterView:
            className = data['Project']
            if self._projFilterView.has_key(className):
                return self._projFilterView[className](self, data, *val)
            else:
                return self._filterView(self, data, *val)
        else:
            return self._filterView(self, data, *val)

    def filterHtml(self, data, *val):
        """ 
        filterHtml: Transforms the value(s) provided for this field into its
                    HTML viewable format.
        val: The value must be the raw value(s) of the view names of this field
        data: The data provided must be an instance of a concrete subclass of 
              DataCommon and is provided incase the transform requires
              knowledge of the value of other fields. e.g. the transform 
              required may be different depending on the Project in which we
              are working.
        """
        if self._projFilterHtml:
            className = data['Project']
            if self._projFilterHtml.has_key(className):
                return self._projFilterHtml[className](self, data, *val)
            else:
                return self._filterHtml(self, data, *val)
        else:
            return self._filterHtml(self, data, *val)

    def filterEdit(self, data, val):
        """ 
        filterEdit: Transforms the value(s) provided for this field back in to
                    its backend format.
        val: The value must be the value(s) of this field as provided by the
             user
        data: The data provided must be an instance of a concrete subclass of 
              DataCommon and is provided incase the transform requires
              knowledge of the value of other fields. e.g. the transform 
              required may be different depending on the Project in which we
              are working.
        """
        if self._projFilterEdit:
            className = data['Project']
            if self._projFilterEdit.has_key(className):
                return self._projFilterEdit[className](self, data, val)
            else:
                return self._filterEdit(self, data, val)
        else:
            return self._filterEdit(self, data, val)

    def filterEditableHtml(self, data, val):
        """ 
        filterEditableHtml: Transforms the value(s) provided for this field
                            into its HTML editable format.
        val: The value must be the value(s) of this field already filtered
             for standard viewing
        data: The data provided must be an instance of a concrete subclass of 
              DataCommon and is provided incase the transform requires
              knowledge of the value of other fields. e.g. the transform 
              required may be different depending on the Project in which we
              are working.
        """
        if self._projFilterEditableHtml:
            className = data['Project']
            if self._projFilterEditableHtml.has_key(className):
                return self._projFilterEditableHtml[className](self, data, val)
            else:
                return self._filterEditableHtml(self, data, val)
        else:
            return self._filterEditableHtml(self, data, val)

    def __eq__(self, other):
        return self.name == other.name and self.mvf == other.mvf and self.editable == other.editable and self.maxlen == other.maxlen and self.values == other.values and self._parentFields == other._parentFields and self._perParentFieldValues == other._perParentFieldValues and self._perParentFieldDescs == other._perParentFieldDescs and self._childFields == other._childFields and self._mandatoryIf == other._mandatoryIf and self._bannedIf == other._bannedIf

    def __repr__(self):
        return "TiqitField(%s)" % self.name

    def isMandatory(self, data):
        return all(data[fname] in vals for fname, vals in
                    self._mandatoryIf.iteritems()) if self._mandatoryIf else False


#
# These are the various conversion functions for various classes
#

# Generic convertors (by type, ignoring exact field name)

def filterNone(field, data, *val):
    return val[0]

def filterDisplayEditableText(field, data, val):
    vals = field.getValues(data)

    if not vals:
        if field.defaultsWith:
            display = "<span field='%s' class='tiqitIndicatorContainer tiqitDefaultLinkEditor'>" % field.name
        else:
            display = "<span class='tiqitIndicatorContainer'>"
        size = field.displaylen

        if field.defaultsWith:
            display += "<a class='tiqitDefaultLink' href='%sdefaultvals'> </a>" % Config().section('general').get('metaurl')
            size -= 5

        display += "<input id='%s' type='text' name='%s' size='%d'" % (field.name, field.name, size)

        if field.maxlen > 0 and not field.mvf:
            display += " maxlength='%d'" % field.maxlen

        if val:
            display += " value='%s'" % encodeHTML(val)

        if field.defaultsWith:
            display += " class='tiqitDefaultLinkInput'"
            display += " onchange='updateChildrenView(event); checkFormValidity(event); Tiqit.defaults.updateURL(%s, getFieldValueView)'></span>" % encodeJS(field.name)
        else:
            display += " onchange='updateChildrenView(event); checkFormValidity(event);'></span>"

    else:
        descs = field.getDisplayValues(data)
        values = zip(vals, descs)

        display = StringIO()
        writeOptions(field.name, values, val, 'updateChildrenView(event); checkFormValidity(event);', display)
        display = display.getvalue()

    return display

def filterDisplayEditableSummary(field, data, val):
    display = (
        "<textarea id='{0}' rows='{1}' cols='{2}' "
        "onChange='checkFormValidity(event);'>{3}</textarea>"
        "<textarea id='{0}Send' name='{0}' style='display: none'></textarea>"
        "<script type='text/javascript'>textareasToSubmit.push(['{0}', '{0}Send'])</script>"
    ).format(field.name, field.rows, field.displaylen, val)
    return display

def filterDisplayEditableDefect(field, data, val):
    display = ''
    if val:
        display += "<a href='view/%s'> </a>" % encodeHTML(val)

    display += "<input id='%s' type='text' name='%s' size='16'" % (field.name, field.name)

    if val:
        display += " value='%s'" % encodeHTML(val)

    display += " onchange='updateChildrenView(event); checkFormValidity(event)'>"

    return display

def filterDisplayEditableComp(field, data, val):
    return filterDisplayEditableText(field, data, val)

def filterDisplayEditableUser(field, data, val):
    display = """<span class='tiqitUserEditable tiqitIndicatorContainer'><a onclick='showUserDropDown(event, document.getElementById("%s"));'></a><input id='%s' type='text' name='%s' size='15'""" % (field.name, field.name, field.name)

    if val:
        display += " value='%s'" % encodeHTML(val)

    display += " onchange='updateChildrenView(event); checkFormValidity(event)'></span>"

    return display

def filterDisplayEditableCheckbox(field, data, val):
    display = "<input id='%s' type='checkbox' name='%s'" % (field.name, field.name)

    if val == 'Y':
        display += ' checked'

    display += " onchange='updateChildrenView(event); checkFormValidity(event)'>"

    return display

def filterDisplayEditableDate(field, data, val):
    display = """<a class='tiqitCalendarDropDown'></a><input id='%s' type='text' name='%s' size='20'""" % (field.name, field.name)
    if val:
        display += " value='%s'" % encodeHTML(val)

    display += " onchange='updateChildrenView(event); checkFormValidity(event);'>"

    return display

# Generic (all classes)

def filterDisplayDateOnly(field, data, val):
    return val and val.split(' ')[0]

def filterEditDateOnly(field, data, val):
    return val and (val + ' 21:00:00')

def filterDisplayIdentifier(field, data, id, headline):
    #id, headline = val.split(VALUE_SEP)
    return "<a href='%s' title='%s'>%s</a>" % (id, encodeHTML(headline), id)

def filterDisplayDefect(field, data, val):
    regex = re.compile('(' + '|'.join((r.pattern for r in plugins.getBugIdRegexes())) + ')')
    return regex.sub(r"<a href='\1'>\1</a>", val)

def filterDisplayUser(field, data, val):
    return val and "<a onclick='showUserDropDown(event);'>%s</a>" % encodeHTML(val)

#
# External Functions
#

def load():
   fields = database.get('tiqit.fields')

   addCustomFields(fields)
   plugins.addCustomFields(fields)

   return fields

def addCustomFields(fields):
    fields['Identifier']._filterHtml = filterDisplayIdentifier

