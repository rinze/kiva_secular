#!/usr/bin/python
# coding=utf8
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 3 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import xml.sax.handler

__author__ = 'José María Mateos - chema@rinzewind.org'

class ParseKivaPartners(xml.sax.handler.ContentHandler):

        def __init__(self, forbidden_mfi_list):
                self.forbidden_mfi_list = forbidden_mfi_list
		self.pick_id = 0
		self.in_image = 0
		self.approved_list = []

        def startElement(self, name, attributes):
                if name == 'id':
			self.pick_id = 1
		elif name == 'image':
			self.in_image = 1
	
	def characters(self, data):
		if self.pick_id == 1 and self.in_image == 0:
			if data not in self.forbidden_mfi_list and data not in self.approved_list:
				self.approved_list.append(data)

	def endElement(self, name):
		if name == 'id':
			self.pick_id = 0
		elif name == 'image':
			self.in_image = 0
		
	def getApprovedList(self):
		return self.approved_list
