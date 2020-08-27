"""
Step 1: Log Into Youtube 
Step 2: Grab Liked Videos
Step 3: Create a New Playlist
Step 4: Search for Song
Step 5: Add this song to Spotify playlist
"""
import json
import requests
import os 

from secrets import spotify_user_id, spotify_token
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl

from exceptions import ResponseException

class CreatePlaylist:

    def __init__(self):
        self.get_youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    # Step 1: Log Into Youtube
    def get_youtube_client(self):
        """Log Into Youtube, Copied from Youtube Data API"""
        # disable OAuthLib's HTTPS verification when running locally
        # *DO NOT* leave this option enabled in production
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        api_service_name = 'youtube'
        api_version = 'v3'
        client_secrets_file = 'client_secret.json'

        # get credentials and create an API client 
        scopes = ['https://www.googleapis.com/auth/youtube.readonly']
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file,scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

            return youtube_client

    # Step 2: Grab Liked Videos & Creating A Dictionary of Important Song Information 
    def get_liked_videos(self):
        requests = self.get_youtube_client.videos().list(
            part = 'snippet, contentDetails, statistics',
            myRating = 'like'
        )
        response = request.execute()

        # collect each video and get important information
        for item in response['items']:
            video_title = item['snippet']['title']
            youtube_url = 'https://www.youtube.com/watch?v={}'.format(item['id'])

            # use youtube_dl to collect the song name & artist name
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
            song_name = video['track']
            artist = video['artist']

            if song_name is not None and artist is not None:
                # save all important info and skip any missing song and artist 
                self.all_song_info[video_title] = {
                    'youtube_url': youtube_url,
                    'song_name': song_name,
                    'artist': artist,

                    # add the uri, easy to get song to put into playlist 
                    'spotify_uri': self.get_spotify_uri(song_name, artist)
                }

    # Step 3: Create a New Playlist
    def create_playlist(self):
        
        request_body = json.dumps({
            'name': 'Youtube Liked Vids'
            'description': 'All Liked Youtube Videos'
            'public': True
        })

        query = 'https://api.spotify.com/v1/users/{}/playlists'.format(self.user_id)
        response = requests.post(
            query,
            data = request_body,
            headers = {
                'Content-Type':'application/json',
                'Authorization':'Bearer {}'.format(spotify_token)
            }
        )
        response_json = response.json()

        # playlist id
        return response_json['id']

    # Step 4: Search for Song
    def get_spotify_uri(self, song_name, artist):

        query = 'https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20'.format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers = {
                'Content-Type':'application/json',
                'Authorization':'Bearer {}'.format(self.spotify_token)
            }
        )
        response_json = response_json()
        songs = response_json['tracks']['items']

        # only use the first song  
        uri = songs[0]['uri']

        return uri

    # Step 5: Add this song to Spotify playlist
    def add_song_to_playlist(self):
        """Add all liked songs into a new Spotify playlist"""
        # populate our songs dictionary 
        self.get_liked_videos()

        # collect all of uri
        uri = []
        for song, info in self.all_song_info.items():
            uri.append(info['spotify_uri'])

        # create a new playlist 
        playlist_id = self.create_playlist()

        # add all songs into new playlist 
        request_data = json.dumps(uris)

        query = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id)

        response = requests.post(
            query, 
            data = request_data,
            header = {
                'Content-Type':'application/json',
                'Authorization':'Bearer {}'.format(spotify_token)
            }
        )

        # check for valid response status 
        if response.status.code != 200:
            raise ResponseException(response.status.code)

        response_json = response.json()
        return response_json


if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_playlist()