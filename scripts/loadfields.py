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

