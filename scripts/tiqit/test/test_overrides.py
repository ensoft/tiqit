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

"""Test the tiqit overrides module."""

import pytest
import tiqit
import tempfile
import yaml
from dataclasses import dataclass
from pathlib import Path
from tiqit import overrides
from fields import TiqitField
from typing import Any, Iterator
from unittest import mock

_STUB_OVERRIDES = {
    "tiqit_test_proj": {
        "tiqit_test_prod": {
            "test_comp_no_wildcard": {"Manager": "test_manager_no_wildcard"}
        },
        "*": {"test_comp_wildcard_prod": {"Manager": "test_manager_wildcard_prod"}},
    },
    "*": {
        "tiqit_test_prod": {
            "test_comp_wildcard_proj": {"Manager": "test_manager_wildcard_proj"}
        },
        "*": {"test_comp_wildcard_both": {"Manager": "test_manager_wildcard_both"}},
    },
}


@pytest.fixture
def mock_overrides_path() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmpdir:
        with mock.patch.object(tiqit, "OVERRIDES_PATH", tmpdir):
            yield Path(tmpdir)


@pytest.fixture
def populated_mock_overrides_path(mock_overrides_path: Path) -> Iterator[Path]:
    tmppath = mock_overrides_path / "field.yaml"
    tmppath.write_text(yaml.safe_dump(_STUB_OVERRIDES))
    yield mock_overrides_path


@pytest.fixture
def mock_field() -> TiqitField:
    """Stub TiqitField object for testing in this file."""
    ret = mock.Mock()
    # Note: mock.Mock has special handling for the "name" arg, so to set the
    # mock property called "name" we have to do it outside of the constructor.
    ret.name = "field"
    return ret


@pytest.mark.parametrize(
    "testcase, expected_manager",
    [
        (
            ("tiqit_test_proj", "tiqit_test_prod", "test_comp_no_wildcard"),
            "test_manager_no_wildcard",
        ),
        (
            ("tiqit_test_proj", "tiqit_test_prod", "test_comp_wildcard_prod"),
            "test_manager_wildcard_prod",
        ),
        (
            ("tiqit_test_proj", "tiqit_test_prod", "test_comp_wildcard_proj"),
            "test_manager_wildcard_proj",
        ),
        (
            ("tiqit_test_proj", "tiqit_test_prod", "test_comp_wildcard_both"),
            "test_manager_wildcard_both",
        ),
    ],
)
def test_get_overrides(
    testcase: tuple[str, str, str],
    expected_manager: str,
    populated_mock_overrides_path: Path,
    mock_field: TiqitField,
) -> None:
    """Test the overrides are read correctly, including the use of wildcards."""
    actual = overrides.get(mock_field, "&".join(testcase))
    assert actual.get("Manager") == expected_manager


def test_no_overrides(mock_overrides_path: Path, mock_field: TiqitField) -> None:
    """Test the handling when the overrides file is not found."""
    actual = overrides.get(
        mock_field, "tiqit_test_proj&tiqit_test_prod&test_comp_no_wildcard"
    )
    assert actual == {}


@dataclass
class InvalidOverridesTestcase:
    name: str
    input_dict: Any
    expected_output: overrides._OverridesDict


INVALID_OVERRIDES_TESTCASES = [
    InvalidOverridesTestcase(
        "top_level_invalid",
        ["NOT A DICT"],
        {},
    ),
    InvalidOverridesTestcase(
        "invalid_proj",
        {
            "invalid_proj": "not a dict",
            "valid_proj": {"prod": {"comp": {"manager": "bert"}}},
        },
        {
            "invalid_proj": {},
            "valid_proj": {"prod": {"comp": {"manager": "bert"}}},
        },
    ),
    InvalidOverridesTestcase(
        "invalid_prod",
        {
            "proj": {
                "invalid_prod": "not a dict",
                "valid_prod": {"comp": {"manager": "bert"}},
            }
        },
        {
            "proj": {
                "invalid_prod": {},
                "valid_prod": {"comp": {"manager": "bert"}},
            }
        },
    ),
    InvalidOverridesTestcase(
        "invalid_comp",
        {
            "proj": {
                "prod": {
                    "invalid_comp": "not a dict",
                    "valid_comp": {"manager": "bert"},
                },
            }
        },
        {
            "proj": {
                "prod": {
                    "invalid_comp": {},
                    "valid_comp": {"manager": "bert"},
                }
            }
        },
    ),
    InvalidOverridesTestcase(
        "invalid_overrides",
        {
            "proj": {
                "prod": {
                    "compA": {
                        "somefield": "somevalue",
                        "keywords": "INVALID - not a list",
                    },
                    "compB": {
                        "somefield": "somevalue",
                        "keywords": ["VALID", "LIST"],
                    },
                    "compC": {
                        "somefield": "somevalue",
                        "keywords": ["INVALID", 2, 3, 4, "LIST"],
                    },
                    "compD": {
                        "somefield": "somevalue",
                        "badfield": 1234,
                    },
                }
            }
        },
        {
            "proj": {
                "prod": {
                    "compA": {"somefield": "somevalue"},
                    "compB": {
                        "somefield": "somevalue",
                        "keywords": ["VALID", "LIST"],
                    },
                    "compC": {"somefield": "somevalue"},
                    "compD": {"somefield": "somevalue"},
                }
            }
        },
    ),
]


@pytest.mark.parametrize(
    "testcase",
    INVALID_OVERRIDES_TESTCASES,
    ids=[x.name for x in INVALID_OVERRIDES_TESTCASES],
)
def test_invalid_overrides(
    testcase: InvalidOverridesTestcase,
    mock_overrides_path: Path,
    mock_field: TiqitField,
) -> None:
    tmppath = mock_overrides_path / (mock_field.name + ".yaml")
    tmppath.write_text(yaml.safe_dump(testcase.input_dict))
    actual = overrides._load_overrides(mock_field)
    assert actual == testcase.expected_output
