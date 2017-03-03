from geopy.distance import vincenty
import sqlite3
from googlemaps import convert
from googlemaps.convert import as_list

# Problem 2 'I will never look at McDonalds the same!' 
def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return vincenty(point1, point2).miles


conn = sqlite3.connect('database2.db')
conn.create_function("calculate_distance", 4, calculate_distance)
cursor = conn.cursor()

cursor.execute('''
SELECT
    A.storeNumber, Max(a.distance)
FROM (
    SELECT
        Nearby.storeNumber AS storeNumber,
        calculate_distance(Nearby.latitude, Nearby.longitude, NY.latitude, NY.longitude) AS distance
    FROM
        McDonaldsLocations AS Nearby,
        McDonaldsLocations AS NY
    WHERE
        Nearby.state IN ('NY', 'PA', 'NJ', 'CT', 'RI', 'MA', 'NH', 'VT', 'OH', 'MD', 'DE')
            AND
        NY.state = 'NY'
) AS A
WHERE distance <= 100
GROUP BY A.storeNumber


''')

results = cursor.fetchall()
        
for row in results:
    print row 


#conn.execute("SELECT * FROM McdonaldsLocations WHERE state = 'NY'")
# allNY = cursor.fetchall()

#conn.execute("SELECT * FROM McDonaldsLocations WHERE state = 'NY' LIMIT 3")
# threeNY = cursor.fetchall()
# for row in allNY:
#     print row
#
#json_str = json.dumps(threeNY)

#
# gmaps = googlemaps.Client(key='KEY')


# gmaps = googlemaps.Client(key='KEY')
