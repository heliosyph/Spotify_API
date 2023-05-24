from requests import post, get
from dotenv import load_dotenv

import os
import base64
import json

load_dotenv()

# for security reasons, we want to have our credentials stored away
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


# through get SEARCH -> artist
def search_for_artist(token, artist_name):
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist,album&limit=1"
    headers = get_auth_header(token)

    # query = f"?q={artist_name}&type=artist&limit=1"
    # query_url = url + query
    # result = get(query_url, headers=headers)

    result = get(url, headers=headers)

    # [outer][inner]
    artist = json.loads(result.content)["artists"]["items"]

    if len(artist) == 0:
        print("No artist with this name exists...")
        return None

    albums = json.loads(result.content)["albums"]["items"]

    # combine both
    combined_result = {"artists": artist, "albums": albums}

    return combined_result
    # print(combined_result)


# through get Artists --> top tracks AND top albums
def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)

    result = get(url, headers=headers)

    top_tracks = json.loads(result.content)["tracks"]

    return top_tracks


# limited to 10 unique
def get_albums_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?country=US&limit=15&include_groups=album"
    headers = get_auth_header(token)

    result = get(url, headers=headers)

    top_albums = json.loads(result.content)["items"]

    return top_albums


def get_related_artists(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"

    headers = get_auth_header(token)

    result = get(url, headers=headers)
    related_artists = json.loads(result.content)["artists"]

    return related_artists


# beginning of main code-------
# gives a long list of information pertaining to the artist
token = get_token()


# followers, genres, id, name, popularity, type
search_result = search_for_artist(token, "Artist_Name_Here_From_User_Input")


# -- For search_for_artist
artists = search_result["artists"]
albums = search_result["albums"]

print("Here's your requested artist:", artists[0]["name"])
print()

market_length = len(albums[0]["available_markets"])

print(
    artists[0]["name"],
    "has a popularity of",
    artists[0]["popularity"],
    "and has",
    market_length,
    "available markets in: ",
)

for album in albums:
    print(album["available_markets"])

print()

print("--- Top Tracks ---")
# this is a long value
artist_id = artists[0]["id"]

# to get a messy compilation of artist's information within the "tracks" tag
songs = get_songs_by_artist(token, artist_id)


# to show a nicer list of the songs
for idx, song in enumerate(songs):
    name = song["name"]
    release_date = song["album"]["release_date"]
    print(f"{idx +1}. {name} (Release Date: {release_date})")
print()


print("--- Top Album ---")
print(f"{albums[0]['name']}")


print()
top_albums = get_albums_by_artist(token, artist_id)

print("--- Top Albums ---")
unique_names = set()
count = 0
for idx, top_album in enumerate(top_albums):
    album_name = top_album["name"]

    if album_name not in unique_names:
        count = count + 1
        unique_names.add(album_name)
        print(f"{count}.{album_name}")


print()

print(f"Here are {artists[0]['name']}'s related artists ---")

related_artists = get_related_artists(token, artist_id)

for idx, related_artist in enumerate(related_artists):
    print(f"{idx+1}. {related_artists[idx]['name']}")
