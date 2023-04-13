#!/usr/bin/python3

"""
Load field metadata and save it into a pickle DB, and Javascript.

Both the pickle DB (`tiqit.db`) and the Javascript (`fielddata.js`) contain the
same information. The pickle DB is used by server-side code, whereas the
Javascript is used in-browser.

"""

import argparse

import generatejs
import tiqit
import tiqit.database
import sys


def _save_fields(fields):
    # Before saving, we want to intern all the strings we can! This is to
    # reduce the size of tiqit.pickle.
    for f in fields:
        obj = fields[f]
        fields[sys.intern(f)] = obj
        obj.name = sys.intern(obj.name)
        obj.viewnames = list(map(sys.intern, obj.viewnames))
        obj.longname = sys.intern(obj.longname)
        obj.shortname = sys.intern(obj.shortname)
        obj.type = sys.intern(obj.type)
        obj.values = list(map(sys.intern, obj.values))
        obj.descs = list(map(sys.intern, obj.descs))
        obj._parentFields = list(map(sys.intern, obj._parentFields))
        obj._childFields = list(map(sys.intern, obj._childFields))
        mi = {}
        for m in obj._mandatoryIf:
            mi[sys.intern(m)] = list(map(sys.intern, obj._mandatoryIf[m]))
        obj._mandatoryIf = mi
        bi = {}
        for b in obj._bannedIf:
            bi[sys.intern(b)] = list(map(sys.intern, obj._bannedIf[b]))
        obj._bannedIf = bi
        obj.defaultsWith = tuple(map(sys.intern, obj.defaultsWith))
        obj.defaultsFor = list(map(sys.intern, obj.defaultsFor))
        ppfv = {}
        for p in obj._perParentFieldValues:
            ppfv[tuple(map(sys.intern, p))] = list(map(sys.intern, obj._perParentFieldValues[p]))
        obj._perParentFieldValues = ppfv

    tiqit.database.initialise()
    tiqit.database.set('tiqit.fields', fields)
    tiqit.database.commit()

def _main():
    tiqit.loadPlugins()

    # Parse the arguments, including those defined by plugins.
    parser = argparse.ArgumentParser(
        description='Populate local database with field meta-data')
    tiqit.plugins.add_load_fields_arguments(parser)
    args = parser.parse_args()

    # Have the plugins load fields.
    fields = tiqit.plugins.load_fields(args)

    # Write the data into the database, and fielddata.js.
    _save_fields(fields)
    generatejs.genEverything()


if __name__ == "__main__":
    _main()

