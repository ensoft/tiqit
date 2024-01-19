#!/usr/bin/python3
#
# Copyright (c) 2017 Ensoft Ltd, 2010 Martin Morrison
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

from tiqit import *
from backend import addNote

__all__ = [
    'prepareNewBug',
    'doNewBug',
    ]

_fullSummary = None

def prepareNewBug(fields):
    global _fullSummary
    # If the summary is too large, put it in a note
    if 'Summary' in fields and len(fields['Summary']) > 2000:
        fullsum = fields['Summary'].replace('\r\n', '\n')
        shortsum = fullsum[:1900]
        shortsum = shortsum[:shortsum.rfind('\n\n')]
        shortsum += """

Note: summary truncated. Full summary in 'Summary' enclosure."""

        fields['Summary'] = shortsum
        _fullSummary = fullsum

def doNewBug(newid, args):
    global _fullSummary
    if _fullSummary:
        addNote(newid, 'N-comments', 'Summary', _fullSummary)
        _fullSummary = None
