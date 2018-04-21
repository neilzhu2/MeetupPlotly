from secrets import *
from cache_prepare import *
from model import *

import requests
import json
import sqlite3
from bs4 import BeautifulSoup

class Event:
    def __init__(self, not_available, name, link):
        self.not_available = not_available
        self.name = name
        self.link = link

    def explore_more_details(self):
        conn_g_e_p = sqlite3.connect('meetup.sqlite')
        cur_g_e_p = conn_g_e_p.cursor()
        if self.if_not_available() == 0:
            statement_get_Event_location = '''
                SELECT [Date], [Time], EventName, Lat, Lon, Address
                FROM Events
                WHERE Link = ?
            '''
            cur_g_e_p.execute(statement_get_Event_location, (self.link,))
            temp_list = cur_g_e_p.fetchall()[0]
            if (None not in temp_list) and ((temp_list[3] != 0) or (temp_list[4] != 0)):
                self.lat = temp_list[3]
                self.lon = temp_list[4]
                self.address = temp_list[5]
                self.date = temp_list[0]
                self.time = temp_list[1]
                self.time_name = temp_list[0] + ' ' + temp_list[1] + '<br>' + temp_list[2]
            else:
                self.not_available = 1
        conn_g_e_p.close()

        #participants
        self.participants_list = []
        base_url = 'https://www.meetup.com'
        html = make_request_using_cache(self.link, style = 'html')
        soup = BeautifulSoup(html, "html.parser")
        member_elements = soup.find_all(class_ = 'groupMember-link')
        for each in member_elements:
            member_url = base_url + each['href']
            self.participants_list.append(Participant(member_url))

    def if_not_available(self):
        return self.not_available

    def get_link(self):
        return self.link

    def get_date(self):
        return self.date

    def get_date_time(self):
        return self.date + ' ' + self.time

    def get_address(self):
        return self.address

    def get_name(self):
        return self.name

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def get_details_for_map_plotly(self):
        return (self.time_name, self.lat, self.lon)

    def get_participants(self):
        return self.participants_list

    def count_participants(self):
        return len(self.participants_list)

    def print_event(self, count):
        other = ''
        if self.if_not_available() == 1:
            other = '(Limited Accessibility! Available only to members)'
        print_ordered_list_item(count, self.name, other)






class Participant:
    def __init__(self, link):
        self.link = link

        html = make_request_using_cache(self.link, style = 'html')
        soup = BeautifulSoup(html, "html.parser")
        try:
            self.name = soup.find(class_ = 'memName').text
        except:
            self.name = ''
        self.city = soup.find(class_ = 'locality').text
        self.region = soup.find(class_ = 'region').text

        self.interests = []
        try:
            interests_list = soup.find(class_ = 'interest-topics').find_all('a')
            for each in interests_list:
                self.interests.append(each.text)
        except:
            self.interests = []

    def get_location(self):
        location_url = 'https://www.zipcodeapi.com/rest/%s/city-zips.json/%s/%s' % (zip_api, self.city, self.region)
        zipcode =  make_request_using_cache(location_url)["zip_codes"][0]
        latLon = get_zipcode(zipcode)
        self.lat = latLon['lat']
        self.lon = latLon['lng']
        return {'city':self.city + ', ' + self.region, 'lat': self.lat, 'lon': self.lon}

    def get_interests(self):
        return self.interests

    def get_name(self):
        return self.name
