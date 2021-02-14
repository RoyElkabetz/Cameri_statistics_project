from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup


def find_spaces(my_string):
    # return all spaces indices in a string
    spaces_idx = []
    for idx, s in enumerate(my_string):
        if s == ' ':
            spaces_idx.append(idx)
    return spaces_idx


def strip_date(my_date):
    # strip the date and save it as a datetime.isoformat YYYY-MM-DD.
    date_dict = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'}
    date_iso = ''
    spaces = find_spaces(my_date)
    date_iso += my_date[spaces[1] + 1:]
    date_iso += '-'
    date_iso += date_dict[my_date[spaces[0] + 1:spaces[1]]]
    date_iso += '-'
    date_iso += my_date[:spaces[0]] if spaces[0] == 2 else '0' + my_date[:spaces[0]]
    return date_iso


def print_table(my_table):
    for singleRow in my_table:
        print(singleRow)



myUrl = 'http://www.israports.co.il/SiteAssets/Waves/haifaw-ipa.html'
names = ['Time-GMT', 'Hmax-meter', 'Hs-meter', 'H1/3-meter', 'Direction-deg',
         'Tav-sec', 'Tz-sec', 'Tp-sec', 'Temperature-C']

# opening up connections and grabbing the page
uClient = uReq(myUrl)
page_html = uClient.read()
uClient.close()

# html parsing
page_soup = soup(page_html, "html.parser")

centers = []
dates_iso = []
tables_data = []
all_data = []

for center in page_soup.body:
    centers.append(center)
i_old = 14
i_new = 4

dates = [centers[i_old].text.strip(),
         centers[i_new].text.strip()]

tables_raw = [centers[i_old + 6].findAll("tr", {"align": "CENTER"}),
              centers[i_new + 6].findAll("tr", {"align": "CENTER"})]

for date in dates:
    dates_iso.append(strip_date(date))

for k, table_data in enumerate(tables_raw):
    table = []
    for i, row in enumerate(table_data):
        if i == 0:
            continue
        line = row.findAll("font", {'face': "Arial"})
        row_values = []
        for tx in line:
            word = tx.text.strip()
            if word[2] == ':':
                row_values.append(dates_iso[k] + ' ' + word)
            else:
                row_values.append(word)
        table.append(row_values)
        all_data.append(row_values)
    tables_data.append(table)

#print_table(tables_data[0])
#print('\n')
#print_table(tables_data[1])
print_table(all_data)
