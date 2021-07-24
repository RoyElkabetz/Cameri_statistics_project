from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import pandas as pd
import random
from datetime import date
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

columns = ['TimeGMT', 'Hmax meter', 'Hs meter', 'H1/3 meter', 'Direction deg',
       'Tav sec', 'Tz sec', 'Tp sec', 'Temperature oC']


class Logger:
    def __init__(self, path_to_log='/Users/royelkabetz/Git/Cameri_statistics_project/scraping_log.txt'):
        self.path_to_log = path_to_log
        self.log_file = open(path_to_log, "a")
        self.log_file.write(f"Date: {str(date.today())}\n")

    def write_to_log(self, text):
        self.log_file.write(text + "\n")

    def close_log(self):
        self.log_file.close()


def open_html_connection(url, logger=None):
    # opening up connections and grabbing the page
    try:
        u_client = uReq(url)
        page_html = u_client.read()
        u_client.close()
        if logger is not None:
            logger.write_to_log("Html connection established.")
        return page_html
    except:
        if logger is not None:
            logger.write_to_log("There was a problem in html connection.")
        return


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


def pars_grab(html, logger=None):
    # return a pandas dataFrame with the relevant data from the html
    try:
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
        if logger is not None:
            logger.write_to_log("Html was successfully parsed.")
        return pd.DataFrame(all_data, columns=columns)
    except:
        if logger is not None:
            logger.write_to_log("There was a problem in html parsing process.")
        return


def get_last_date_from_csv(path_to_file, logger=None):
    try:
        df = pd.read_csv(filepath_or_buffer=path_to_file, usecols=columns)
        if logger is not None:
            logger.write_to_log("Got last measurement date.")
        return df['TimeGMT'].values[0]
    except:
        if logger is not None:
            logger.write_to_log("Could not collect last measurement date.\n")
        return



def get_new_data_from_dataframe(last_date, df_new_data, logger=None):
    try:
        idx = 0
        for row in df_new_data.iterrows():
            if row[1]['TimeGMT'] == last_date:
                idx = row[0]
                break
        if logger is not None:
            logger.write_to_log("Got new waves data.")
        return df_new_data[idx:]
    except:
        if logger is not None:
            logger.write_to_log("There was a problem in computing new data.")
        return


def append_new_data(path_to_file, df_new_data, logger=None):
    try:
        df_new_data.to_csv(path_or_buf=path_to_file, mode='a', header=False)
        if logger is not None:
            logger.write_to_log("New data appended to CSV.")
        pass
    except:
        if logger is not None:
            logger.write_to_log("There was a problem in appending new data to CSV.")
        pass


def update_last_line_of_csv(path_to_file, df, logger=None):
    try:
        df_last = df.iloc[[-1]]
        df_last.to_csv(path_or_buf=path_to_file, columns=columns)
        if logger is not None:
            logger.write_to_log("Last measurement was updated.")
        pass
    except:
        if logger is not None:
            logger.write_to_log("There was a problem in Last measurement updating.")
        pass


##################################### RUN #########################################


logger = Logger()
time.sleep(random.choice(range(6)))  # sleep 0-100 minutes randomly
PATH_haifa = '/Users/royelkabetz/Git/Cameri_statistics_project/data/haifa.csv'
PATH_LAST_haifa = '/Users/royelkabetz/Git/Cameri_statistics_project/data/haifa_last_row.csv'
PATH_ashdod = '/Users/royelkabetz/Git/Cameri_statistics_project/data/ashdod.csv'
PATH_LAST_ashdod = '/Users/royelkabetz/Git/Cameri_statistics_project/data/ashdod_last_row.csv'

# urls
url_haifa = 'https://www.israports.co.il//_layouts/15/wave/haifaw-ipa.html'
url_ashdod = 'https://www.israports.co.il//_layouts/15/wave/ashdodw-ipa.html'

# get data from Cameri Haifa
logger.write_to_log('HAIFA:')
html = open_html_connection(url_haifa, logger)
df = pars_grab(html, logger)
last_date = get_last_date_from_csv(PATH_LAST_haifa, logger)
df_new_data = get_new_data_from_dataframe(last_date, df, logger)
append_new_data(PATH_haifa, df_new_data, logger)
update_last_line_of_csv(PATH_LAST_haifa, df_new_data, logger)


time.sleep(random.choice(range(6)))  # sleep 0-6 seconds randomly

# get data from Cameri Ashdod
logger.write_to_log('ASHDOD:')
html = open_html_connection(url_ashdod, logger)
df = pars_grab(html, logger)
last_date = get_last_date_from_csv(PATH_LAST_ashdod, logger)
df_new_data = get_new_data_from_dataframe(last_date, df, logger)
append_new_data(PATH_ashdod, df_new_data, logger)
update_last_line_of_csv(PATH_LAST_ashdod, df_new_data, logger)
logger.close_log()
