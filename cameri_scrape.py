from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import pandas as pd
import random
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

columns = ['TimeGMT', 'Hmax meter', 'Hs meter', 'H1/3 meter', 'Direction deg',
       'Tav sec', 'Tz sec', 'Tp sec', 'Temperature oC']


def open_html_connection(url):
    # opening up connections and grabbing the page
    u_client = uReq(url)
    page_html = u_client.read()
    u_client.close()
    return page_html


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


def pars_grab(html):
    # return a pandas dataFrame with the relevant data from the html
    page_soup = soup(html, "html.parser")

    centers = []
    dates_iso = []
    columns = []
    all_data = []
    i_old = 14
    i_new = 4

    for center in page_soup.body:
        centers.append(center)

    dates = [centers[i_old].text.strip(),
             centers[i_new].text.strip()]
    tables_raw = [centers[i_old + 6].findAll("tr", {"align": "CENTER"}),
                  centers[i_new + 6].findAll("tr", {"align": "CENTER"})]

    for date in dates:
        dates_iso.append(strip_date(date))

    for k, table_data in enumerate(tables_raw):
        table = []
        for i, row in enumerate(table_data):
            if i == 0 and k == 1:
                continue
            if i == 0 and k == 0:
                line = row.findAll("font", {'face': "Arial"})
                row_values = []
                for j, tx in enumerate(line):
                    word = tx.text.strip()
                    columns.append(word)
                continue
            line = row.findAll("font", {'face': "Arial"})
            row_values = []
            for j, tx in enumerate(line):
                word = tx.text.strip()
                if word == 'NA':
                    row_values.append('NULL')
                    continue
                if j == 0:
                    row_values.append(dates_iso[k] + ' ' + word + ':00')
                else:
                    row_values.append(word)
            table.append(row_values)
            all_data.append(row_values)
    return pd.DataFrame(all_data, columns=columns)


def get_last_date_from_csv(path_to_file):
    df = pd.read_csv(filepath_or_buffer=path_to_file, usecols=columns)
    return df['TimeGMT'].values[0]


def get_new_data_from_dataframe(last_date, df_new_data):
    idx = 0
    for row in df_new_data.iterrows():
        if row[1]['TimeGMT'] == last_date:
            idx = row[0]
            break
    return df_new_data[idx:]


def append_new_data(path_to_file, df_new_data):
    df_new_data.to_csv(path_or_buf=path_to_file, mode='a', header=False)
    pass


def update_last_line_of_csv(path_to_file, df):
    df_last = df.iloc[[-1]]
    df_last.to_csv(path_or_buf=path_to_file, columns=columns)
    pass


##################################### RUN #########################################
time.sleep(random.choice(range(60)))  # sleep 0-100 minutes randomly
PATH_haifa = '/Users/royelkabetz/Git/Cameri_statistics_project/data/haifa.csv'
PATH_LAST_haifa = '/Users/royelkabetz/Git/Cameri_statistics_project/data/haifa_last_row.csv'
PATH_ashdod = '/Users/royelkabetz/Git/Cameri_statistics_project/data/ashdod.csv'
PATH_LAST_ashdod = '/Users/royelkabetz/Git/Cameri_statistics_project/data/ashdod_last_row.csv'

# urls
url_haifa = 'https://www.israports.co.il//_layouts/15/wave/haifaw-ipa.html'
url_ashdod = 'https://www.israports.co.il//_layouts/15/wave/ashdodw-ipa.html'

# get data from Cameri Haifa
html = open_html_connection(url_haifa)
df = pars_grab(html)
last_date = get_last_date_from_csv(PATH_LAST_haifa)
df_new_data = get_new_data_from_dataframe(last_date, df)
append_new_data(PATH_haifa, df_new_data)
update_last_line_of_csv(PATH_LAST_haifa, df_new_data)

time.sleep(random.choice(range(60)))  # sleep 0-6 seconds randomly

# get data from Cameri Ashdod
html = open_html_connection(url_ashdod)
df = pars_grab(html)
last_date = get_last_date_from_csv(PATH_LAST_ashdod)
df_new_data = get_new_data_from_dataframe(last_date, df)
append_new_data(PATH_ashdod, df_new_data)
update_last_line_of_csv(PATH_LAST_ashdod, df_new_data)