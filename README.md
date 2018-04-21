# MeetupPlotly

## Data sources include:
- MeetUp API
- MeetUp web page
- Zipcode API
- Twitter API

Please start with "secrets_SAMPLE.py" to get API_keys (the websites are included accordingly), and change the file name to "secrets.py"


## How to run the program:
### 1. Start and OAuthorize
- Operate FinalProject.py
- Copy and paste the url to your browser and allow the connection
- Come back to terminal and type anything and enter
### 2. Home Menu
- Enter "a" or "A" to check more
### 3. List of Themes
- Choose any theme you like by entering the index number, if it's "04", just type "4"
- Enter a zipcode where you want to find events
### 4. List of Events
- Enter "a" or "A" to check the locations on a map (may need to wait for half a minute)
- Enter "b" or "B" to check the number of attendees of the specific theme each day in near future
- Enter an index number to check the event's details
### 5. Event Detail
- Enter "a" or "A" to check the connections between attendees' locations to the event address
- Enter "b" or "B" to check the the popularity of attendees' interests
- Enter "c" or "C" to go back to the List of Events
### 6. List of Events
- Enter "d" or "D" to go back to the List of Themes
### 7. List of Themes
- Enter "0" to go back to Home Menu
### 8. Home Menu
- Enter "b" or "B" to go back to Exit
### 9*. Others
- If you try to run app.py, you can check the unfinished raw web version of the program, and due to time constraints, that's far from finishing.


## Intro to .py files:
### FinalProject.py
- The main file to run the program
### secrets_SAMPLE.py
- Provide what APIs to get, how to get, and where to store, just remember to change the name to "secrets.py"
### OAuth_process.py
- Function OAuthorize()
### cache_prepare.py
- Functions about cache
### db_create.py
- Functions mainly about creating the database
### eventClass.py
- Create the classes of Event and Participants
### model.py
- Most of other affiliated, data-processing, and visualization functions
### test_file.py
- Unittest functions
### app.py & templates
- Tried to implicate everything to a web app through Flask but has run out of time and founding...
