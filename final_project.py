#################################
##### Name: Jovana Paripovic    
##### Uniqname: jparipov
#################################

from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1
import requests
import json
import secrets # file that contains API key
import time
import ast
import sqlite3


client_key = secrets.API_KEY
CACHE_FILE_NAME = "travel.json"
CACHE_DICT = {}

headers = {
    'User-Agent': 'UMSI 507 Course Final Project',
    'From': 'jparipov@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

#CACHE INFORMATION

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_url_request_using_cache(url, cache):
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

class Region:
    '''a national site
    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')
    address: string
        the city and state of a national site (e.g. 'Houghton, MI')
    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')
    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, region = 'No Region', destination = 'No Destination', attraction = 'No Attraction'):
        self.region = region
        self.destination = destination
        self.attraction = attraction

    def info(self):
        return f'{self.destination} ({self.region}): {self.attraction}'


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
        

    for search in searching_url:
        try:
            destination = search.find('a').text.strip()
            for item in second_url:
                try:
                    found_params = item.find('a')['href']
                    found_url = baseurl + found_params
                except:
                    pass
            dest_url_dict[destination] = found_url
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
        attractions_list.append(result.strip())
    
    return attractions_list

# get_attractions_for_region('https://www.planetware.com/tourist-attractions/sweden-s.htm')


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
        long = soup.find('span',class_= "longitude").text

        #translate coordinates minutes to decimals

        i = lat.split('°')[1]
        m = int(i.split("′")[0])/60
        i2= i.split("′")[1]
        s = int(i2.split('″')[0])/3600

        if lat[-1] == "N":
            latitude = int(lat.split('°')[0])+m+s
        else:
            latitude = (int(lat.split('°')[0])+m+s)*(-1)
        
        i = long.split('°')[1]
        m = int(i.split("′")[0])/60
        i2= i.split("′")[1]
        s = int(i2.split('″')[0])/3600

        
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

# print(get_coordinates('http://en.wikipedia.org/wiki/ann_arbor'))


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

DATABASE = 'final.sqlite'

def create_db():
    '''
    Create two bases, one representing travel and the other representing the fields returned from the Dark Sky weather API. 
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
    Load data from dark sky into weather table

    parameters:
    json
        output of the call from dark sky api
    
    return:
    none
    '''


    insert_weather_sql = '''
        INSERT INTO Travel
        VALUES (?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    lat = data['latitude']
    long = data['longitude']

    coordinates = f'{lat},{long}' 

    cur.execute(insert_weather_sql,
        [
            coordinates,
            region,
            destination,
            attraction
        ]
    )

    conn.commit()
    conn.close()


# def load_weather(data): 
    # '''
    # Load data from dark sky into weather table

    # parameters:
    # json
    #     output of the call from dark sky api
    
    # return:
    # none
    # '''

    # # base_url = 'https://restcountries.eu/rest/v2/all'
    # # countries = requests.get(base_url).json()

    # insert_weather_sql = '''
    #     INSERT INTO CurrentWeather
    #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    # '''

    # conn = sqlite3.connect(DATABASE)
    # cur = conn.cursor()
    # lat = data['latitude']
    # long = data['longitude']

    # coordinates = f'{lat},{long}' 

    # cur.execute(insert_weather_sql,
    #     [
    #         coordinates,
    #         data['currently']['time'],
    #         data['latitude'], 
    #         data['longitude'], 
    #         data['currently']["summary"],
    #         data['currently']["precipProbability"], 
    #         data['currently']["temperature"],
    #         data['currently']["apparentTemperature"],
    #         data['currently']["humidity"],
    #         data['currently']["windSpeed"]
    #     ]
    # )

    # conn.commit()
    # conn.close()

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

    cur.execute(insert_forecast_sql,
        [
            coordinates,
            data['currently']['time'], 
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
                hour['time'],
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
                day['time'],
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
load_travel(make_request(get_coordinates('http://en.wikipedia.org/wiki/vasa_museum')), 'Europe', 'Sweden', 'vasa museum')
load_forecast(make_request(get_coordinates('http://en.wikipedia.org/wiki/vasa_museum')))

