import unittest

from cache_prepare import *
from OAuth_process import *
from db_create import *
from model import *


class TestSources(unittest.TestCase):
	# 1. Test that if zipcode can be used to find lat and lon
	def test_zipcode(self):
		zipcode = 48105
		lat = 42.327659
		lon = -83.69653
		zipcodes_json = get_zipcode(zipcode)
		self.assertEqual('%.2f' % zipcodes_json['lat'], '%.2f' % lat)
		self.assertEqual('%.2f' % zipcodes_json['lng'], '%.2f' % lon)


	# 2. Test that if categories can be get from Meetup API
	def test_meetup_category(self):
		category_name = 'Tech'
		category_Id = 292
		categories_json = get_categories()
		for each in categories_json:
			if (each['id'] == category_Id) and (each['name'] == category_name):
				return True
		return False



	# 3. Test that if certain events can be get from Meetup API
	def test_meetup_events(self):
		event_name = "Let's try to talk in Japanese! 日本語で話しましょう！"
		lat = 42.327659
		lon = -83.69653
		category_Id = 212 #language

		events_url = protected_url + '/find/upcoming_events'
		event_params = {'lon' : lon, 'lat' : lat, 'topic_category': category_Id}
		params = {**api_param, **event_params}
		events_json = make_request_using_cache(events_url, params = params)

		for each in events_json['events']:
			if each['name'] == event_name:
				return True
		return False


	# 4. Test that if a attendee's information can be get from crowling
	def test_meetup_attendees_scraping(self):
		link = 'https://www.meetup.com/Ann-Arbor-Japanese-Language-Meetup/events/249628443/'
		member_link = '/Ann-Arbor-Japanese-Language-Meetup/members/12234611/'
		html = make_request_using_cache(link, style = 'html')
		soup = BeautifulSoup(html, "html.parser")
		member_elements = soup.find_all(class_ = 'groupMember-link')
		for each in member_elements:
			if member_link == each['href']:
				return True
		return False


	# 5. Test that if a attendee's information can be get from crowling
	def test_meetup_attendee_detail_scraping(self):
		member_link = 'https://www.meetup.com/Ann-Arbor-Japanese-Language-Meetup/members/12234611/'
		member_location = 'Ann Arbor'
		html = make_request_using_cache(member_link, style = 'html')
		soup = BeautifulSoup(html, "html.parser")
		city = soup.find(class_ = 'locality').text
		self.assertEqual(city, member_location)


class TestDatabase(unittest.TestCase):
	# 6. can get category from the db
	def test_db_get_category(self):
		category_name = 'Tech'
		category_Id = 292

		conn_c = sqlite3.connect('meetup.sqlite')
		cur_c = conn_c.cursor()
		statement_c_name = '''
			SELECT CategoryName
			FROM Categories
			WHERE CategoryId = ?
		'''
		cur_c.execute(statement_c_name, (category_Id,))
		name = list(cur_c.fetchall())[0][0]
		conn_c.close()

		self.assertEqual(name, category_name)

	# 7. can get zipcode from the db
	def test_db_get_zipcode_latLon(self):
		zipcode = 48105
		lat = 42.327659
		lon = -83.69653

		conn = sqlite3.connect('meetup.sqlite')
		cur = conn.cursor()
		statement_get_latLon = '''
            SELECT Lat, Lon
            FROM Zipcodes
            WHERE Zipcode = ?
        '''
		cur.execute(statement_get_latLon, (zipcode,))
		latLon = list(cur.fetchall())[0]
		conn.close()

		self.assertEqual('%.2f' % latLon[0], '%.2f' % lat)
		self.assertEqual('%.2f' % latLon[1], '%.2f' % lon)

	# 8. can use link to get the latLon of event from the db
	def test_db_get_latLon_link(self):
		event_link = 'https://www.meetup.com/ChiStreetStyle/events/249838149/'
		lat = 41.9005088806152
		lon = -87.6366500854492

		conn = sqlite3.connect('meetup.sqlite')
		cur = conn.cursor()
		statement_get_Event_location = '''
			SELECT Lat, Lon
			FROM Events
			WHERE Link = ?
		'''
		cur.execute(statement_get_Event_location, (event_link,))
		latLon = cur.fetchall()[0]
		conn.close()

		self.assertEqual('%.2f' % latLon[0], '%.2f' % lat)
		self.assertEqual('%.2f' % latLon[1], '%.2f' % lon)

	# 9. can use link to get the name of the category from the db
	def test_db_get_latLon_link(self):
		event_link = 'https://www.meetup.com/ChiStreetStyle/events/249838149/'
		category_name = 'Photography'

		conn = sqlite3.connect('meetup.sqlite')
		cur = conn.cursor()
		statement = '''
			SELECT CategoryName
			FROM Events as e
				JOIN Categories as c
				ON e.CategoryId = c.Id
			WHERE Link = ?
		'''
		cur.execute(statement, (event_link,))
		CategoryName = cur.fetchall()[0][0]
		conn.close()

		self.assertEqual(CategoryName, category_name)

	# 10. can check if a zipcode is in the database
	def test_db_check_zip(self):
		zipcode = 48105
		return has_zip(zipcode)


class TestClasses(unittest.TestCase):
	# 11. test build class Event
	def test_build_Event(self):
		event_name = "April Challenge: The Weather"
		event_link = "https://www.meetup.com/Chicago-Digital-Photo/events/249240165/"
		event_1 = Event(0,event_name, event_link)
		self.assertEqual(event_name, event_1.get_name())

	# 12. test "explore" Event
	def test_explore_Event(self):
		event_name = "Quick Tips - Street Style Meet-up"
		event_link = "https://www.meetup.com/ChiStreetStyle/events/249838149/"
		event_lat = 41.900508880615234

		event_2 = Event(0,event_name, event_link)
		event_2.explore_more_details()

		self.assertEqual('%.2f' % event_lat, '%.2f' % event_2.get_lat())

	# 13. test build class Participant
	def test_build_Participant(self):
		member_link = 'https://www.meetup.com/Ann-Arbor-Japanese-Language-Meetup/members/12234611/'
		member_location = 'Ann Arbor'

		html = make_request_using_cache(member_link, style = 'html')
		soup = BeautifulSoup(html, "html.parser")

		location = soup.find(class_ = 'locality').text

		member_1 = Participant(member_link)
		self.assertEqual(member_location, member_1.city)



class TestProcessing(unittest.TestCase):
	# 14. can get the middle point of lats and lons
	def test_lat_lon_scale_range(self):
		lonList = [2,4,6]
		latList = [1,3,5]
		result = lat_lon_scale_range(latList, lonList)

		self.assertEqual(result['center_lat'], 3)
		self.assertEqual(result['center_lon'], 4)


	# 15. can get the middle point of lats and lons
	def test_get_events_details_for_map_plotly(self):
		event_1_name = "Quick Tips - Street Style Meet-up"
		event_1_link = "https://www.meetup.com/ChiStreetStyle/events/249838149/"
		event_1 = Event(0, event_1_name, event_1_link)
		event_1_lat = 41.9005088806152

		event_2_name = "Urban Night Photography | Outdoor Class and Field Workshop"
		event_2_link = "https://www.meetup.com/Lensflare/events/246787055/"
		event_2 = Event(0, event_2_name, event_2_link)
		event_2_lat = 41.9209785461426

		events_list = [event_1, event_2]
		events_lats_list = [event_1_lat, event_2_lat]

		result = get_events_details_for_map_plotly(events_list)
		self.assertEqual('%.2f' % result['lat_list'][0], '%.2f' % events_lats_list[0])


#############
## The following is a line to run all of the tests you include:
if __name__ == "__main__":
	OAuthorize()
	unittest.main(verbosity=2)
