# si507-final-project
University of Michigan SI 507 final project for Winter 2020 semester. 

This project contains an interactive terminal for users to explore various travel destinations and view results pertaining to its weather. The intended idea is for users to select a region of the world, and be given a list of popular countries traveled to in that region. When the user selects one of those countries, a list of popular cities and tourist attractions will be given. All of the information at this point will be accessed by scraping and crawling through planetware.com. When a popular city is selected by the user, Wikipedia will be scraped to locate its coordinates and Dark Sky’s API will return information pertaining to the type of weather in that city. The user will then be able to choose what visualizations they would like to return through an interactive command prompt and plotly. Visualizations will include hourly temperatures, daily temperatures, hourly precipitation, and wind speeds. 

Websites scraped:
- www.planetware.com
- www.wikipedia.org

Dark Sky API Key:
- The API key is located in a file called secrets.py. Within this file, the api_key = 'string containing key'.
- www.darksky.net 

Add Ons:
- from bs4 import BeautifulSoup
- import requests
- import json
- import secrets # file that contains API key
- import time
- import ast
- import sqlite3
- from datetime import datetime
- import plotly.graph_objs as go 

To interact with this program, obtain api key, save api key in secrets.py file, and run final-project.py
