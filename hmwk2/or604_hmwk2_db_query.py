from geopy.distance import vincenty
import sqlite3
import googlemaps


# Problem 2 'I will never look at McDonalds the same!'

#calculate distance function
def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return vincenty(point1, point2).miles


#Set Database, calculate function and cursor
conn = sqlite3.connect('database2.db')
conn.create_function("calculate_distance", 4, calculate_distance)
cursor = conn.cursor()


#Problem 2
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

hundredMileMcDonaldsresults = cursor.fetchall()

for row in hundredMileMcDonaldsresults:
    print row


#Problem 3, part 1

#Select 3 McDonalds in NY
cursor.execute(''' SELECT latitude,longitude, storeNumber FROM McDonaldsLocations WHERE state = 'NY' LIMIT 3 ''')
threeNYdb = cursor.fetchall()
print threeNYdb

#Find road distance among all three
gmaps = googlemaps.Client(key='AIzaSyDzj7fmLOEAUKnTgF__5ZQU-kKdcqD1zVU')
gmaps.distance_matrix(threeNYdb, threeNYdb, mode="driving")


#Problem 3, part 2

#Build Query to find top 10 closest McDonalds in NY that are closest to the 3 selected 
cursor.execute('''
    SELECT
        NY.storeNumber, three.storeNumber,
        calculate_distance(three.latitude, three.longitude, NY.latitude, NY.longitude) AS distance
    FROM
        McDonaldsLocations AS three,
        McDonaldsLocations AS NY
    WHERE
       three.storeNumber IN (665596, 165697, 268242)
            AND
        NY.state = 'NY'
ORDER BY distance ASC
LIMIT 10''')
tenMcDonaldsResults = cursor.fetchall()

for row in tenMcDonaldsResults:
    print row
