from model import *
import sqlite3
from eventClass import *

# initiate database
conn = sqlite3.connect('meetup.sqlite')

cur = conn.cursor()

def db_initialize_tables():
    conn = sqlite3.connect('meetup.sqlite')
    cur = conn.cursor()
    # Drop tables
    statement = '''
        DROP TABLE IF EXISTS 'Participants';
        DROP TABLE IF EXISTS 'InterestsOfPaticipants';
    '''
    cur.executescript(statement)

    # Create tables
    statement = '''
        CREATE TABLE IF NOT EXISTS 'Categories'(
            'Id'                      INTEGER PRIMARY KEY AUTOINCREMENT,
            'CategoryName'            TEXT NOT NULL,
            'CategoryId'              INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS 'Zipcodes' (
            'Id'                      INTEGER PRIMARY KEY AUTOINCREMENT,
            'Zipcode'                 INTEGER NOT NULL,
            'CityName'                TEXT NOT NULL,
            'StateName'               TEXT NOT NULL,
            'Lat'                     FLOAT NOT NULL,
            'Lon'                     FLOAT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS 'Events' (
            'Id'                      INTEGER PRIMARY KEY AUTOINCREMENT,
            'EventName'               TEXT NOT NULL,
            'CategoryId'              INTEGER NOT NULL,
            'Zipcode'                 INTEGER,
            'Address'                 TEXT,
            'City'                    TEXT NOT NULL,
            'State'                   TEXT NOT NULL,
            'Date'                    TEXT,
            'Time'                    TEXT,
            'Lat'                     FLOAT,
            'Lon'                     FLOAT,
            'Link'                    TEXT NOT NULL
        );
    '''
    #     CREATE TABLE 'Participants' (
    #         'Id'                      INTEGER PRIMARY KEY AUTOINCREMENT,
    #         'City'                    TEXT,
    #         'State'                   TEXT,
    #         'EventId'                 INTEGER NOT NULL
    #     );
    #
    #     CREATE TABLE 'InterestsOfPaticipants' (
    #         'Id'                      TEXT NOT NULL,/* ParticipantId/Interest */
    #         'ParticipantId'           INTEGER NOT NULL,
    #         'Interest'                TEXT NOT NULL
    #     );
    # '''
    cur.executescript(statement)
    conn.close()

# Insert data into 'Categories'
def db_insert_categories():
    if not has_categories():
        conn = sqlite3.connect('meetup.sqlite')
        cur = conn.cursor()
        categories_json = get_categories()
        for each_category in categories_json:
            statement = '''
                INSERT INTO Categories (CategoryName, CategoryId)
                VALUES (?, ?)
            '''
            params_s = (each_category['name'], each_category['id'])
            cur.execute(statement, params_s)
        conn.commit()
        conn.close()


def print_categories():
    conn = sqlite3.connect('meetup.sqlite')
    cur = conn.cursor()
    statement_see_categories = '''
        SELECT CategoryName
        FROM Categories
    '''
    cur.execute(statement_see_categories)
    list_categories = cur.fetchall()
    print('\n*********** ALL THEMES ***********')
    count = 1
    for each in list_categories:
        print_ordered_list_item(count, each[0])
        count += 1
    conn.close()
    return list_categories

def flask_get_categories():
    conn = sqlite3.connect('meetup.sqlite')
    cur = conn.cursor()
    statement_see_categories = '''
        SELECT CategoryName
        FROM Categories
    '''
    cur.execute(statement_see_categories)
    list_categories = cur.fetchall()
    conn.close()
    return list_categories

#insert zipcode
def db_insert_zipcode(zip_code):
    # conn_z = sqlite3.connect('meetup.sqlite')
    # cur_z = conn_z.cursor()
    if not has_zip(zip_code):
        zipcodes_json = get_zipcode(zip_code)
        if zipcodes_json != None:
            statement = '''
                INSERT INTO Zipcodes (Zipcode, CityName, StateName, Lat, Lon)
                VALUES (?, ?, ?, ?, ?)
            '''
            try:
                params_s = (zip_code, zipcodes_json['city'], zipcodes_json['state'], zipcodes_json['lat'], zipcodes_json['lng'])
                cur.execute(statement, params_s)
                conn.commit()
                latLon = [zipcodes_json['lat'], zipcodes_json['lng']]
            except:
                return False
        else:
            return False #when the zipcode does not exist
    else:
        statement_get_latLon = '''
            SELECT Lat, Lon
            FROM Zipcodes
            WHERE Zipcode = %s
        ''' % zip_code
        cur.execute(statement_get_latLon)
        latLon = list(cur.fetchall())[0]
    # conn_z.close()
    return latLon

# def db_insert_zipcode_get_id(zip_code):
#     conn = sqlite3.connect('meetup.sqlite')
#     cur = conn.cursor()
#     if not has_zip(zip_code):
#         zipcodes_json = get_zipcode(zip_code)
#         if zipcodes_json != None:
#             statement = '''
#                 INSERT INTO Zipcodes (Zipcode, CityName, StateName, Lat, Lon)
#                 VALUES (?, ?, ?, ?, ?)
#             '''
#             params_s = (zip_code, zipcodes_json['city'], zipcodes_json['state'], zipcodes_json['lat'], zipcodes_json['lng'])
#             cur.execute(statement, params_s)
#             conn.commit()
#         else:
#             return None #when the zipcode does not exist
#
#     statement_get_latLon = '''
#         SELECT Id
#         FROM Zipcodes
#         WHERE Zipcode = %s
#     ''' % zip_code
#     cur.execute(statement_get_latLon)
#     zipcode_Id = list(cur.fetchall())[0][0]
#     conn.close()
#     return zipcode_Id

#insert event
def db_insert_event(zip_code, latLon, category_Id):
    category_name = get_category_name(category_Id)

    events_json = get_events(latLon[0], latLon[1], category_Id)
    events_list = [] # [[0,name,link], [1,name,link]] # 0/1 means available/not available # in form of class Event

    if len(events_json['events']) != 0:
        # conn = sqlite3.connect('meetup.sqlite')
        # cur = conn.cursor()
        #input information into DB
        for each in events_json['events']:
            if not has_event(each['link']):
                if 'venue' in each:
                    try:
                        zipcode = each['venue']['zip']
                    except:
                        zipcode = ''

                    if zipcode == '':
                        zipcode = int(zip_code)

                    db_insert_zipcode(zipcode)

                    statement = '''
                        INSERT INTO Events (EventName, CategoryId, Zipcode, Address, City, State, [Date], [Time], Lat, Lon, Link)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    # +', '+each['venue']['state']
                    params_s = (each['name'], category_Id, zipcode, each['venue']['address_1']+', '+each['venue']['city'], events_json['city']['city'], events_json['city']['state'], each['local_date'], each['local_time'], each['venue']['lat'], each['venue']['lon'], each['link'])
                    cur.execute(statement, params_s)
                else:
                    statement = '''
                        INSERT INTO Events (EventName, CategoryId, City, State, Link)
                        VALUES (?, ?, ?, ?, ?)
                    '''
                    params_s = (each['name'], category_Id, events_json['city']['city'], events_json['city']['state'], each['link'])
                    cur.execute(statement, params_s)
        conn.commit()
        # conn.close()

        #get information from DB into onject Events
        for each in events_json['events']:
            if 'venue' in each:
                events_list.append(Event(0, each['name'], each['link']))
            else:
                events_list.append(Event(1, each['name'], each['link']))

        return [category_name,events_list]
    # if no upcoming events
    else:
        return False
