#!/usr/bin/python
# coding=utf8
#
# This file may be licensed under the terms of of the GNU General Public
# License Version 3 (the ``GPL'').
#
# Software distributed under the License is distributed # on an ``AS IS''
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the GPL
# for the specific language governing rights and limitations.
#
# You should have received a copy of the GPL along with this program. If not,
# go to http://www.gnu.org/licenses/gpl.html or write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

# Use simplejson if json not available (will make this work with Python 2.5)
try: 
    import json
except ImportError:
    import simplejson as json

# Regular imports
import random
import csv
import urllib2
from cookielib import CookieJar
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

    # Sort partners and get maximum score
    partners.sort(reverse=True, key=lambda x: x[1])
    max_score = partners[0][1]

    # Let's take the partners in the top 90% percentile
    approved_list = [x[0] for x in partners if x[1] >= int(max_score*0.9)]

    # The output will change every N hours (depending on the cron settings). 
    # Let's choose just a few partners and use them to search for loans
    # Only if there are many (> 10)
    if len(approved_list) > 10:
        chosen_partners = random.sample(approved_list, 10)
    else:
        chosen_partners = approved_list

    # Get 10 pages of data (200 loans)
    for i in range(1, 11):
        get_loans(chosen_partners, i, loans)

    loans = random.sample(loans, 70)

    # Get HTML data from file
    html_file = file('index_template.html')
    html_data = html_file.read()
    html_file.close()

    # Include loan data
    evenrow = False
    for loan in loans:
        html_data += generate_html(loan, evenrow)
        evenrow = not evenrow

    # Add time information and print (output should be redirected)
    now = datetime.utcnow()
    now = now.strftime('%d/%B/%Y @%H:%M UTC')

    html_data += '</table></div>\n<p class="update">Last update: '
    html_data += now + '</p>\n\n</body>\n</html>'

    # Print result to standard output
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

    # Build query URL
    q = 'http://api.kivaws.org/v1/' # Base URL
    q += 'loans/search.json?partner=' + ','.join(partners) # Partners list
    q += '&status=fundraising&page=' + str(page) # Fundraising + page
    q += '&sort_by=expiration' # Get loans close to expiration

    # Query API with given data and parse the JSON output
    json_loans = json.JSONDecoder().decode(urllib2.urlopen(q).read())

    # Get the needed data and store it in the result set
    for l in json_loans['loans']:
        result.add((l['id'], l['name'], l['loan_amount'], l['funded_amount'],
                    l['location']['country'], l['location']['country_code'],
                    l['activity']))

def generate_html(loan, evenrow):
    """Generates the HTML data for a given partner"""
    
    style = 'evenrow' if evenrow else 'oddrow'

    # Open row, include ID and link it to Kiva page
    data = '<tr class="' + style + '"><td><a href="http://www.kiva.org/lend/'
    data += str(loan[0]) + '">' + str(loan[0]) + '</a></td>'

    # Name
    data += '<td>' + loan[1].replace('&', '&amp;').encode('ascii', 'xmlcharrefreplace') \
            + '</td>'

    # Country
    # TODO: use flag image?
    data += '<td>' + loan[4].encode('ascii', 'xmlcharrefreplace') + '</td>'

    # Funding
    data += '<td>' + str(loan[3]) + '$/' + str(loan[2]) + '$</td>'

    # Activity and close row
    data += '<td>' + loan[-1].replace('&', '&amp;').encode('ascii', 'xmlcharrefreplace') \
            + '</td></tr>'

    return data

if __name__ == '__main__':
    main()

