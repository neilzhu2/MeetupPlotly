from flask import Flask, render_template, request

from cache_prepare import *
from OAuth_process import *
from db_create import *
from model import *

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    ## print the categories
    return render_template("index.html", categories = flask_get_categories())


@app.route("/eventsList", methods=['GET', 'POST'])
def eventsList():
    zipcode = request.form["zipcode"]
    latLon = db_insert_zipcode(zipcode)
    category_Id = int(request.form["theme"])

    db_insert_event_result = db_insert_event(latLon, category_Id)
    events_list = db_insert_event_result[1]
    category_name = db_insert_event_result[0]

    ## print the events and have two plotly figures
    return render_template("eventsList.html",
                            category = category_name,
                            plotly_locations = plotly_flask_events_locations(events_list, category_name),
                            plotly_quantity = plotly_flask_number_time(events_list),
                            events_list = events_list,
                            zip_and_theme = [zipcode, category_Id])


@app.route("/eventDetail", methods=['GET', 'POST'])
def eventDetail():
    zipcode = request.form["zipcode"]
    category_Id = int(request.form["theme"])

    events_list = request.form["events_list"]
    event_Id = int(request.form["event_index"])
    selected_event = select_event(events_list, event_Id)


    event_name = selected_event.get_name()
    time = selected_event.get_date_time()
    address = selected_event.get_address()
    attendees_list = selected_event.get_participants()

    selected_event.explore_more_details()

    ## print the details of the event
    return render_template("eventDetail.html",
                            event_name = event_name,
                            time = time,
                            address = address,
                            attendees_list = attendees_list,
                            plotly_from = plotly_flask_people_location(attendees_list, selected_event),
                            plotly_interests = plotly_flask_interests_bar(attendees_list),
                            zip_and_theme = [zipcode, category_Id])


if __name__=="__main__":
    ### OAUTH ###
    OAuthorize()

    ### DB ###

    db_initialize_tables()

    db_insert_categories()

    ### launch flask ###
    app.run(debug=True)
