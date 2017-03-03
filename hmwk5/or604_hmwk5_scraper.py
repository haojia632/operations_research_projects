from bs4 import BeautifulSoup
import csv
import urllib2
import re
from geopy.geocoders import Nominatim as nom
import json
import sqlite3
# import googlemaps

def reverseGeocode(latitude, longitude):
    geolocator = nom()
    return geolocator.reverse(latitude, longitude)

def getStateDict():
    stateTable = open('state_table.csv')
    stateDict = {}
    for row in csv.reader(stateTable):
        stateName, stateAbrv = row[0], row[1]
        stateDict[stateName] = stateAbrv
    return stateDict

def scrapeRestaurant(location, hdr):
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
        restaurant['streetAddress'] = reverseGeocode(restaurant['latitude'], restaurant['longitude'])
    return restaurant

# Iterate over all states and create an list to hold the location dict
def agreggateRestaurantInfo():
    # Header element so the page does not treat routine as a web bot
    hdr = {'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) \
    Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"}
    i = 0
    csv_headers = ['latitude', 'longitude', 'storeNumber', 'addressLocality', 'addressRegion',
    'streetAddress', 'postalCode']
    # Define Restaurant Chain URL root
    stateRoot = 'https://www.menuism.com/restaurant-locations/dominos-pizza-7144/us/'

    # Import state abreviations
    stateDict = getStateDict()

    with open('dominos-info.csv','w') as output_file:
        dict_writer = csv.DictWriter(output_file, csv_headers)
        dict_writer.writeheader()

        for state in stateDict:
            i += 1
            print i, state
            restaurants_in_state = []
            stateReq = urllib2.Request(stateRoot + stateDict[state], headers=hdr)
            soupState = BeautifulSoup(urllib2.urlopen(stateReq), "lxml")
            storeStateTable = soupState.findAll('ul', {'class':'list-unstyled-links'})

            for storeCode in storeStateTable:
                for storeLink in storeCode.find_all('a'):
                    location = storeLink.get('href')
                    restaurant = scrapeRestaurant(location, hdr)
                    print location, restaurant
                    restaurants_in_state.append(restaurant)

            # Write all restaurants in the current state to CSV
            dict_writer.writerows(restaurants_in_state)

#Save CSV Values in Database
def saveDominosResults():
    conn = sqlite3.connect('database5.db')
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS DominosLocations''')
    c.execute('''CREATE TABLE DominosLocations
    (latitude numeric, longitude numeric, storeNumber int, city text,
    state text, streetAddress varchar,  zip int)''')
    # ['latitude', 'longitude', 'storeNumber', 'addressLocality', 'addressRegion',
    # 'streetAddress', 'postalCode']
    with open ('dominos-info.csv') as g:
        reader = csv.reader(g)
        next(reader, None) # skip header row
        print "saving csv records to database:"
        for i in reader:
            print i
            c.execute("INSERT INTO DominosLocations VALUES (?,?,?,?,?,?,?)", i)
            conn.commit()
    conn.close()


# Call function that agreggates all Dominos information
agreggateRestaurantInfo()

#Call function to save Dominos results to database2
saveDominosResults()
