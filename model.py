from secrets import *
from cache_prepare import *
from OAuth_process import *
import db_create

import requests
import json
import sqlite3
from bs4 import BeautifulSoup
import tweepy

import plotly.plotly as py
from plotly.graph_objs import *
import plotly.offline as offplot


# Get Categories
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

def get_category_name(category_id):
    conn_c = sqlite3.connect('meetup.sqlite')
    cur_c = conn_c.cursor()
    statement_c_name = '''
        SELECT CategoryName
        FROM Categories
        WHERE Id = ?
    '''
    cur_c.execute(statement_c_name, (category_id,))
    result = list(cur_c.fetchall())[0][0]
    conn_c.close()
    return result

#input data - zip & themes
def input_zip_and_theme():
    print('\n***********************\n')
    latLon = False
    events_list = False
    in_repeat = False
    # will pass only when zipcode exists and upcoming events exists
    category_Id = input('Theme ("0" to main menu): ')
    while True:
        if not events_list:
            if in_repeat and latLon:
                print('No upcoming events for the theme you chose, please try again...')
                category_Id = input('Theme ("0" to main menu): ')
            if category_Id == '0':
                return False
            category_Id = int(category_Id)
            print('')

        if not latLon:
            if in_repeat:
                print('The zipcode you entered does not exist, please try again...')
            zip_code = input('Zipcode ("0" to main menu): ')
            if zip_code == '0':
                return False
            conn = sqlite3.connect('meetup.sqlite')
            cur = conn.cursor()
            latLon = db_create.db_insert_zipcode(zip_code)
            conn.close()
            print('')

        if latLon:
            db_insert_event_result = db_create.db_insert_event(zip_code, latLon, category_Id)
            events_list = db_insert_event_result[1]
        if latLon and events_list:
            break
        in_repeat = True
    category_name = db_insert_event_result[0]

    return(events_list, category_name)

# Get Zipcode infos
def has_zip(zipcode):
    conn_z = sqlite3.connect('meetup.sqlite')
    cur_z = conn_z.cursor()
    statement_find_z = '''
        SELECT *
        FROM Zipcodes
        WHERE Zipcode = ?
    '''
    cur_z.execute(statement_find_z, [zipcode])
    if list(cur_z.fetchall()) == []:
        conn_z.close()
        return False
    conn_z.close()
    return True

def get_zipcode(zipcode):
    zip_url = 'https://www.zipcodeapi.com/rest/%s/info.json/%s/degrees' % (zip_api, zipcode)
    return make_request_using_cache(zip_url)

# Choose theme to Get Events
def has_event(link):
    conn_e = sqlite3.connect('meetup.sqlite')
    cur_e = conn_e.cursor()
    statement_find_e = '''
        SELECT *
        FROM Events
        WHERE Link = ?
    '''
    params_s = (link,)
    cur_e.execute(statement_find_e, params_s)
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
    category = cur_e.fetchall()[0]
    cur_e.close()

    event_params = {'lon' : lon, 'lat' : lat, 'topic_category': category}
    params = {**api_param, **event_params}
    return make_request_using_cache(events_url, params = params)

# print out events
def print_events(events_list):
    print('\n*********** UPCOMING EVENTS ***********')
    count = 1
    for each in events_list:
        each.print_event(count)
        count += 1

#input data - event
def select_event(events_list, event_index):
    in_repeat = False
    while(True):
        if in_repeat:
            print('The information of the selected event is not accessible, please try another event...')
            event_index = input('Select Event: ')
        event_index = int(event_index) - 1
        not_available = events_list[event_index].if_not_available()
        if not not_available:
            break
        in_repeat = True
    print('')

    return events_list[event_index]

# Print ordered list
def print_ordered_list_item(count, item, other = ''):
        if count < 10:
            print('0',end='')
        print(count,'. ',item, ' ', other)

# Collect information from the list of events for plotly
def get_events_details_for_map_plotly(events_list):
    events_time_name_list = []
    events_lat_list = []
    events_lon_list = []
    for each in events_list:
        each.explore_more_details()
        if each.if_not_available() == 0:
            temp_list = each.get_details_for_map_plotly()
            events_time_name_list.append(temp_list[0])
            events_lat_list.append(temp_list[1])
            events_lon_list.append(temp_list[2])
    return {'time_name_list':events_time_name_list, 'lat_list': events_lat_list, 'lon_list': events_lon_list}

def lat_lon_scale_range(events_lat_list, events_lon_list):
    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000
    for v in events_lat_list:
        # v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for v in events_lon_list:
        # v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v
    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2
    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]
    return {'center_lat': center_lat, 'center_lon': center_lon, 'lat_axis': lat_axis, 'lon_axis': lon_axis}


# Plotly of event locations
def plotly_events_locations(events_list, category_name):
    events_details_for_plotly = get_events_details_for_map_plotly(events_list)
    events_time_name_list = events_details_for_plotly['time_name_list']
    events_lat_list = events_details_for_plotly['lat_list']
    events_lon_list = events_details_for_plotly['lon_list']

    #get the min/max lat/lon
    scale_range = lat_lon_scale_range(events_lat_list, events_lon_list)
    center_lat = scale_range['center_lat']
    center_lon = scale_range['center_lon']

    #plotly of locations
    # data = [ dict(
    #         type = 'scattergeo',
    #         # locationmode = 'USA-states',
    #         lon = events_lon_list,
    #         lat = events_lat_list,
    #         text = events_time_name_list,
    #         hoverinfo = 'text',
    #         mode = 'markers',
    #         marker = dict(
    #             size = 4,
    #             symbol = 'circle',
    #             color = 'yellow'
    #         ))]
    # layout = dict(
    #         title = 'Geo-Scope of Survey',
    #         geo = dict(
    #             # scope='world',
    #             scope='north america',
    #
    #             projection=dict( type='robinson' ),
    #             showland = True,
    #             showlakes = True,
    #             landcolor = "black",
    #             lakecolor = "rgb(250, 250, 250)",
    #             subunitcolor = "rgb(50, 50, 50)",
    #             countrycolor = "rgb(100, 100, 100)",
    #             countrywidth = 0.5,
    #             subunitwidth = 0.5,
    #             lataxis = {'range': lat_axis},
    #             lonaxis = {'range': lon_axis},
    #             center= {'lat': center_lat, 'lon': center_lon },
    #             showsubunits = True,
    #             showcountries = True,
    #             resolution = 50,
    #         ),
    #     )
    data = Data([
        Scattermapbox(
            lat=events_lat_list,
            lon=events_lon_list,
            mode='markers',
            marker=Marker(
                size = 12,
                symbol = 'circle',
                color = 'blue'
            ),
            text=events_time_name_list,
        )
    ])
    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_api,
            bearing=0,
            center={'lat': center_lat, 'lon': center_lon },
            pitch=0,
            zoom=10
        ),
    )

    fig = dict(data=data, layout=layout )
    py.plot( fig, validate=False, filename='Upcoming Events of "%s"' % category_name)

# Plotly of numbers of participants through time
def plotly_number_time(events_list):
    # events_date_list, events_member_num_list
    date_num_dict = {}
    events_date_list = []
    events_member_num_list = []

    for each in events_list:
        each.explore_more_details()
        if each.if_not_available() == 0:
            date = each.get_date()
            num = each.count_participants()
            if date not in date_num_dict:
                date_num_dict[date] = num
            else:
                date_num_dict[date] += num

    for key in sorted(date_num_dict.keys()):
        events_date_list.append(key)
        events_member_num_list.append(date_num_dict[key])

    data = [Scatter(
          x=events_date_list,
          y=events_member_num_list)]

    py.plot(data)

# Get tweets
def get_tweets(search_term, num_tweets):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    searched_tweets = [status for status in tweepy.Cursor(api.search, q=search_term).items(num_tweets)]
    for each in searched_tweets:
        print(each)

# Display event details
def display_event_detail(selected_event):
    selected_event.explore_more_details()

    print('\n******* %s *******\n' % selected_event.get_name())

    # Show time and location
    print('Time: %s\nLocation: %s\n\n*******\n' % (selected_event.get_date_time(), selected_event.get_address()))

    # Show tweets
    print('(ir)Relevant tweets, if any:\n')
    get_tweets(selected_event.get_name(), num_tweets = 5)
    print('\n*******\n')

    # Show attendees
    print('%d people will attend, including:  ' % selected_event.count_participants())
    participants_list = selected_event.get_participants()
    print(participants_list[0].get_name(), end = '')
    for each in participants_list[1:]:
        print(', ', each.get_name(), end='')
    print('\n\n*******\n')

    # options to see diagrams
    see_detail = True
    is_repeating = False
    order_detail = input("a. Check where everyone's from \nb. Check the popularity of each interest everyone has\nc. Back to Event List\nGive your order: ")

    while see_detail:
        if is_repeating:
            order_detail = input('\nGive another one: ')
        else:
            is_repeating = True

        if order_detail == ('a' or 'A'):
            plotly_people_location(participants_list, selected_event)
        elif order_detail == ('b' or 'B'):
            plotly_interests_bar(participants_list)
        elif order_detail == ('c' or 'C'):
            see_detail = False
        else:
            print("Sorry, the command you input is too complicated for me to understand... let's try again...")
            continue

# Plotly of where attendees from
def distance(alon, alat, blon, blat):
    return float(((alon - blon)**2 + (alat - blat)**2)**(1/2))

def plotly_people_location(participants_list, selected_event):
    event_lon = selected_event.get_lon()
    event_lat = selected_event.get_lat()
    event_address = selected_event.get_address()

    lons_list = []
    lats_list = []
    cities_list = []
    dist_paths = []

    #get the longest distance
    dist = []
    for each in participants_list:
        location_info = each.get_location()
        dist.append(distance(location_info['lon'], location_info['lat'], event_lon, event_lat))
    max_dist = max(dist)

    for each in participants_list:
        location_info = each.get_location()
        lons_list.append(location_info['lon'])
        lats_list.append(location_info['lat'])
        cities_list.append(location_info['city'])
        dist_paths.append(
            dict(
                type = 'scattergeo',
                locationmode = 'USA-states',
                lon = [ location_info['lon'], event_lon ],
                lat = [ location_info['lat'], event_lat ],
                mode = 'lines',
                line = dict(
                    width = 1,
                    color = 'red',
                ),
                opacity = 1 - distance(location_info['lon'], location_info['lat'], event_lon, event_lat) / (max_dist * 1.2),
            )
        )

    event_place = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = [event_lon],
        lat = [event_lat],
        hoverinfo = 'text',
        text = event_address,
        mode = 'markers',
        marker = dict(
            size=8,
            color='rgb(0, 0, 255)',
            symbol = 'star',
            line = dict(
                width=3,
                color='rgba(68, 68, 68, 1)'
            )
        ))]

    attendees = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = lons_list,
        lat = lats_list,
        hoverinfo = 'text',
        text = cities_list,
        mode = 'markers',
        marker = dict(
            size=4,
            color='rgb(255, 0, 0)',
            symbol = 'circle',
            line = dict(
                width=1,
                color='rgba(68, 68, 68, 0)'
            )
        ))]

    #get the min/max lat/lon
    lat_list = lats_list
    lon_list = lons_list
    lat_list.append(event_lat)
    lon_list.append(event_lon)
    scale_range = lat_lon_scale_range(lat_list, lon_list)
    center_lat = scale_range['center_lat']
    center_lon = scale_range['center_lon']
    lat_axis = scale_range['lat_axis']
    lon_axis = scale_range['lon_axis']

    layout = dict(
            title = 'Attendees of %s comes from...' % selected_event.get_name(),
            showlegend = False,
            geo = dict(
                scope='north america',
                projection=dict( type='azimuthal equal area' ),
                showland = True,
                showlakes = True,
                landcolor = 'rgb(243, 243, 243)',
                lakecolor = 'rgb(255, 255, 255)',
                countrycolor = 'rgb(204, 204, 204)',
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center= {'lat': center_lat, 'lon': center_lon },
            ),
        )

    fig = dict( data = dist_paths + attendees + event_place, layout = layout )
    py.plot( fig, filename='Attendees are from...' )

# Plotly of where interests lie
def plotly_interests_bar(participants_list):
    interest_num_dict = {}
    for each in participants_list:
        interest_list = each.get_interests()
        for interest in interest_list:
            if interest not in interest_num_dict:
                interest_num_dict[interest] = 1
            else:
                interest_num_dict[interest] += 1

    interests_list = []
    interests_num = []
    for key, value in sorted(interest_num_dict.items(), key=lambda kv: (kv[1],kv[0])):
        interests_list.append(key)
        interests_num.append(value)

    data = [Bar(
            x = interests_list,
            y = interests_num
    )]

    py.plot(data, filename='interests-bar')



## plotly for flask
def plotly_flask_events_locations(events_list, category_name):
    events_details_for_plotly = get_events_details_for_map_plotly(events_list)
    events_time_name_list = events_details_for_plotly['time_name_list']
    events_lat_list = events_details_for_plotly['lat_list']
    events_lon_list = events_details_for_plotly['lon_list']

    #get the min/max lat/lon
    scale_range = lat_lon_scale_range(events_lat_list, events_lon_list)
    center_lat = scale_range['center_lat']
    center_lon = scale_range['center_lon']

    data = Data([
        Scattermapbox(
            lat=events_lat_list,
            lon=events_lon_list,
            mode='markers',
            marker=Marker(
                size = 12,
                symbol = 'circle',
                color = 'blue'
            ),
            text=events_time_name_list,
        )
    ])
    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_api,
            bearing=0,
            center={'lat': center_lat, 'lon': center_lon },
            pitch=0,
            zoom=10
        ),
    )

    fig = dict(data=data, layout=layout )
    div = offplot.plot(fig, validate=False, filename='Upcoming Events of "%s"' % category_name)
    return div
    # py.plot( fig, validate=False, filename='Upcoming Events of "%s"' % category_name)

def plotly_flask_number_time(events_list):
    # events_date_list, events_member_num_list
    date_num_dict = {}
    events_date_list = []
    events_member_num_list = []

    for each in events_list:
        each.explore_more_details()
        if each.if_not_available() == 0:
            date = each.get_date()
            num = each.count_participants()
            if date not in date_num_dict:
                date_num_dict[date] = num
            else:
                date_num_dict[date] += num

    for key in sorted(date_num_dict.keys()):
        events_date_list.append(key)
        events_member_num_list.append(date_num_dict[key])

    data = [Scatter(
          x=events_date_list,
          y=events_member_num_list)]

    div = offplot.plot(data)
    return div
    # py.plot(data)

def plotly_flask_people_location(participants_list, selected_event):
        event_lon = selected_event.get_lon()
        event_lat = selected_event.get_lat()
        event_address = selected_event.get_address()

        lons_list = []
        lats_list = []
        cities_list = []
        dist_paths = []

        #get the longest distance
        dist = []
        for each in participants_list:
            location_info = each.get_location()
            dist.append(distance(location_info['lon'], location_info['lat'], event_lon, event_lat))
        max_dist = max(dist)

        for each in participants_list:
            location_info = each.get_location()
            lons_list.append(location_info['lon'])
            lats_list.append(location_info['lat'])
            cities_list.append(location_info['city'])
            dist_paths.append(
                dict(
                    type = 'scattergeo',
                    locationmode = 'USA-states',
                    lon = [ location_info['lon'], event_lon ],
                    lat = [ location_info['lat'], event_lat ],
                    mode = 'lines',
                    line = dict(
                        width = 1,
                        color = 'red',
                    ),
                    opacity = 1 - distance(location_info['lon'], location_info['lat'], event_lon, event_lat) / (max_dist * 1.2),
                )
            )

        event_place = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = [event_lon],
            lat = [event_lat],
            hoverinfo = 'text',
            text = event_address,
            mode = 'markers',
            marker = dict(
                size=8,
                color='rgb(0, 0, 255)',
                symbol = 'star',
                line = dict(
                    width=3,
                    color='rgba(68, 68, 68, 1)'
                )
            ))]

        attendees = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lons_list,
            lat = lats_list,
            hoverinfo = 'text',
            text = cities_list,
            mode = 'markers',
            marker = dict(
                size=4,
                color='rgb(255, 0, 0)',
                symbol = 'circle',
                line = dict(
                    width=1,
                    color='rgba(68, 68, 68, 0)'
                )
            ))]

        #get the min/max lat/lon
        lat_list = lats_list
        lon_list = lons_list
        lat_list.append(event_lat)
        lon_list.append(event_lon)
        scale_range = lat_lon_scale_range(lat_list, lon_list)
        center_lat = scale_range['center_lat']
        center_lon = scale_range['center_lon']
        lat_axis = scale_range['lat_axis']
        lon_axis = scale_range['lon_axis']

        layout = dict(
                title = 'Attendees of %s comes from...' % selected_event.get_name(),
                showlegend = False,
                geo = dict(
                    scope='north america',
                    projection=dict( type='azimuthal equal area' ),
                    showland = True,
                    showlakes = True,
                    landcolor = 'rgb(243, 243, 243)',
                    lakecolor = 'rgb(255, 255, 255)',
                    countrycolor = 'rgb(204, 204, 204)',
                    lataxis = {'range': lat_axis},
                    lonaxis = {'range': lon_axis},
                    center= {'lat': center_lat, 'lon': center_lon },
                ),
            )

        fig = dict( data = dist_paths + attendees + event_place, layout = layout )
        div = offplot.plot(fig, filename='Attendees are from...')
        return div
        # py.plot( fig, filename='Attendees are from...' )

def plotly_flask_interests_bar(participants_list):
            interest_num_dict = {}
            for each in participants_list:
                interest_list = each.get_interests()
                for interest in interest_list:
                    if interest not in interest_num_dict:
                        interest_num_dict[interest] = 1
                    else:
                        interest_num_dict[interest] += 1

            interests_list = []
            interests_num = []
            for key, value in sorted(interest_num_dict.items(), key=lambda kv: (kv[1],kv[0])):
                interests_list.append(key)
                interests_num.append(value)

            data = [Bar(
                    x = interests_list,
                    y = interests_num
            )]

            div = offplot.plot(data, filename='interests-bar')
            return div
            # py.plot(data, filename='interests-bar')
