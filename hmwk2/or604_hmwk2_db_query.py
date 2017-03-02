from geopy.distance import vincenty
import sqlite3
import pandas

def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return vincenty(point1, point2).miles


conn = sqlite3.connect('database2.db')
conn.create_function("calculate_distance", 4, calculate_distance)
cursor = conn.cursor()

cursor.execute('''
 SELECT
     Nearby.storeNumber AS storeNumber,
     MAX(calculate_distance(Nearby.latitude, Nearby.longitude, NY.latitude, NY.longitude)) AS distance
 FROM
     McDonaldsLocations AS Nearby,
     McDonaldsLocations AS NY
 WHERE
     Nearby.state IN ('PA', 'NJ', 'CT', 'RI', 'MA', 'NH', 'VT', 'OH', 'MD', 'DE', 'NY')
         AND
     NY.state = 'NY'
GROUP BY Nearby.storeNumber

''')

results = cursor.fetchall()
for row in results:
    print row 



# SELECT A.storeNumber
# FROM (
# SELECT
#     Nearby.storeNumber AS storeNumber,
#     calculate_distance(Nearby.latitude, Nearby.longitude, NY.latitude, NY.longitude) AS distance
# FROM
#     McDonaldsLocations AS Nearby,
#     McDonaldsLocations AS NY
# WHERE
#     Nearby.state IN ('PA', 'NJ', 'CT', 'RI', 'MA', 'NH', 'VT', 'OH', 'MD', 'DE')
#         AND
#     NY.state = 'NY'
# ) AS A
# GROUP BY A.storeNumber
# HAVING Max(A.distance) <= 100;



# for j in restaurants:
#     selectedThreeNY = []
#     if restaurant['addressRegion'] == "NY":
#         selectedThreeNY.append(restaurants[0:3])
#     print selectedThreeNY
# json_str = json.dumps(selectedThreeNY)
#
# gmaps = googlemaps.Client(key='KEY')
