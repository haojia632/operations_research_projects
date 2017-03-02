from geopy.distance import vincenty
import sqlite3
import pandas as pd 
import numpy as np
import json

def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return vincenty(point1, point2).miles


conn = sqlite3.connect('database2.db')
conn.create_function("calculate_distance", 4, calculate_distance)
cursor = conn.cursor()


df = pd.read_sql_query('''
 SELECT
     Nearby.storeNumber AS storeNumber,
     calculate_distance(Nearby.latitude, Nearby.longitude, NY.latitude, NY.longitude) AS distance
 FROM
     McDonaldsLocations AS Nearby,
     McDonaldsLocations AS NY
 WHERE
     Nearby.state IN ('PA', 'NJ', 'CT', 'RI', 'MA', 'NH', 'VT', 'OH', 'MD', 'DE')
         AND
     NY.state = 'NY'

''', conn)
df.groupby('storeNumber').filter(lambda x: max(x['distance']) <= 100)


#print df['distance'].dtype
#print df
#print(df.head())

#conn.close()

#grouped = df.groupby(['storeNumber'])
#len(grouped)


#conn.execute("SELECT * FROM McdonaldsLocations WHERE state = 'NY'")
#allNY = cursor.fetchall()
#
#
#conn.execute("SELECT * FROM McDonaldsLocation WHERE state = 'NY' LIMIT 3")
#threeNY = cursor.fetchall()
#for row in threeNY:
#    print row
#
#json_str = json.dumps(threeNY)

#
# gmaps = googlemaps.Client(key='KEY')