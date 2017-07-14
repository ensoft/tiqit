#!/usr/bin/python

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


def _save_fields(fields):
    # Before saving, we want to intern all the strings we can! This is to
    # reduce the size of tiqit.pickle.
    for f in fields:
        obj = fields[f]
        fields[intern(f)] = obj
        obj.name = intern(obj.name)
        obj.viewnames = map(intern, obj.viewnames)
        obj.longname = intern(obj.longname)
        obj.shortname = intern(obj.shortname)
        obj.type = intern(obj.type)
        obj.values = map(intern, obj.values)
        obj.descs = map(intern, obj.descs)
        obj._parentFields = map(intern, obj._parentFields)
        obj._childFields = map(intern, obj._childFields)
        mi = {}
        for m in obj._mandatoryIf:
            mi[intern(m)] = map(intern, obj._mandatoryIf[m])
        obj._mandatoryIf = mi
        bi = {}
        for b in obj._bannedIf:
            bi[intern(b)] = map(intern, obj._bannedIf[b])
        obj._bannedIf = bi
        obj.defaultsWith = tuple(map(intern, obj.defaultsWith))
        obj.defaultsFor = map(intern, obj.defaultsFor)
        ppfv = {}
        for p in obj._perParentFieldValues:
            ppfv[tuple(map(intern, p))] = map(intern, obj._perParentFieldValues[p])
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

