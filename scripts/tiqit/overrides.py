#
# Copyright (c) 2017 Ensoft Ltd, 2024 Olli Johnson
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

"""
Provides utilities for interacting with the overrides to the tiqit DB defaults.
"""

import tiqit
import yaml
from fields import TiqitField
from pathlib import Path
from typing import Iterator

def get(field: TiqitField, value: str) -> dict[str, str]:
    parts = value.split("&")
    proj = parts[0]
    prod = parts[1]
    comp = parts[2]

    overrides_file = Path(tiqit.OVERRIDES_PATH) / (field.name + ".yaml")
    if not overrides_file.exists():
        return {}

    overrides = yaml.full_load(overrides_file.read_text())
    ret = {}
    wildcard_combos = [
        ("*", "*", comp),
        ("*", prod, comp),
        (proj, "*", comp),
        (proj, prod, comp)
    ]
    for prj, prd, cmpn in wildcard_combos:
        ret.update(overrides.get(prj, {}).get(prd, {}).get(cmpn, {}))
    return ret
