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

#
# This file defines the external API of the backends, and splits out
# to the right one depending on the Project.
#
# It also defines a few helper functions first.
#

from tiqit import *
import fields, sys, re, utils
from StringIO import StringIO

_backends = {}
def initialise():
    global allFields
    allFields = fields.load()

    # Import all the configured backends
    for prefix, mod in Config().section('backends').items():
        # Should probably check prefix is valid here
        __import__(mod)
        _backends[prefix] = sys.modules[mod]

#
# Helper functions (not part of external API)
#

noteTypes = ("A-comments",
             "C-comments",
             "Code-review",
             "Configuration",
             "Crash-decode",
             "D-comments",
             "Debug-output",
             "Deferral-Info",
             "Dev-escape-comments",
             "Documentation",
             "EDP-resolver-comments",
             "Eng-notes",
             "Evaluation",
             "F-comments",
             "Field-Notice-Info",
             "H-comments",
             "I-comments",
             "J-comments",
             "M-comments",
             "N-comments",
             "O-comments",
             "Other",
             "P-comments",
             "PSIRT-evaluation",
             "R-comments",
             "Release-note",
             "SS-Eval",
             "SS-Review",
             "SS-Test",
             "Static-analysis",
             "TS-Eval",
             "TS-Info",
             "Test",
             "Testplan",
             "U-comments",
             "Unit-test",
             "Unknown-type",
             "V-comments",
             "W-comments",
             "Workaround");

class DataCommon(object):
    """ 
    DataCommon: Common data super class
    Allows data from all sources to be wrapped so that the Field: Value data 
    mapping method is common. 
    DataCommon and has the following methods:
    getSanitisedValue: returns the transformed value of the given TiqitField 
                       The raw value is obtained using the Field name
                       from the base class's own "getRawValue" function. 
                       There is an option for whether the data should be in
                       standard or HTML format.
    __getitem__: standard python dictionary accessor which calls
                 getSanitisedValue asking for standard formatting.
                 Supplied for code neatness as this is the most commonly used access.
    Any concrete subclass of DataCommon must provide its own _getRawValue 
    function to provide the raw value of the given field based on the data

    """
    def __getitem__(self, key):
        return self.getSanitisedValue(key, False)
    @utils.memoize
    def getSanitisedValue(self, name, pretty=False):
        # First convert the name (which is the field unique name) to the view
        # name(s) under which the value in the data is to be found
        indexNames = allFields[name].viewnames
        # Now get the values
        vals = map(self._getRawValue, indexNames)
        # Now convert the values according to the arguments
        if pretty:
            value = allFields[name].filterHtml(self, *map(encodeHTML, vals))
        else:
            value = allFields[name].filterView(self, *vals)
        return value

    def getHistory(self):
        """
        Returns a list of dicts containing the following fields:
        - Date: a string representing the date in some random format
        - Operation: the operation that the event is tracking
        - NewValue: the new value of the field
        - OldValue: the previous value of the field
        - Field: the name of the field that is changing (not converted?)
        - User: the user who performed the change
        - DateVal: the date in a useful format (from data.mktime())
        """
        return []
    def getEnclosures(self):
        """
        Returns a list of dicts containing the following fields:
        - Date: a string representing the date the note was last changed
        - Creator: user who created the note
        - Updater: user who last updated the note
        - Type: the type string of the note
        - Title: title of the note
        - Note: the note content
        - Size: the number of characters in the note
        - Identifier: the bugid the note belongs to (i.e. of this bugdata)
        """
        return []
    def getAttachments(self):
        """
        Returns a list of dicts containing the following fields:
        - Date: a string representing the date the note was last changed
        - Creator: user who created the attachment
        - Updater: user who last updated the attachment
        - Type: the type string of the attachment
        - Title: title of the attachment
        - Size: the number of characters in the attachment
        - Identifier: the bugid the attachment belongs to
        - Name: wtf, a second name/title thing
        - Ext: wtf, a file extension or something
        - LinkName: the name that should be used when trying to find the damned thing.
        """
        return []
    def getRelates(self):
        """
        Returns a list of 3-tuples containing:
        - Bug ID of the related bug
        - Relationship (a user-friendly string)
        - Boolean indicating whether the relationship is deleteable
        """
        return []

class OverriddenData(DataCommon):
    """ 
    OverriddenData: Instance of DataCommon
    Initialised with two sets of data - the base data, in DataCommon format,
    and some overrides, formatted as a dictionary of name to View 
    Values.
    If an override value is present for a particular field this is used.
    Otherwise the base data is used.
    OverriddenData has the following methods:
    getSanitisedValue: First chooses which of the data items the value should 
                       be extracted from (overrides first as above).
                       Then returns the standard format value from this data.
                       Pretty formatting is not supported.
    """
    def __init__(self, data, overrides):
        self._data = data
        self._overrides = overrides
    def getSanitisedValue(self, name, pretty):
        assert not pretty, "Overridden data only supports standard output format"
        if name in self._overrides:
            return self._overrides[name]
        else:
            return self._data[name]
    def __repr__(self):
        return "<OverriddenData(data=%s,overrides=%s)>" % (str(self._data), str(self._overrides))

def isValidField(field, data):
    # This field may be banned. Check all of the fields in its "bannedif" list
    # and get the value to check that it is not in the list. To get the 
    # value we must check the changes first (incase the value of the parent
    # is also being updated) or if no value is found here then check the bug 
    # data for the original value - the data object handles this for us
    for banned in field._bannedIf:
        if data[banned] in field._bannedIf[banned]:
            return False
    return True

def extractFieldsFromFormat(cls, formats):
    fieldsInUpdate = []
    for title, titleDetail, format in formats:
        fieldsInUpdate += [allFields[x] for x in re.findall('%\((.*?)(?:Raw)?\)s',
                           cls.getFormat(format)) if not x.endswith('Label')]
    return list(dict.fromkeys(fieldsInUpdate))

def getFormatArguments(data, inFields=None):
    if not inFields:
        inFields = allFields.values()
    args = {}

    for field in inFields:
        val = data[field.name]

        args['%sRaw' % field.name] = val

        # Plugins can add information to the Label; use a StringIO
        label = StringIO("<label for='%s' id='%sLabel'>%s:</label>" % (field.name, field.name, field.longname))
        plugins.updateLabel(field, label)
        args['%sLabel' % field.name] = label.getvalue()
        label.close()

        args[field.name] = field.filterEditableHtml(data, val)

    # Now return the lovely dict
    return args

#
# The first section deals with loading bugs
#

def loadBugs(bugids):
    """
    Loads the given bugids and returns an array of bug data objects.
    """
    bck = None
    curr = []
    data = []
    for x in bugids:
        if bck != x[:3]:
            if curr:
                data.extend(_backends[bck].loadBugs(curr))
                curr = []
            bck = x[:3]
        curr.append(x)
    data.extend(_backends[bck].loadBugs(curr))
    return data

def performQuery(*args):
    """
    Performs the given query. (Laziness omits the arguments here)

    Ask each backend to perform it, and concatenate their results.
    """
    results = []
    for bck in _backends:
        more = _backends[bck].performQuery(*args)
        if more:
            results.extend(more)
    return results

#
# This section deals with actually updating the database
#

def createBug(fields):
    return _backends[fields['Project'][:3]].createBug(fields)

def updateBug(bugid, changes):
    return _backends[bugid[:3]].updateBug(bugid, changes)

def addNote(bugid, noteType, noteTitle, noteContent, isUpdate=False):
    """
    Add a new note to the given bug.

    Arguments:
      - bugid: the ID of the bug to add the note to
      - noteType: type of note to add (str)
      - noteTitle: the title to give the node
      - noteContent: the content of the new note
      - isUpdate: is this an update to an existing note
    """
    return _backends[bugid[:3]].addNote(bugid, noteType, noteTitle, noteContent, isUpdate)

def deleteNote(bugid, noteTitle):
    return _backends[bugid[:3]].deleteNote(bugid, noteTitle)

def renameNote(bugid, noteType, noteTitle, newTitle):
    return _backends[bugid[:3]].renameNote(bugid, noteType, noteTitle, newTitle)

def addAttachment(bugid, fileTitle, filename):
    return _backends[bugid[:3]].addAttachment(bugid, fileTitle, filename)

def deleteAttachment(bugid, fileTitle):
    return _backends[bugid[:3]].deleteAttachment(bugid, fileTitle)

def renameAttachment(bugid, fileTitle, newTitle):
    return _backends[bugid[:3]].renameAttachment(bugid, fileTitle, newTitle)

def attachmentUrl(info):
    return _backends[info['Identifier'][:3]].attachmentUrl(info)

def attachmentDownloadUrl(info):
    return _backends[info['Identifier'][:3]].attachmentDownloadUrl(info)