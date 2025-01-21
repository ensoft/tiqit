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

import logging
import tiqit
import yaml
from fields import TiqitField
from pathlib import Path
from typing import Union

_logger = logging.getLogger()

CompOverridesDict = dict[str, Union[str, list[str]]]

_OverridesDict = dict[
    # Project
    str,
    dict[
        # Product
        str,
        dict[
            # Component
            str,
            CompOverridesDict,
        ],
    ],
]


def _load_overrides(field: TiqitField) -> _OverridesDict:
    overrides_file = Path(tiqit.OVERRIDES_PATH) / (field.name + ".yaml")
    if not overrides_file.exists():
        return {}

    overrides = yaml.full_load(overrides_file.read_text())
    if not isinstance(overrides, dict):
        _logger.warning("Overrides YAML file loaded is not a dict. Ignoring.")
        overrides = {}
    for proj, proj_value in overrides.items():
        # Verify the value is a valid dict of product overrides
        if not isinstance(proj_value, dict):
            _logger.warning("Overrides entry for %s is not a dict. Ignoring.", proj)
            overrides[proj] = {}
            continue

        for prod, prod_value in proj_value.items():
            # Verify the value is a valid dict of component overrides
            if not isinstance(prod_value, dict):
                _logger.warning(
                    "Overrides entry for %s -> %s is not a dict. Ignoring.", proj, prod
                )
                overrides[proj][prod] = {}
                continue

            for comp, comp_value in prod_value.items():
                # Verify the value is a valid dict of overrides
                if not isinstance(comp_value, dict):
                    _logger.warning(
                        "Overrides entry for %s -> %s -> %s is not a dict. Ignoring.",
                        proj,
                        prod,
                        comp,
                    )
                    overrides[proj][prod][comp] = {}
                    continue

                # Verify each of the override entries is of valid type
                for field, f_value in comp_value.copy().items():
                    if field == "keywords":
                        if not isinstance(f_value, list) or not all(
                            isinstance(s, str) for s in f_value
                        ):
                            _logger.warning(
                                "Overrides entry for %s -> %s -> %s -> keywords is not a valid list of strings. Ignoring.",
                                proj,
                                prod,
                                comp,
                            )
                            del overrides[proj][prod][comp]["keywords"]
                            continue
                    else:
                        if not isinstance(f_value, str):
                            _logger.warning(
                                "Overrides entry for %s -> %s -> %s -> %s is not a valid string. Ignoring.",
                                proj,
                                prod,
                                comp,
                                field,
                            )
                            del overrides[proj][prod][comp][field]
                            continue

    return overrides


def get(field: TiqitField, value: str) -> dict[str, Union[str, list[str]]]:
    overrides = _load_overrides(field)

    parts = value.split("&")
    proj = parts[0]
    prod = parts[1]
    comp = parts[2]

    ret = {}
    wildcard_combos = [
        ("*", "*", comp),
        ("*", prod, comp),
        (proj, "*", comp),
        (proj, prod, comp),
    ]
    for prj, prd, cmpn in wildcard_combos:
        ret.update(overrides.get(prj, {}).get(prd, {}).get(cmpn, {}))
    return ret
