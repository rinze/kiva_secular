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
    
import json
import random
import csv
import urllib2
from cookielib import CookieJar

from ParseKivaProjects import ParseKivaProjects
from datetime import datetime

__author__ = 'José María Mateos - chema@rinzewind.org'

def main():

    # Tuples of loan data will be added to this set
    loans = set()

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

    # Get maximum possible score and sort my partners
    max_score = max([p[1] for p in partners])
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

    # Get 5 pages of data (100 loans)
    for i in range(1, 6):
        get_loans(chosen_partners, i, loans)

    # Finally: get 30 loans from all obtained in the search
    # Is this sampling really useful?
    loans = random.sample(loans, 30)

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
    for l in loans:
        html_data += generateBlock(l)

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
    if secular == 0 or social == 0: return 0
    else: return 2*secular + social

def get_loans(partners, page, result):
    """Adds a tuple of loan data to results set starting from a 
       list of partners"""

    # Kiva base URL for API queries
    kb = 'http://api.kivaws.org/v1/'
    q = kb + 'loans/search.json?partner=' + ','.join(partners)
    q = q + '&status=fundraising&page=' + str(page)

    # Query API with given data and parse the JSON output
    json_loans = json.JSONDecoder().decode(urllib2.urlopen(q).read())

    # Get the needed data and store it in the result set
    for l in json_loans['loans']:
        result.add((l['id'], l['name'], l['loan_amount'], l['funded_amount'],
                    l['location']['country'], l['location']['country_code'],
                    l['activity']))

def generateBlock(loan):
    """Generates the HTML data for a given partner.
    TODO: code improved version"""

    res = '<a href="http://www.kiva.org/lend/' + str(loan[0]) + '">'
    res += 'Loan ' + str(loan[0]) + '</a> '
    return res

if __name__ == '__main__':
    main()

