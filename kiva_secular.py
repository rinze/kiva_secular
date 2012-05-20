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

import urllib
import xml.sax.handler
import json

from ParseKivaPartners import ParseKivaPartners
from ParseKivaProjects import ParseKivaProjects
from datetime import datetime

__author__ = 'José María Mateos - chema@rinzewind.org'

def main():
	# Define variables
	approved_projects = []
	parsed_projects = []
	kiva_partners_url = 'http://api.kivaws.org/v1/partners.xml'

	# Get forbidden partners ids
	forbidden_mfi_list = getForbiddenList()

	parser = xml.sax.make_parser()
	handler = ParseKivaPartners(forbidden_mfi_list)
	parser.setContentHandler(handler)
	temp_sock = urllib.urlopen(kiva_partners_url)
	parser.parse(temp_sock)
	temp_sock.close()

	approved_list = handler.getApprovedList()
	str_approved_list = ','.join(approved_list)

	# New handler for loop below
	handler = ParseKivaProjects()
	parser.setContentHandler(handler)

	for page in range(1, 6):
	    query_projects_str = buildPartnerURL(str_approved_list, page)
	    temp_sock = urllib.urlopen(query_projects_str)
	    parser.parse(temp_sock)
	    temp_sock.close()

	approved_projects = handler.getApprovedList()

	html_data = """
	<html>
		<head>
			<title>Kiva Secular Loans</title>
			<link rel="stylesheet" rev="stylesheet" href="styles.css" type="text/css" media="all">
		</head>
		<body>
		<h1>Kiva Secular</h1>
		<p>Listed below you will find projects being funded by non-religious Kiva field 
		partners. This list has been generated using the information contained on the 
		<a href="http://atheist-monkey.blogspot.com/2009/08/kiva-mfi-checker.html#list">list compiled</a>
		by the <a href="http://www.kiva.org/community/teams/view?team_id=94">Kiva Lending Team 
		"Atheists, Agnostics, Skeptics, Freethinkers, Secular Humanists and the Non-Religious"</a></p>
		
		<p>You can find the code for the script used to generate this web page 
		<a href="https://github.com/rinze/kiva_secular/">in this Github</a>.</p>

		<p>This page is updated every 5 hours. Enjoy.</p>
		
		<div id="loanlist">
	"""
	for p in approved_projects:
		if p not in parsed_projects:
			parsed_projects.append(p)
			#html_data += '<SCRIPT type="text/javascript" src="http://www.kiva.org/banners/bannerBlock.php?busId='
			#html_data += id+'" language="javascript"></SCRIPT>\n'
			html_data += generateBlock(p)




	now = datetime.utcnow()
	now = now.strftime("%A, %d. %B %Y %I:%M%p")

	html_data += '</div>\n<p>Last updated: '
	html_data += now + '</p>\n\n</div>\n\n</body>\n</html>'

	print html_data	

def generateBlock(project_id):

	res = '<a href="http://www.kiva.org/lend/'+project_id+'">'
	res += 'Loan ' + project_id + '</a> '
	return res
	

def buildPartnerURL(partner_id, page):
	base_string = 'http://api.kivaws.org/v1/loans/search.xml?'
	base_string += 'status=fundraising'
	base_string += '&partner='+partner_id
	base_string += '&page='+str(page)
	base_string += '&sort_by=popularity'
	return base_string

def getForbiddenList():

	forbidden_mfi_list = []
	# TODO: change to new list
	religious_mfi_doc_url = 'http://spreadsheets.google.com/pub?key=ty2bXC4IvFg1ozCoPmsflUQ&single=true&gid=0&output=csv'

	temp_sock = urllib.urlopen(religious_mfi_doc_url)
	data = temp_sock.readlines()
	temp_sock.close()
	for line in data:
		mfi_code_list = line.split(',')
		temp_length = len(mfi_code_list)
		mfi_code = mfi_code_list[temp_length - 1].strip()
		if mfi_code != 'MFI ID':
			forbidden_mfi_list.append(mfi_code)
	
	return forbidden_mfi_list



if __name__ == '__main__':
	main()

