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

from ParseKivaPartners import ParseKivaPartners
from ParseKivaProjects import ParseKivaProjects
from datetime import datetime

__author__ = 'José María Mateos - chema@rinzewind.org'
app_id = 'org.rinzewind.kiva_secular.testing'

def main():
	forbidden_mfi_list = []
	approved_projects = []
	parsed_projects = []

	global app_id

	religious_mfi_doc_url = 'http://spreadsheets.google.com/pub?key=ty2bXC4IvFg1ozCoPmsflUQ&single=true&gid=0&output=csv'
	kiva_partners_url = 'http://api.kivaws.org/v1/partners.xml?app_id='+app_id

	temp_sock = urllib.urlopen(religious_mfi_doc_url)
	data = temp_sock.readlines()
	temp_sock.close()
	for line in data:
		mfi_code_list = line.split(',')
		temp_length = len(mfi_code_list)
		mfi_code = mfi_code_list[temp_length - 1].strip()
		if mfi_code != 'MFI ID':
			forbidden_mfi_list.append(mfi_code)

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
		<a href="http://code.google.com/p/kivasecular">in this Google Code Project</a>.</p>

		<p>This page is updated every 5 hours. Enjoy.</p>
		
		<div id="loanlist">
	"""
	for id in approved_projects:
		if id not in parsed_projects:
			parsed_projects.append(id)
			#debug_string = "Processed project: " + id
			#print debug_string
			html_data += '<SCRIPT type="text/javascript" src="http://www.kiva.org/banners/bannerBlock.php?busId='
			html_data += id+'" language="javascript"></SCRIPT>\n'
			#html_data += generateBlock(id, handler)


	now = datetime.utcnow()
	now = now.strftime("%A, %d. %B %Y %I:%M%p")

	html_data += '\n<p>Last updated: ' + now + '</p>\n\n</div>\n\n</body>\n</html>'

	print html_data	

def generateBlock(project_id, handler):
	
	block_text = """
	<div style="border: 1px solid gray;width: 260px;height: 170px;margin: 0;padding: 0;background-color: #fff;">
	<table height="170" width="260"  style="margin:0px; padding: 0; background-color:#fff;"><tr>
	<td style="text-align: center;" width="130" height="105">
	<a  href="http://www.kiva.org/lend/PROJECTID?utm_source=viralbanner&amp;utm_medium=viral&amp;utm_content=block260x170&amp;utm_campaign=banner" target="_blank" >
	<img  border="0" src="http://s3-1.kiva.org/img/w125h100/PROJECTIMAGE.jpg" style="margin: 0px; border:1px solid gray; text-align:center;" /></a>
	</td><td valign="top" style="font-size:16px;font-family:  Helvetica,Arial,sans-serif;color:#060;font-weight:bold;line-height:1.4;text-align: center;" >
	Make&nbsp;a&nbsp;loan<br/>Change&nbsp;a&nbsp;life<br/>
	<a href="http://www.kiva.org/lend/PROJECTID?utm_source=viralbanner&utm_medium=viral&utm_content=block260x170&utm_campaign=banner" target="_blank">
	<img src="http://l3-1.kiva.org/r22581/images/bannersmall.png"width="95" height="45" alt="Kiva logo"
	title="Kiva - loans that change lives" border="0" align="bottom" style="margin: 0px;" />
	</a></td></tr><tr><td style="text-align:left;padding-left:5px;padding-bottom:5px;font-size:12px;font-family: Helvetica,Arial,sans-serif;color:#060;font-weight:normal;line-height:1.4;">Name:     <a style="color:#00c;" href="http://www.kiva.org/lend/PROJECTID?utm_source=viralbanner&utm_medium=viral&utm_content=block260x170&utm_campaign=banner" target="_blank">Mom Chea</a> <br/>Location: <a style="color:#00c;" href="http://www.kiva.org/lend/PROJECTID?utm_source=viralbanner&utm_medium=viral&utm_content=block260x170&utm_campaign=banner" target="_blank">Cambodia</a></td><td style="text-align: center;margin-bottom:5px;font-size:10px;font-family:  Helvetica,Arial,sans-serif;color:#006600;font-weight:normal;line-height:1.4;">Loan&nbsp;Needed:&nbsp;$1,200<table height="15" style="border:1px solid black;"><tr><td width="96" style="background-color:#f00;"></td><td width="4" style="background-color:#eee"></td></tr></table>96 % funded</td></tr></table></div>
	"""

	block_text = block_text.replace('PROJECTID', project_id)
	block_text = block_text.replace('PROJECTIMAGE', handler.getProjectImage(id))

	return(block_text)

def buildPartnerURL(partner_id, page):
	global app_id
	base_string = 'http://api.kivaws.org/v1/loans/search.xml?'
	base_string += 'status=fundraising'
	base_string += '&partner='+partner_id
	base_string += '&page='+str(page)
	base_string += '&sort_by=popularity'
	base_string += '&app_id='+str(app_id)
	return base_string


if __name__ == '__main__':
	main()

