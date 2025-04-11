import pandas as pd
import requests
import base64
import time

# === CONFIGURE HERE ===
CLIENT_ID = 'f415fe6c370a4a7d8dc28e972536b0fd'
CLIENT_SECRET = 'b0a2bf5b118b47c6a58e60f8721d5c64'
INPUT_CSV = 'spotify-2023.csv'
OUTPUT_CSV = 'spotify-2023-with-art.csv'


def get_access_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {b64_auth_str}"},
        data={"grant_type": "client_credentials"}
    )
    return response.json().get("access_token")


def search_album_art(track, artist, token):
    query = f"track:{track} artist:{artist}"
    url = f"https://api.spotify.com/v1/search?q={requests.utils.quote(query)}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    items = response.json().get("tracks", {}).get("items", [])
    if items:
        images = items[0]['album']['images']
        return images[0]['url'] if images else None
    return None


def add_album_art_column(input_csv, output_csv, client_id, client_secret):
    df = pd.read_csv(input_csv,encoding="ISO-8859-1")
    access_token = get_access_token(client_id, client_secret)

    art_urls = []
    for index, row in df.iterrows():
        track = row['track_name']
        artist = row['artist(s)_name']
        print(f"Searching: {track} by {artist}")
        try:
            art_url = search_album_art(track, artist, access_token)
        except Exception as e:
            print(f"Error on row {index}: {e}")
            art_url = None
        art_urls.append(art_url)
        time.sleep(0.2)  # Avoid rate limits

    df['album_art_url'] = art_urls
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"\n✅ Done! Saved to {output_csv}")


# === RUN SCRIPT ===
add_album_art_column(INPUT_CSV, OUTPUT_CSV, CLIENT_ID, CLIENT_SECRET)
