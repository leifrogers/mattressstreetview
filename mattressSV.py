import urllib
import os
import pytumblr
import time
import sqlite3
import codecs
from googleplaces import GooglePlaces
from urllib.request import urlopen
from sqlite3 import Error

database = "mattress"
image_location = r"images/"

# Google Maps key
key = "&key=" + "YOUR_GOOGLE_MAPS_API_KEY"

# Google Places key
google_places_key = 'YOUR_GOOGLE_PLACES_API_KEY'

# tumblr stuff
client = pytumblr.TumblrRestClient(
    '<consumer_key>',
    '<consumer_secret>',
    '<oauth_token>',
    '<oauth_secret>',
)


def the_connection(db_location):

    try:
        connection = sqlite3.connect(db_location)
        return connection
    except Error as e:
        print(e)

    return None


# create a database connection
conn = the_connection(database)
# with conn:
cur = conn.cursor()
cur.execute("select city, state from citystate where searched = 'false' group by city, state ORDER BY RANDOM() LIMIT "
            "10;")
rows = cur.fetchall()
cities = []

for row in rows:
    print(row[0])
    test = "update citystate set searched = 'true' where city = '" + row[0] + "' and state = '" + row[1] + "'"
    print(test)
    cities.append(row[0] + ',' + row[1])
    print(cities)
    cur2 = conn.cursor()
    cur2.execute(test)
    conn.commit()


def get_street(address, save_location):
    base = "https://maps.googleapis.com/maps/api/streetview?size=640x480&location="
    maps_url = base + address.replace(' ', '%20') + key
    the_file = address.replace(',', '').replace('#', '').replace('.', '').replace('/', '').replace(' ', '-') + ".jpg"
    upload_to_tumblr(the_file, maps_url)
    print(maps_url)
    urllib.request.urlretrieve(maps_url, os.path.join(save_location, the_file))


def upload_to_tumblr(the_file, the_source):
    the_caption = 'Mattress! found at ' + the_file.replace('-', ' ').replace('.jpg', '')
    the_tags = ["mattress", "mattress store", "consumerism", "street view", "google", "new aesthetic", "post digital"]
    #uploads to https://mattressmattressmattress.tumblr.com/
    client.create_photo('mattressmattressmattress', state="post", tags=the_tags, caption=the_caption, source=the_source)
    print(the_caption)


# I could be doing a lot more with this library than I'm currently doing but that's out of scope for this, however, it's
# awesome, look it up and use it.
google_places = GooglePlaces(google_places_key)

for city in cities:

    query_result = google_places.nearby_search(location=city, keyword='mattress', radius=5000)
    fileName = city.replace(",", "-") + ".txt"
    file = codecs.open(fileName, 'w', 'utf-8')
    if query_result.has_attributions:
        print(str(query_result.html_attributions))
        file.write(str(query_result.html_attributions))

    for place in query_result.places:
        place.get_details()
        print(str(place.formatted_address))
        get_street(address=str(place.formatted_address), save_location=image_location)
        file.write(str(place.formatted_address) + "\r")

    file.close()
    time.sleep(10)
