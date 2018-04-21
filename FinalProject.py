from cache_prepare import *
from OAuth_process import *
from db_create import *
from model import *


### OAUTH ###
OAuthorize()

### DB ###

db_initialize_tables()

db_insert_categories()

### in app ###
in_app = True

print("\n\nWelcome to Neil's 507 lo-final project!")
## 1 Main Menu ##
while in_app:
    order_main = input('\n***********************\n\na. Check information of events\nb. Exit\n\nGive your order: ')

    print(order_main)
    if order_main == ('b' or 'B'):
        in_app = False

    elif order_main == ('a' or 'A'):
        ## 2 Theme List ##
        choose_theme = True
        while choose_theme:
            print_categories()

            # Insert data into 'Zipcodes' & 'Events' based on user's input
            input_results = input_zip_and_theme()

            # input 0 to go back to main menu
            if not input_results:
                choose_theme = False
                break

            events_list = input_results[0]
            category_name = input_results[1]

            ## 3 Event List ##
            choose_event = True
            while choose_event:
                print_events(events_list)
                order_event = input('\n***********************\n\na. Check locations of the events\nb. Check the number of attendees of "%s" on each day\n*c. Check the details of one Event (INPUT the index number)\nd. Back to Theme List\nGive your order: ' % category_name)
                if order_event == ('a' or 'A'):
                    #plotly of locations
                    plotly_events_locations(events_list, category_name)

                elif order_event == ('b' or 'B'):
                    # Plotly of numbers of participants through time
                    plotly_number_time(events_list)

                elif order_event == ('d' or 'D'):
                    choose_event = False

                elif order_event == ('c' or 'C'):
                    print('just name the index number of the event...')

                elif order_event.isdigit():
                    selected_event = select_event(events_list, int(order_event))
                    ## 4 Event Detail ##
                    display_event_detail(selected_event)

                else:
                    print("Sorry, the command you input is too complicated for me to understand... let's try again...")
                    continue


    else:
        print("Sorry, the command you input is too complicated for me to understand... let's try again...")
        continue

print("\nHave a great day! Bye!\n")
