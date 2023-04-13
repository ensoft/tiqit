#!/usr/bin/python3

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import utils
import time

import tiqit

init_time = time.time()
def time_now():
    return time.time() - init_time

print("Initializing")
tiqit.initialise()

print(("{}: Reading old defaults".format(time_now())))
before = tiqit.defaults.getDict()
print(("{}: Updating defaults".format(time_now())))
tiqit.defaults.loadDefaultsFromBackend()
print(("{}: Reading new defaults".format(time_now())))
after = tiqit.defaults.getDict()

print(("{}: Calculating differences".format(time_now())))

diff = list(utils.dictDiff(before, after))
print("Added:")
for k, v in ((k, v[1]) for k, v in diff if v[0] is None):
    print(("    {}".format(((k, v),))))

print("Modified:")
for k, v in ((k, v) for k, v in diff if v[0] is not None and v[1] is not None):
    print(("    Old: {}".format(((k, v[0]),))))
    print(("    New: {}".format(((k, v[1]),))))

print("Removed:")
for k, v in ((k, v[0]) for k, v in diff if v[1] is None):
    print(("    {}".format(((k, v),))))

print(("{}: Done".format(time_now())))

