
from secrets import *
from requests_oauthlib import OAuth1Session
import requests
import json
import sqlite3
from bs4 import BeautifulSoup





### 0 CACHE ###
CACHE_FNAME = 'cache_file.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}


def params_unique_combination(baseurl, params = {}):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)


def make_request_using_cache(baseurl, params = {}, style = 'json'): #style = 'json' or 'html'
    unique_ident = params_unique_combination(baseurl,params)
    if unique_ident in CACHE_DICTION:
        if 'error_msg' not in CACHE_DICTION[unique_ident]:
            print("Getting cached data...")
            return CACHE_DICTION[unique_ident]
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params=params).text
        if style == 'json':
            CACHE_DICTION[unique_ident] = json.loads(resp)
        elif style == 'html':
            CACHE_DICTION[unique_ident] = resp
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]





### 1 OAUTH ###

#1.0 GET A REQUEST TOKEN
request_token_url = 'https://api.meetup.com/oauth/request/'
oauth = OAuth1Session(client_key, client_secret = client_secret)
fetch_response = oauth.fetch_request_token(request_token_url)
resource_request_key = fetch_response.get('oauth_token')
resource_request_secret = fetch_response.get('oauth_token_secret')

#1.1 GET AUTHORIZATION FROM THE USER
base_authorization_url = 'https://secure.meetup.com/authorize/'
authorization_url = oauth.authorization_url(base_authorization_url) #, oauth_callback = "http://neil-zhu2.appspot.com"
print ('Please go here and authorize:', authorization_url)
verifier = input('Type anything after authorization: ')

#1.2 GET ACCESS TOKEN
access_token_url = 'https://api.meetup.com/oauth/access/'
oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=resource_request_key,
                          resource_owner_secret=resource_request_secret,
                          verifier=verifier)
oauth_tokens = oauth.fetch_access_token(access_token_url)
resource_access_key = oauth_tokens.get('oauth_token')
resource_access_secret = oauth_tokens.get('oauth_token_secret')

#1.3 FINAL AUTHORIZE
oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=resource_access_key,
                          resource_owner_secret=resource_access_secret)

protected_url = 'https://api.meetup.com'
api_param = {'key': api_key}


### 2 Founctions ###
#2.0 Get Categories
def has_categories():
    conn_c = sqlite3.connect('meetup.sqlite')
    cur_c = conn_c.cursor()
    statement_find_c = '''
        SELECT *
        FROM Categories
    '''
    cur_c.execute(statement_find_c)
    if list(cur_c.fetchall()) == []:
        conn_c.close()
        return False
    conn_c.close()
    return True

def get_categories():
    category_url = protected_url + '/find/topic_categories'
    return make_request_using_cache(category_url, params = api_param)

#2.1 Get Zipcode infos
def has_zip(zip):
    conn_z = sqlite3.connect('meetup.sqlite')
    cur_z = conn_z.cursor()
    statement_find_z = '''
        SELECT *
        FROM Zipcodes
        WHERE Zipcode = %s
    ''' % zip
    cur_z.execute(statement_find_z)
    if list(cur_z.fetchall()) == []:
        conn_z.close()
        return False
    conn_z.close()
    return True

def get_zipcode(zipcode):
    zip_url = 'https://www.zipcodeapi.com/rest/%s/info.json/%s/degrees' % (zip_api, zipcode)
    return make_request_using_cache(zip_url)

#2.2 Get Events
def has_event(link):
    conn_e = sqlite3.connect('meetup.sqlite')
    cur_e = conn_e.cursor()
    statement_find_e = '''
        SELECT *
        FROM Events
        WHERE Link = '%s'
    ''' % link
    cur_e.execute(statement_find_e)
    if list(cur_e.fetchall()) == []:
        conn_e.close()
        return False
    conn_e.close()
    return True

def get_events(lat, lon, category_id):
    events_url = protected_url + '/find/upcoming_events'

    conn_e = sqlite3.connect('meetup.sqlite')
    cur_e = conn_e.cursor()
    statement_e = '''
        SELECT CategoryId
        FROM Categories
        WHERE Id = %s
    ''' % category_id
    cur_e.execute(statement_e)
    category = cur_e.fetchall()[0][0]
    cur_e.close()

    event_params = {'lon' : lon, 'lat' : lat, 'topic_category': category}
    params = {**api_param, **event_params}
    return make_request_using_cache(events_url, params = params)

#2.3 Get Participants
def get_participants(event_url):
    html = make_request_using_cache(event_url)
    soup = BeautifulSoup(html, "html.parser")
    return soup

#2.4 Get InterestsOfPaticipants
def get_interests(personal_url):
    pass




### 3 DB ###

# 3.0 initiat database
conn = sqlite3.connect('meetup.sqlite')
cur = conn.cursor()

#3.1 Drop tables
statement = '''
    DROP TABLE IF EXISTS 'Participants';
    DROP TABLE IF EXISTS 'InterestsOfPaticipants';
'''
cur.executescript(statement)

#3.2 Create tables
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

#3.3.1 Insert data into 'Categories'
if not has_categories():
    categories_json = get_categories()
    for each_category in categories_json:
        statement = '''
            INSERT INTO Categories (CategoryName, CategoryId)
            VALUES ("%s", %d)
        ''' % (each_category['name'], each_category['id'])
        cur.execute(statement)
    conn.commit()

#3.3.2 Insert data into 'Zipcodes' and get lat&lon
zip_code = input('***********************\nZipcode: ')
if not has_zip(zip_code):
    zipcodes_json = get_zipcode(zip_code)
    statement = '''
        INSERT INTO Zipcodes (Zipcode, CityName, StateName, Lat, Lon)
        VALUES ("%s", "%s", "%s", %f, %f)
    ''' % (zip_code, zipcodes_json['city'], zipcodes_json['state'], zipcodes_json['lat'], zipcodes_json['lng'])
    cur.execute(statement)
    conn.commit()
    latLon = [zipcodes_json['lat'], zipcodes_json['lng']]
else:
    statement_get_latLon = '''
        SELECT Lat, Lon
        FROM Zipcodes
        WHERE Zipcode = %s
    ''' % zip_code
    cur.execute(statement_get_latLon)
    latLon = list(cur.fetchall())[0]

#3.3.3 Options of categories to select
statement_see_categories = '''
    SELECT CategoryName
    FROM Categories
'''
cur.execute(statement_see_categories)
list_categories = cur.fetchall()
print('***********************\nALL THEMES')
count = 1
for each in list_categories:
    if count < 10:
        print('0',end='')
    print(count,'. ',each[0])
    count += 1
category_Id = input('***********************\nTheme: ')
category_Id = int(category_Id)

#3.3.4 Insert data into 'Events'
events_json = get_events(latLon[0], latLon[1], category_Id)
for each in events_json['events']:
    if not has_event(each['link']):
        if 'venue' in each:
            statement = '''
                INSERT INTO Events (EventName, City, State, [Date], [Time], Lat, Lon, Link)
                VALUES ("%s", "%s", "%s", "%s", "%s", "%f", "%f", "%s")
            ''' % (each['name'], events_json['city']['city'], events_json['city']['state'], each['local_date'], each['local_time'], each['venue']['lat'], each['venue']['lon'], each['link'])
            cur.execute(statement)
        else:
            statement = '''
                INSERT INTO Events (EventName, City, State, Link)
                VALUES ("%s", "%s", "%s", "%s")
            ''' % (each['name'], events_json['city']['city'], events_json['city']['state'], each['link'])
            cur.execute(statement)
conn.commit()








print('Done!')
