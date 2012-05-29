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
import random
import csv
import urllib2
from cookielib import CookieJar

from ParseKivaProjects import ParseKivaProjects
from datetime import datetime

__author__ = 'José María Mateos - chema@rinzewind.org'

def main():
    # Define variables
    approved_projects = []
    parsed_projects = []

    # New list and new method for reading
    url = 'https://docs.google.com/spreadsheet/ccc?key=0AhfuHQgSfgERdDhUOW9jajFUSWFiang0eXVlSGI3YVE&authkey=CK36kZMN&hl=en&output=csv#gid=1'
    # Cookie management
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
    csv_data = csv.reader(opener.open(url))
    # Get rid of header
    csv_data.next()

    # Fields of interest:
    # 0 - ID
    # 4 - 'active' if working partner
    # 6 - Secular Rating
    # 9 - Social Rating
    partners = [(p[0], partner_score(p[6], p[9])) for p in csv_data
                if p[4] == 'active']

    # Get maximum possible score
    max_score = max([p[1] for p in partners])

    # TODO: Might need to rethink the whole score thing
    # Beware that partners is a variable previously used. 
    # Won't be necessary when this is complete, though.
    partners.sort(reverse=True, key=lambda x: x[1])

    # Let's take the partners in the top 90% percentile
    approved_list = [x[0] for x in partners if x[1] >= int(max_score*0.9)]
    str_approved_list = ','.join(approved_list)

    # The output will change every N hours (depending on the cron settings). 
    # Let's choose just a few partners and use them to search for loans
    # Only if there are many (> 10)
    if len(approved_list) > 10:
        chosen_partners = random.sample(approved_list, 10)
    else:
        chosen_partners = approved_list

    # TODO: use the chosen_partners variable to get new projects

    # New handler for loop below
    parser = xml.sax.make_parser()
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
        <a href="https://docs.google.com/spreadsheet/ccc?authkey=CK36kZMN&key=0AhfuHQgSfgERdDhUOW9jajFUSWFiang0eXVlSGI3YVE&hl=en&authkey=CK36kZMN#gid=0">list compiled</a>
        by the <a href="http://www.kiva.org/community/teams/view?team_id=94">Kiva Lending Team 
        "Atheists, Agnostics, Skeptics, Freethinkers, Secular Humanists and the Non-Religious"</a></p>
        
        <p>You can find the code for the script used to generate this web page 
        <a href="https://github.com/rinze/kiva_secular/">in Github</a>.</p>

        <div id="loanlist">
    """
    for p in approved_projects:
        if p not in parsed_projects:
            parsed_projects.append(p)
            #html_data += '<SCRIPT type="text/javascript" src="http://www.kiva.org/banners/bannerBlock.php?busId='
            #html_data += id+'" language="javascript"></SCRIPT>\n'
            html_data += generateBlock(p)

    now = datetime.utcnow()
    now = now.strftime('%d/%B/%Y @%H:%M')

    html_data += '</div>\n<p class="update">Last update: '
    html_data += now + '</p>\n\n</div>\n\n</body>\n</html>'

    print html_data 

def partner_score(secular, social):
    """Computes partner score. There are lots of Kiva partners with a high
    secular rating, so let's use the social rating as well in a weighted
    way."""
    secular = int(secular) if secular != '' else 0
    social = int(social) if social != '' else 0
    # No crappy partners
    if secular == 0 or social == 0: return 0
    else: return 2*secular + social

def generateBlock(project_id):
    """Generates the HTML data for a given partner.
    TODO: code improved version"""
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

if __name__ == '__main__':
    main()

