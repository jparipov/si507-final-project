#################################
##### Name: Jovana Paripovic    
##### Uniqname: jparipov
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains API key
import time
import ast
import sqlite3
from datetime import datetime
import plotly.graph_objs as go 



client_key = secrets.API_KEY
CACHE_FILE_NAME = "travel.json"
CACHE_DICT = {}
DATABASE = 'final.sqlite'

headers = {
    'User-Agent': 'UMSI 507 Course Final Project',
    'From': 'jparipov@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

#CACHE INFORMATION

def load_cache():
    '''
    loading cache
    paramters:
    none
    return:
    none
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    '''a place to save cache
    parameter:
    string
    return:
    none
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_url_request_using_cache(url, cache):
    '''Make a url request using cache

    parameters:
    url - string of url
    cache - dictionary

    return:
    none
    '''

    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

CACHE_DICT = load_cache()

# class Region:
#     '''a national site
#     Instance Attributes
#     -------------------
#     category: string
#         the category of a national site (e.g. 'National Park', '')
#         some sites have blank category.
    
#     name: string
#         the name of a national site (e.g. 'Isle Royale')
#     address: string
#         the city and state of a national site (e.g. 'Houghton, MI')
#     zipcode: string
#         the zip-code of a national site (e.g. '49931', '82190-0168')
#     phone: string
#         the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
#     '''
#     def __init__(self, region = 'No Region', destination = 'No Destination', attraction = 'No Attraction'):
#         self.region = region
#         self.destination = destination
#         self.attraction = attraction

#     def info(self):
#         return f'{self.destination} ({self.region}): {self.attraction}'


### PLANETWARE ####

def build_region_url_dict():
    ''' Make a dictionary that maps region name to region page url from "https://www.planetware.com"
    Parameters
    ----------
    None
    Returns
    -------
    dict
        key is a region and value is the url
        e.g. {'europe':'https://www.planetware.com/europe-travel.htm', ...}
    '''

    #Make the soup
    region_url_dict = {}
    url = "https://www.planetware.com"
    response = make_url_request_using_cache(url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    
    #Get the searching-div
    searching_div = soup.find('div',class_= "regions" )

    
    region_li_list= searching_div.find_all('li')
    # print(state_li_list)

    for element in region_li_list:
        name = element.find('a').text.lower()
        # print(name)
        params = element.find('a')['href']
        final_url = url + params
        region_url_dict[name] = final_url

    region_url_dict.pop('explore your world ×')    
    return region_url_dict


def build_destination_url_dict(region_url):
    ''' Make a dictionary that maps destination name to state page url from "https://www.planetware.come"
    Parameters
    ----------
    None
    Returns
    -------
    dict
        key is a destination and value is the url of the tourist attractions
        e.g. {'Wales Travel Guide': https://www.planetware.com/tourist-attractions/wales-w.htm', ...}
    '''

    response = make_url_request_using_cache(region_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')

    searching_url = soup.find_all('div',class_= "dest" )
    # print(searching_url)
    second_url = soup.find_all('div',class_= "extra" )
    
    dest_url_dict = {}
    baseurl = "https://www.planetware.com"

    # for tag in soup.find_all("span", class_ = 'img'):
    #     tag.replaceWith('')
        
    f = []


    for item in second_url:
        try:
            found_params = item.find('a')['href']
            found_url = baseurl + found_params
            f.append(found_url)
        except:
            pass

    # count = 0 
    for search in searching_url:
        try:
            destination = search.find('a').text.strip()
            for item in f:
                if destination[0:5].lower() in item:
                    dest_url_dict[destination] = item
                else:
                    pass
        except:
            pass

   
    return dest_url_dict

# print(build_destination_url_dict('https://www.planetware.com/europe-travel.htm'))

def get_attractions_for_region(destination_url):
    '''Make a list of attractions from a destinations url
    
    Parameters
    ----------
    state_url: string
        The URL for a attractions page in planetware.com
    
    Returns
    -------
    list
        a list of travel attractions (ie "The Great Wall of China")
    '''
    response = make_url_request_using_cache(destination_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')

    searching_url = soup.find_all('h2',class_= "sitename" )
    # print(searching_url)
    
    attractions_list = []
    for search in searching_url:
        # found_params = search.find('h2')
        s = search.text
        result = ''.join([i for i in s if not i.isdigit()])
        # print(result)
        attractions_list.append(result.strip())
    
    new_list = []
    for item in attractions_list:
        if item[1] == ' ':
            item = item[2:]
            new_list.append(item)
            attractions_list = new_list
        else:
            pass
    
    return attractions_list

    

# print(get_attractions_for_region('https://www.planetware.com/tourist-attractions/sweden-s.htm'))


### WIKIPEDIA ###

def get_wiki_url(attraction):
    ''' 
    Get wiki url of a given attraction from en.wikipedia.com
    Parameters
    ----------
    attraction

    Returns
    -------
    string
        url for the specified attraction '''

    base_wiki = 'http://en.wikipedia.org/wiki/'
    a = attraction.split(",")[0]
    underscore = a.replace(" ", "_")
    url = f'{base_wiki}{underscore}'
    return url

# print(get_wiki_url('gamla stan'))

def get_coordinates(wiki_url):
    ''' 
    Get coordinates of a given attraction from wikipedia.com and convert coordinates from degrees to decimals
    Parameters
    ----------
    attraction

    Returns
    -------
    string
        coordinates for the specified attraction in decimal latitude,longitude '''

    #Make the soup
    
    response = make_url_request_using_cache(wiki_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    
    try: 
        #Get the searching-div
        lat = soup.find('span',class_= "latitude" ).text
        # print(lat)
        long = soup.find('span',class_= "longitude").text

        #translate coordinates minutes to decimals

        i = lat.split('°')[1]
        # print(i)
        m = int(i.split("′")[0])/60
        # print(m)
        i2= i.split("′")[1]
        # print(i2)

        try:
            s = int(i2.split('″')[0])/3600
            # print(s)
        except ValueError:
            s = 0
        
        if lat[-1] == "N":
            latitude = int(lat.split('°')[0])+m+s
        else:
            latitude = (int(lat.split('°')[0])+m+s)*(-1)
        
        i = long.split('°')[1]
        m = int(i.split("′")[0])/60
        i2= i.split("′")[1]

        try:
            s = int(i2.split('″')[0])/3600

        except ValueError:
            s = 0 

        
        if long[-1] == "E":
            longitude = int(long.split('°')[0])+m+s
        else:
            longitude = (int(long.split('°')[0])+m+s)*(-1)
        
        coordinate = []
        coordinate.append(latitude)
        coordinate.append(longitude)

        coordinates = f'{latitude},{longitude}'
    
    except:
        coordinates = 'Weather cannot be obtained for this attraction'

    return coordinates

# print(get_coordinates('http://en.wikipedia.org/wiki/andorra'))


### DARK SKY ###

def make_request(params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    baseurl = 'https://api.darksky.net/forecast/'
    url = f'{baseurl}{client_key}/{params}'
    response = make_url_request_using_cache(url, CACHE_DICT)

    #save to json file to better understand data    
    data = ast.literal_eval(response)

    with open('data.json', 'w') as f:
        json.dump(data, f, indent = 4)

    return data


# make_request(get_coordinates('http://en.wikipedia.org/wiki/gamla_stan'))

### DATABASES ###


def create_db():
    '''
    Create two bases, one representing travel and the other representing the fields returned from the Dark Sky weather API. 
    parameters/return : none
    '''

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    drop_travel_sql = 'DROP TABLE IF EXISTS "Travel"'
    # drop_weather_sql = 'DROP TABLE IF EXISTS "CurrentWeather"'
    drop_forecast_sql = 'DROP TABLE IF EXISTS "Forecast"'

    create_travel_sql = '''
        CREATE TABLE IF NOT EXISTS "Travel" (
            "Coordinates" TEXT PRIMARY KEY,
            "Region"    TEXT NOT NULL,
            "Destination" TEXT NOT NULL,
            "Attraction" TEXT NOT NULL
        );
    '''
    #current weather
    # create_weather_sql = '''
    #     CREATE TABLE IF NOT EXISTS "CurrentWeather" (
    #         "Coordinates" TEXT PRIMARY KEY,
    #         "Time"      INTEGER NOT NULL,
    #         "Latitude"  REAL NOT NULL,
    #         "Longitude" REAL NOT NULL,
    #         "Summary"   TEXT NOT NULL,
    #         "Precipitation_Probability"    REAL NOT NULL,
    #         "Temperature" REAL NOT NULL,
    #         "Feel_Like_Temp" REAL NOT NULL,
    #         "Humidity" REAL NOT NULL,
    #         "Wind_Speed" REAL NOT NULL
    #     );
    # '''
    #forecasted data
    create_forecast_sql = '''
        CREATE TABLE IF NOT EXISTS "Forecast" (
            "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Coordinates" TEXT NOT NULL,
            "Time"      INTEGER NOT NULL,
            "ForecastType" TEXT NOT NULL,
            "Summary"   TEXT NOT NULL,
            "Precipitation_Probability"    REAL NOT NULL,
            "Temperature" REAL NOT NULL,
            "Feel_Like_Temp" REAL NOT NULL,
            "Humidity" REAL NOT NULL,
            "Wind_Speed" REAL NOT NULL
        );
    '''

    cur.execute(drop_travel_sql)
    # cur.execute(drop_weather_sql)
    cur.execute(drop_forecast_sql)
    cur.execute(create_travel_sql)
    # cur.execute(create_weather_sql)
    cur.execute(create_forecast_sql)
    conn.commit()
    conn.close()

# create_db()



def load_travel(data, region, destination, attraction):  
    '''
    Load data from dark sky into weather table based off of user inputs

    parameters:
    data: json
        output of the call from dark sky api

    region: string

    destination: string

    attraction: string
    
    return:
    none
    '''


    insert_travel_sql = '''
        INSERT INTO Travel
        VALUES (?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    lat = data['latitude']
    long = data['longitude']

    coordinates = f'{lat},{long}' 

    cur.execute(insert_travel_sql,
        [
            coordinates,
            region,
            destination,
            attraction
        ]
    )

    conn.commit()
    conn.close()


def load_forecast(data): 
    '''
    Load hourly/daily data from dark sky into forecast table

    parameters:
    json
        output of the call from dark sky api
    
    return:
    none
    '''

    # base_url = 'https://restcountries.eu/rest/v2/all'
    # countries = requests.get(base_url).json()

    insert_forecast_sql = '''
        INSERT INTO Forecast
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    lat = data['latitude']
    long = data['longitude']

    coordinates = f'{lat},{long}' 

    current_time = datetime.fromtimestamp(data['currently']['time'])

    cur.execute(insert_forecast_sql,
        [
            coordinates,
            current_time, 
            'Currently',
            data['currently']["summary"],
            data['currently']["precipProbability"], 
            data['currently']["temperature"],
            data['currently']["apparentTemperature"],
            data['currently']["humidity"],
            data['currently']["windSpeed"]
        ]
    )

    for hour in data['hourly']['data']:
        cur.execute(insert_forecast_sql,
            [#first is ID,
                coordinates,
                datetime.fromtimestamp(hour['time']),
                'Hourly',
                hour["summary"],
                hour["precipProbability"], 
                hour["temperature"],
                hour["apparentTemperature"],
                hour["humidity"],
                hour["windSpeed"]
            ]
        )

    for day in data['daily']['data']:
        cur.execute(insert_forecast_sql,
            [#first is ID,
                coordinates,
                datetime.fromtimestamp(day['time']),
                'Daily',
                day["summary"],
                day["precipProbability"], 
                day["temperatureHigh"],
                day["apparentTemperatureHigh"],
                day["humidity"],
                day["windSpeed"]
            ]
        )

    conn.commit()
    conn.close()


# load_weather(make_request(get_coordinates('http://en.wikipedia.org/wiki/gamla_stan')))
# load_travel(make_request(get_coordinates('http://en.wikipedia.org/wiki/vasa_museum')), 'Europe', 'Sweden', 'vasa museum')
# load_forecast(make_request(get_coordinates('http://en.wikipedia.org/wiki/vasa_museum')))

def clean(string):
    '''
    Description:
    Functions cleans string to only return first word in phrase

    Parameters:
    string - "Andorra Travel Guide"

    Return:
    string -"Andorra"
    '''

    new = string.split(' ')
    word = new [0]

    return word

### PLOTS ###

def hour_plot(data):
    '''Make an hourly line chart based off of hourly weather temperature data

    Parameters:
    dictionary - this is pulling weather data saved in a json

    return:
    line chart
    '''
    time = []
    temp = []

    for hour in data['hourly']['data']:
        time.append(datetime.fromtimestamp(hour['time']))
        temp.append(hour['temperature'])


    xvals = time
    yvals = temp

    scatter_data = go.Scatter(x=xvals, y=yvals, marker = {'color': 'magenta'})
    basic_layout = go.Layout(title="Hourly Temperatures",  xaxis_title = "Time", yaxis_title = "Temperature")
    fig = go.Figure(data=scatter_data, layout=basic_layout)

    return fig.write_html("hour.html", auto_open=True)

def day_plot(data):
    '''Make an daily bar chart based off of daily temperature data

    Parameters:
    dictionary - this is pulling weather data saved in a json

    return:
    line chart
    '''
    time = []
    hightemp = []
    lowtemp = []

    for day in data['daily']['data']:
        time.append(datetime.fromtimestamp(day['time']))
        hightemp.append(day["temperatureHigh"])
        lowtemp.append(day["temperatureLow"])


    bar_data = go.Figure(data=[
    go.Bar(name='Temperature Low', x=time, y=lowtemp),
    go.Bar(name='Temperature High', x=time, y=hightemp)
    ])
    basic_layout = go.Layout(title="Daily Temperatures", barmode = 'group',  xaxis_title = "Time", yaxis_title = "Temperature")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    return fig.write_html("day.html", auto_open=True)

def rain_plot(data):
    '''Make an hourly scatter chart based off of precipiation data

    Parameters:
    dictionary - this is pulling weather data saved in a json

    return:
    scatter chart
    '''
    time = []
    rain = []

    for hour in data['hourly']['data']:
        time.append(datetime.fromtimestamp(hour['time']))
        rain.append(hour["precipProbability"]*100)

    scatter_data = go.Scatter(
    x=time, 
    y=rain,
    marker={'symbol':'diamond-tall-dot', 'size':15},
    mode='markers')
    basic_layout = go.Layout(title="Precipitation Hourly Forecast", xaxis_title = "Time", yaxis_title = "Precipitation Probability" )
    fig = go.Figure(data=scatter_data, layout=basic_layout)

    return fig.write_html("precip.html", auto_open=True)

def wind_plot(data):
    '''Make an hourly line chart based off of daily wind data

    Parameters:
    dictionary - this is pulling weather data saved in a json

    return:
    line chart
    '''
    time = []
    wind = []

    for hour in data['hourly']['data']:
        time.append(datetime.fromtimestamp(hour['time']))
        wind.append(hour['windSpeed'])


    xvals = time
    yvals = wind

    scatter_data = go.Scatter(x=xvals, y=yvals, marker = {'color': 'green'})
    basic_layout = go.Layout(title="Hourly Wind Speeds",  xaxis_title = "Time", yaxis_title = "Wind Speed (mph)")
    fig = go.Figure(data=scatter_data, layout=basic_layout)

    return fig.write_html("wind.html", auto_open=True)

# print(percip_plot(make_request(get_coordinates('http://en.wikipedia.org/wiki/gamla_stan'))))
### INTERACTIVE ###


if __name__ == "__main__":
    
    user_input = None

    while True:

        #get list of regions
        region_dict = build_region_url_dict()
        region_list = list(region_dict.keys())
        print("\nFrom the list below, choose a region of the world you would like to explore:\n")

        r_count = 1
        for region in region_list:
            print(f'[{r_count}] {region}')
            r_count += 1

        user_input = input("\nChoose a number to explore or 'exit': ")

        try:
            #validate number and print list of destinations
            region_num = int(user_input) - 1
            if (region_num < len(region_list)) and (region_num >= 0):

                r = region_list[region_num]
                r_url = region_dict[r]

                dest_dict = build_destination_url_dict(r_url)
                dest_list = list(dest_dict.keys())

            else:
                int('error')

           

            while True:
                
                print("\nList of Destinations:\n")
                d_count = 1
                for dest in dest_list:
                    print(f'[{d_count}] {dest}')
                    d_count += 1
                user_input = input("\nChoose a number to explore or 'back' or 'exit': ")

                if user_input == 'exit':
                    exit()

                elif user_input == 'back':
                    break

                else:
                
                    try:
                        #validate number and provide list of attractions
                        dest_num = int(user_input) - 1

                        if (dest_num < len(dest_list)) and (dest_num >= 0):
                            d = dest_list[dest_num]
                            attractions = get_attractions_for_region(dest_dict[d])
                        
                        else:
                            int('error')

                        while True:

                            print("\nAttractions List")
                            a_count = 1
                            for a in attractions:
                                print(f'[{a_count}] {a}')
                                a_count += 1

                            user_input = input("\nWow! What an exciting list of attractions. Better start planning your trip! \nChoose a number from the list above to check the attraction's weather, 'back' or 'exit': ")
                            
                            if user_input == 'exit':
                                exit()

                            elif user_input == 'back':
                                break

                            else:

                                try:
                                    wiki_index = int(user_input) - 1 
                                    if (wiki_index < len(attractions)) and (wiki_index >= 0):
                                        attraction = attractions[wiki_index]
                                        c = get_coordinates(get_wiki_url(attraction))
                                    else:
                                        int('error')

                                    if "Weather" in c:
                                        #Weather for attraction cannot be obtained, instead destination weather is found
                                        try:
                                            x = clean(d)
                                            url = get_wiki_url(x)
                                            d_c = get_coordinates(url)
                                            create_db()
                                            data = make_request(d_c)
                                            load_travel(data, r, d, attraction)
                                            load_forecast(data)
                                            location = x
                                            print(f"\nWeather for {attraction} cannot be obtained, instead {location} weather is found.")
                                        except:
                                            print('Weather cannot be obtained, please choose another attraction')
                                            break
                                            

                                    else:
                                        #attraction weather was obtained
                                        location = c
                                        create_db()
                                        data = make_request(c)
                                        load_travel(data, r, d, attraction)
                                        load_forecast(data)
                                        print(f'\n{attraction} Weather:')

                                    

                                    while True:

                                        print(f"Which type of weather forecast would you like to see?")

                                        print("\n[1] Hourly Temperatures\n[2] Week Temperatures\n[3] Hourly Precipitation\n[4] Hourly Wind Speeds")
                                        user_input = input("\nChoose a number from the list above, 'back' or 'exit': ")

                                        try:
                                            user = int(user_input)
                                            if user == 1:
                                                hour_plot(data)
                                            elif user == 2:
                                                day_plot(data)
                                            elif user == 3:
                                                rain_plot(data)
                                            elif user == 4:
                                                wind_plot(data)
                                            else:
                                                int('error')
                                                

                                        except ValueError:
                                            if user_input == 'exit':
                                                exit()

                                            elif user_input == 'back':
                                                break

                                            else:
                                                print("\n[Error]: Not a valid number. Please choose number, 'back' or 'exit'.")


                                
                                except ValueError:
                                    print("\n[Error]: Not a valid number. Please choose number, 'back' or 'exit'.")



                    except ValueError:
                        print("\n[Error]: Not a valid number. Please choose number, 'back' or 'exit'.")
                        


        except ValueError:

            if user_input == 'exit':
                exit()

            else:
                print("\nError: Not a valid number. Please choose number or 'exit'.")
            
