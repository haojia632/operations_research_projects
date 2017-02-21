# Homework 1
import csv
from bs4 import BeautifulSoup
import urllib2
import datetime
import re
import sqlite3
import time
import schedule

# Import csv of good rides for Magic Kingdom
goodRides = open('goodRides.csv')
goodRides_csv = csv.reader(goodRides)

# Import csv of good rides for Epcot
goodRidesEpcot = open('goodRidesEpcot.csv')
goodRidesEpcot_csv = csv.reader(goodRidesEpcot)


# Convert Magic Kingdom csv file into list
goodRidesList = []
for row in goodRides_csv:
    goodRidesList.append(row[0])

# Convert Epcot csv file into list
goodRidesEpcotList = []
for row in goodRidesEpcot_csv:
    goodRidesEpcotList.append(row[0])

# Function to extract integer from wait time
def extractInteger(waitTime):
    waitString = re.findall(r'(\d+)', waitTime)
    if len(waitString) == 0:
        return None
    else:
        return int(float(waitString[0]))

# Create lines of rides and necessary information for Magic Kingdom
def getRideListMK(rideRows):
    rideList = []
    timeStamp = str(datetime.datetime.now())
    for rideEntry in rideRows:
        entryList = [ "Magic Kingdom", timeStamp ]
        for rideCell in rideEntry.findAll('td'):
            entryList.append(rideCell.text)

        entryList[4] = extractInteger(entryList[4])
        rideList.append(entryList)
    return rideList
# Create lines of rides and necessary information for Epcot
def getRideListEP(rideRows):
    rideList = []
    timeStamp = str(datetime.datetime.now())
    for rideEntry in rideRows:
        entryList = [ "Epcot", timeStamp ]
        for rideCell in rideEntry.findAll('td'):
            entryList.append(rideCell.text)

        entryList[4] = extractInteger(entryList[4])
        rideList.append(entryList)
    return rideList

def webScraperMK():
    # Create soup of Disney World rides page
    url = "http://www.easywdw.com/waits/?&park=mk&sort=time&showOther=true"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    #Test => print soup.prettify()

    # Identify elements of interest in soup
    rideTable = soup.findAll('table', {"width" : "100%"})[1]
    rideRows = rideTable.findAll('tr')
    rideList = getRideListMK(rideRows)

    # Filter based on Good Rides CSV using list comprehension
    goodRideGenerator = (entryList for entryList in rideList if entryList[2] in goodRidesList)


    # Create CSV file of final output based on scraped data
    with open('final_ride_mk.csv', 'wb') as f:
        writer = csv.writer(f)
        for i in goodRideGenerator:
            del i[5] #delete extra column from extra td in html
            writer.writerow(i)

    # Create database and table in sqlite3
    conn = sqlite3.connect('database1.db')
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS MagicKingdomRides''')
    c.execute('''CREATE TABLE MagicKingdomRides
            (parkName text, accessTimestamp datetime, rideName text, rideLocation text, wait int)
            ''')
    with open ('final_ride_mk.csv') as g:
        dbReader = csv.reader(g)
        for i in dbReader:
            c.execute("INSERT INTO MagicKingdomRides VALUES (?,?,?,?,?)", i)
    conn.commit()
    conn.close()

    print "testing 1"

def webScraperEP():
    # Create soup of Disney World rides page
    url = "http://www.easywdw.com/waits/?park=ep"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    #Test => print soup.prettify()

    # Identify elements of interest in soup
    rideTable = soup.findAll('table', {"width" : "100%"})[1]
    rideRows = rideTable.findAll('tr')
    rideList = getRideListEP(rideRows)

    # Filter based on Good Rides CSV using list comprehension
    goodRideGenerator = (entryList for entryList in rideList if entryList[2] in goodRidesEpcotList)


    # Create CSV file of final output based on scraped data
    with open('final_ride_ep.csv', 'wb') as f:
        writer = csv.writer(f)
        for i in goodRideGenerator:
            del i[5] #delete extra column from extra td in html
            writer.writerow(i)

    # Create database and table in sqlite3
    conn = sqlite3.connect('database1.db')
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS EpcotRides''')
    c.execute('''CREATE TABLE EpcotRides
            (parkName text, accessTimestamp datetime, rideName text, rideLocation text, wait int)
            ''')
    with open ('final_ride_ep.csv') as g:
        dbReader = csv.reader(g)
        for i in dbReader:
            c.execute("INSERT INTO EpcotRides VALUES (?,?,?,?,?)", i)
    conn.commit()
    conn.close()

    print "testing 2"

schedule.every(15).minutes.do(webScraperMK)
schedule.every(15).minutes.do(webScraperEP)
while True:
    schedule.run_pending()
    time.sleep(5)
