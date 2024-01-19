#!/usr/bin/python3


"""
Load class metadata and save it into a pickle DB.

"""


import argparse

import tiqit
import tiqit.database


def _main():
    tiqit.loadPlugins()

    # Parse the arguments, including those defined by plugins.
    parser = argparse.ArgumentParser(
        description='Populate local database with class meta-data')
    tiqit.plugins.add_load_classes_arguments(parser)
    args = parser.parse_args()

    # Have the plugins load class information, and combine the results.
    plugin_output = tiqit.plugins.load_classes(args)

    classes = set()
    projmap = {}
    other = {}
    for plugin_classes, plugin_projects, plugin_other in plugin_output:
        classes.update(plugin_classes)
        projmap.update(plugin_projects)
        other.update(plugin_other)

    # Update the database and commit.
    tiqit.database.initialise()
    tiqit.database.set('tiqit.classes', classes)
    tiqit.database.set('tiqit.projmap', projmap)
    for key, val in other.items():
        tiqit.database.set(key, val)
    tiqit.database.commit()


if __name__ == "__main__":
    _main()

