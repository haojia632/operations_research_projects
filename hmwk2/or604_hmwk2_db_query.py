from geopy.distance import vincenty
import sqlite3

def calculate_distance(lat1, lon1, lat2, lon2):
    return vincenty((lat1, lon1), (lat2, lon2)).miles


conn = sqlite3.connect('database2.db')
conn.create_function("calculate_distance", 4, calculate_distance)
cursor = conn.cursor()
cursor.execute('''
SELECT A.storeNumber
FROM (
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
) AS A
GROUP BY A.storeNumber
HAVING Max(A.distance) <= 100;
''')

table = cursor.fetchall()
print 'Store numbers:'
for row in table:
    print row

#
# for j in restaurants:
#     selectedThreeNY = []
#     if restaurant['addressRegion'] == "NY":
#         selectedThreeNY.append(restaurants[0:3])
#     print selectedThreeNY
# json_str = json.dumps(selectedThreeNY)
#
# gmaps = googlemaps.Client(key='KEY')
