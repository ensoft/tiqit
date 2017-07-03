#
# "Views" or "BugViews" are a veneer provided on top of the data stored in the
# backend databases for customising the display to the user. Use cases include:
#
# - Simplified user input for UT bugs
# - Focus on different fields depending on role (Manager, Engineer, Tester)
# - Restricted view for customers, visitors, or security-related issues
#
# and many more.
#
# The implementation is provided by a concrete instance of the TiqitBugView
# class, defined in this module. Implementations are usually provided by plugins
# and those plugins also participate in the decision process for selecting the
# active View for a given request.
#

from tiqit import *

__all__ = [
    'getBugViewFromArgs', 'getBugViewFromBugData',
    'getCloneBugViewFromBugData',
    'allBugViews', 'TiqitBugView',
    'loadBugViews',
    ]

class TiqitBugView(object):
    """
    A bug view. This class provides the default bug view, and can be sub-classed
    to override behaviour if desired.
    """

    _byname = {}
    def fromName(name):
        return TiqitBugView._byname[name]
    fromName = staticmethod(fromName)

    def __init__(self, name, displayname,
                 submittable=True,
                 bodyClass=''):
        self.name = name
        self.displayname = displayname

        self.submittable = submittable
        self.bodyClass = bodyClass

        TiqitBugView._byname[name] = self

    def initNewBug(self, cloneData):
        """
        Prepare the given cloneData and the meta data in the fields database
        for the display of the "newbug" page. This function must return a
        bug data object (either the given cloneData, or a modified/new one if
        desired).

        A usual technique here is to provide an OverriddenData object using the
        cloneData and additional default values.
        """
        return cloneData

    def getNewBugSections(self, project):
        """
        Get the sections to print on the new bug page for the given view.

        The return value must be a list of 3-tuples: short name, display name,
        format type. The format type is used to obtain the format string from
        the class data.
        """
        return []

    def getViewBugSections(self, data):
        """
        Get the sections to print on the view page for the given view.

        The return value must be a list of 3-tuples: short name, display name,
        format type. The format type is used to obtain the format string from
        the class data.
        """
        return []

    def prepareNewBug(self, fields):
        """
        Override/modify fields in a new bug submission. The given dictionary
        of field: value pairs can be modified if required (e.g. adding further
        defaults).
        """
        pass

    def doNewBug(self, newid, args):
        """
        Do any additional processing to the newly created bug. This can include
        adding default attachments, etc.
        """
        pass

    def prepareUpdateBug(self, changes, data):
        """
        Similar to prepareNewBug, but for later updates. The changes dictionary
        contains field: value pairs, while the data contains the current data
        for the bug.
        """
        pass

    def printDefaultValuesPrefsTable(self):
        """
        Print the HTML required for the default field values preferences in
        the "submit" section of the preferences page. The set of fields for
        which default values are supported is specific to each bug view.
        """
        pass

allBugViews = []

def loadBugViews():
    allBugViews.extend(plugins.loadBugViews())

    return allBugViews

class NoBugViewError(TiqitError):
    pass

def getBugViewFromArgs(args):
    candidates = plugins.getBugViewFromArgs(args)

    if candidates:
        return candidates[0]
    else:
        try:
            return TiqitBugView.fromName(args['bugtype'])
        except:
            raise NoBugViewError("No bug views for args %s" % args)

def getBugViewFromBugData(bugdata):
    candidates = plugins.getBugViewFromBugData(bugdata)

    if candidates:
        return candidates[0]
    else:
        raise NoBugViewError("No bug views for bug data")

def getCloneBugViewFromBugData(bugdata, overrides=None):
    candidates = plugins.getCloneBugViewFromBugData(bugdata, overrides=overrides)

    if candidates:
        return candidates[0]
    else:
        raise NoBugViewError("No bug views for bug data")

