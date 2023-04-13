#
# Copyright (c) 2017 Ensoft Ltd, 2014 Martin Morrison
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
Built-in plugin to define a base (default) class and bugview.
"""

from tiqit import *
from frontend.views import TiqitBugView
from fields import TiqitField

class BaseView(TiqitBugView):
	def getNewBugSections(self, project):
		return [
		    ('General', 'General Information', 'new'),
		]

	def getViewBugSections(self, project):
		return [
		    ('General', 'General Information', 'general'),
		    ('Extra', 'Extra Information', 'extras'),
		]

def loadBugViews():
	return [BaseView('bug', 'Bug')]

def load_data_defaults(key):
	print("Loading data defaults for", key)
	prefix = list(Config().section('backends').items())[0][0]
	if key == 'tiqit.classes':
		database.set('tiqit.classes', [prefix + '.default'])
	elif key == 'tiqit.projmap':
		database.set('tiqit.projmap',
			         {prefix + '.default': prefix + '.default'})
	elif key == 'tiqit.fields':
		database.set('tiqit.fields', {
			'Identifier': TiqitField("Identifier", "Identifier",
				("Identifier", "Headline"), "Identifier", "Identifier",
				"DefectID", 0, 0, True),
			'Status': TiqitField("Status", "Status", ("Status",), "Status", "St",
				"Text", 0, 0, True),
			'Component': None,
			'Severity': None,
			'Headline': None,
			'Summary': None,
			'Project': None,
			})
