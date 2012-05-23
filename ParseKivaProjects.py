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

class ParseKivaProjects(xml.sax.handler.ContentHandler):

    def __init__(self):
        self.pick_id = 0
        self.in_image = 0
        self.in_country = 0
        self.in_name = 0
        self.approved_list = []
        self.project_image = {}
        self.project_name = {}
        self.project_country = {}
        self.temp_image = '' 
        self.temp_country = ''
        self.temp_name = ''

    def startElement(self, name, attributes):
        if name == 'id':
            self.pick_id = 1
        elif name == 'image':
            self.in_image = 1
        elif name == 'country':
            self.in_country = 1
        elif name == 'name':
            self.in_name = 1
    
    def characters(self, data):
        if self.pick_id == 1 and self.in_image == 1:
            self.temp_image = data
        elif self.pick_id == 1 and self.in_image == 0:
            self.approved_list.append(data)
            self.project_image[data] = self.temp_image
            self.project_country[data] = self.temp_country
            self.project_name[data] = self.temp_name
        elif self.in_country == 1:
            self.temp_country = data
        elif self.in_name == 1:
            self.temp_name = data

    def endElement(self, name):
        if name == 'id':
            self.pick_id = 0
        elif name == 'image':
            self.in_image = 0
        elif name == 'country':
            self.in_country = 0
        elif name == 'name':
            self.in_name = 0
        
    def getApprovedList(self):
        return self.approved_list
    
    def getProjectImage(self, id):
        return self.project_image[id]

    def getProjectName(self, id):
        return self.project_name[id]

    def getProjectCountry(self, id):
        return self.project_country[id]
