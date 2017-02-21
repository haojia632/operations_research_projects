from bs4 import BeautifulSoup
import csv
import urllib2
import re
from geopy.geocoders import Nominatim as nom
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
stateRoot = r'https://www.menuism.com/restaurant-locations/mcdonalds-21019/us/'
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

# Iterate over all states and create an list to hold the location dict
def agreggateRestaurantInfo():
    for state in stateDict:
        stateUrl = stateRoot + stateDict[state]
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
                # print restaurant
                restaurants.append(restaurant)

    print storeLinkList

    keys = restaurants[0].keys()

    with open('mcdonalds-info.csv','wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writerows(restaurants)

# Call function that agreggates all McDonalds information
agreggateRestaurantInfo()

#Save CSV Values in Database
def saveMcdonaldsResults():
    conn = sqlite3.connect('database2.db')
    c = conn.cursor()
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS McdonaldsLocations''')
    c.execute('''CREATE TABLE McdonaldsLocations
            (latitude numeric, longitude numeric, storeNumber int, city text, state text, streetAddress varchar,  zip int)
            ''')
    with open ('mcdonalds-info.csv') as g:
        dbReader = csv.reader(g)
        for i in dbReader:
            c.execute("INSERT INTO McdonaldsLocations VALUES (?,?,?,?,?,?,?)", i)
    conn.commit()
    conn.close()

#Call function to save McDonalds results to database2
saveMcdonaldsResults()

 # Calculate McDonalds within 100 miles of all New York McDonalds
 # Center coordinates for New York state 43.2994 N, -74.2179 W
#  for i in restaurants:
#      newYorkPoint = (43.2994, -174.2179)
#      newYorkRestaurantLocation = restaurant['latitude'], restaurant['longitude']
#      print newYorkRestaurantLocation
#      newYorkRestaurantStoreNumber = restaurant['storeNumber']
#      newYorkDistance = vincenty(newYorkPoint, newYorkRestaurantLocation).miles
#      if newYorkDistance <= 100:
#          print newYorkRestaurantLocation, newYorkRestaurantStoreNumber
#
# for j in restaurants:
#     selectedThreeNY = []
#     if restaurant['addressRegion'] == "NY":
#         selectedThreeNY.append(restaurants[0:3])
#     print selectedThreeNY
# json_str = json.dumps(selectedThreeNY)
#
# gmaps = googlemaps.Client(key='KEY')
