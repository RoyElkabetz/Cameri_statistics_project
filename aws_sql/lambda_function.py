from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import pymysql
import datetime


###################################################################################
#                                     UTILS                                       #
###################################################################################

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
    for single_row in my_table:
        print(single_row)


###################################################################################
#                          ESTABLISH HTML CONNECTION                              #
###################################################################################

def open_html_connection(url):
    # opening up connections and grabbing the page
    u_client = uReq(url)
    page_html = u_client.read()
    u_client.close()
    return page_html


def pars_grab(html):
    # html parsing
    page_soup = soup(html, "html.parser")

    centers = []
    dates_iso = []
    tables_data = []
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
            if i == 0:
                continue
            line = row.findAll("font", {'face': "Arial"})
            row_values = []
            for j, tx in enumerate(line):
                word = tx.text.strip()
                if j % 9 == 0:
                    row_values.append(dates_iso[k] + ' ' + word + ':00')
                elif word == 'NA':
                    row_values.append('NULL')
                else:
                    row_values.append(word)
            table.append(row_values)
            all_data.append(row_values)
        tables_data.append(table)
    return all_data


###################################################################################
#                                MYSQL FUNCTIONS                                  #
###################################################################################

def open_connection(endpoint, username, password, database_name):
    try:
        connection = pymysql.connect(host=endpoint, user=username, passwd=password, database=database_name)
        print("Connected to database")
        return connection
    except Exception as err:
        print("Unable to connect to the database: ", err)
        return


def close_connection(connection):
    try:
        connection.close()
        print("Disconnected from database.")
    except Exception as err:
        print("The was a problem in closing the connection: ", err)
        return


def get_cursor(connection):
    try:
        cursor = connection.cursor()
        return cursor
    except Exception as err:
        print("There was an error in getting a cursor: ", err)
        return


def get_last_datetime(cursor, instance='Haifa'):
    try:
        if instance == 'Haifa':
            sql = 'SELECT MAX(date_n_time_GMT) FROM Haifa'
        if instance == 'Ashdod':
            sql = 'SELECT MAX(date_n_time_GMT) FROM Ashdod'
        cursor.execute(sql)
        return cursor.fetchone()[0]
    except Exception as err:
        print("There was an error at the execution stage: ", err)
        return


def insert_row(cursor, row, instance='Haifa'):
    try:
        if instance == 'Haifa':
            sql = "INSERT INTO Haifa VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})".format(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
            )
        if instance == 'Ashdod':
            sql = "INSERT INTO Ashdod VALUES ('{0}', {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})".format(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
            )
        cursor.execute(sql)
        return
    except Exception as err:
        print('There was a problem with the insert execution: ', err)
        return


def find_last(db_lastDatetime, new_data):
    for i, row in enumerate(new_data):
        YYYY = int(row[0][0:4])
        MM = int(row[0][5:7])
        DD = int(row[0][8:10])
        hh = int(row[0][11:13])
        mm = int(row[0][14:16])
        ss = int(row[0][17:19])
        if db_lastDatetime == datetime.datetime(YYYY, MM, DD, hh, mm, ss):
            return i
    return -1


def insert_new_data_to_db(connection, cursor, new_data, idx, instance='Haifa'):
    if idx == -1:
        for i, row in enumerate(new_data):
            insert_row(cursor, row, instance=instance)
    else:
        for i in range(idx + 1, len(new_data)):
            insert_row(cursor, new_data[i], instance=instance)
    connection.commit()
    return


def update_database(instance, connection, cursor):
    # urls
    url = ''
    if instance == 'Haifa':
        # url = 'http://www.israports.co.il/SiteAssets/Waves/haifaw-ipa.html'
        url = 'https://www.israports.co.il//_layouts/15/wave/haifaw-ipa.html'
    if instance == 'Ashdod':
        # url = 'http://www.israports.co.il/SiteAssets/Waves/ashdodw-ipa.html'
        url = 'https://www.israports.co.il//_layouts/15/wave/ashdodw-ipa.html'
    # get data from Haifa / Ashdod site
    html = open_html_connection(url)
    try:
        data = pars_grab(html)
    except Exception as err:
        print('Fail in parsing and arranging the data from {0} site: {1}'.format(instance, err))
        return

    # compare last datetime in database to datetime in instance html
    last_datetime = get_last_datetime(cursor, instance=instance)
    idx = find_last(last_datetime, data)
    insert_new_data_to_db(connection, cursor, data, idx, instance=instance)
    if idx == -1:
        print('Insert {0} new rows into the {1} table.'.format(len(data), instance))
    else:
        print('Insert {0} new rows into the {1} table.'.format(len(data) - idx - 1, instance))


###################################################################################
#                                      MAIN                                       #
###################################################################################

# configuration values
my_endpoint = 'waves-measurements.cdkyy60n2u7f.us-east-2.rds.amazonaws.com'
my_username = 'admin'
my_password = 'Portugal2018'
my_database_name = 'Waves'


def lambda_handler(event, context):
    # open database connection
    connection = open_connection(endpoint=my_endpoint,
                                 username=my_username,
                                 password=my_password,
                                 database_name=my_database_name)

    # get cursor
    cursor = get_cursor(connection)

    # update database
    update_database(instance='Haifa', connection=connection, cursor=cursor)
    update_database(instance='Ashdod', connection=connection, cursor=cursor)

    # close connection
    close_connection(connection)

# lambda_handler(1, 1)




