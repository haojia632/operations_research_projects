from bs4 import BeautifulSoup
import csv
import urllib2
import re
from geopy.geocoders import Nominatim as nom
from geopy.distance import vincenty
import json
import googlemaps

def reverseGeocode(latitude, longitude):
    geolocator = nom()
    return geolocator.reverse(latitude, longitude)

def getStateDict():
    stateTable = open('state_table.csv')
    stateCsv = csv.reader(stateTable)
    stateDict = {}
    for row in stateCsv:
        stateName = row[0]
        stateAbrv = row[1]
        stateDict[stateName] = stateAbrv
    return stateDict
# Import state abreviations
stateDict = getStateDict()

# Define Restaurant Chain URL root
stateRoot = r'https://www.menuism.com/restaurant-locations/mcdonalds-21019/us/ak'
# Header element so the page does not treat routine as a web bot
hdr = {'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"}

def scrapeRestaurant(location):
    locationReq = urllib2.Request(location, headers= hdr)
    pageLocation = urllib2.urlopen(locationReq)
    soupLocation = BeautifulSoup(pageLocation, "lxml")
    restaurant = {}
    # for span in soupLocation.find('div', {'class':'map-info'}).children:
    for span in soupLocation.select('.map-info span'):
        # print unicode(span)
        restaurant[span['itemprop']] = span.text.strip()
    for meta in soupLocation.select('span[itemprop="geo"] meta'):
        restaurant[meta['itemprop']] = float(meta['content'])
    storeNumberListObj = re.findall(r'(\d+$)', str(location))
    restaurant['storeNumber'] = storeNumberListObj[0]
    # If we were unable to get the address from the HTML, we'll
    # have to use reverse geocoding:
    if not restaurant['streetAddress']:
        lat = restaurant['latitude']
        lon = restaurant['longitude']
        restaurant['streetAddress'] = reverseGeocode(lat, lon)
    return restaurant

stateUrl = stateRoot
# print urlState
stateReq = urllib2.Request(stateUrl, headers= hdr)
soupState = BeautifulSoup(urllib2.urlopen(stateReq), "lxml")
storeStateTable = soupState.findAll('ul', {'class':'list-unstyled-links'})

restaurants = []
for storeCode in storeStateTable:

    storeLinkList=[]
    for storeLink in storeCode.find_all('a'):
        storeLinkList.append(storeLink.get('href'))
        # scrape every url for every restaurant.
        for location in storeLinkList:
            restaurant = scrapeRestaurant(location)
            restaurants.append(restaurant)
print restaurants

keys = restaurants[0].keys()

with open('mcdonalds-ak-info.csv','wb') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writerows(restaurants)

 # Calculate Coordinate within 50 mi of (61.219548	-149.823784)

# for i in restaurants:
#     alaskaPoint = (61.219548, -149.823784)
#     alaskaRestaurantLocation = restaurant['latitude'], restaurant['longitude']
#     alaskaRestaurantStoreNumber = restaurant['storeNumber']
#     alaskaDistance = vincenty(alaskaPoint, alaskaRestaurantLocation).miles
#     if alaskaDistance <= 50:
#         print i
#
# # Pick 3 McDonalds Locations
# for j in restaurants:
#     selectedThreeAK = []
#     if restaurant['addressRegion'] == "AK":
#         selectedThreeAK.append(restaurants[0:4])
#     print selectedThreeNY
# json_str = json.dumps(selectedThreeNY)
#
# # gmaps = googlemaps.Client(key='AIzaSyAlNqOWCFtI8VZ2x1I4D10w4uLkRvx9Bpg')
#
# for i in selectedThreeAK:
#   my_distance = ggmaps.distance_matrix(,y)
