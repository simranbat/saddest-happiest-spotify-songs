from __future__ import print_function
import pprint
import sys
import os
import subprocess
import json
import spotipy
import spotipy.util as util
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import time
import re
from config import client_id, client_secret, scope, redirect_uri



client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
token = util.prompt_for_user_token(username=sys.argv[2],
                                   scope=scope,
                                   redirect_uri=redirect_uri,
                                   client_id=client_id,
                                   client_secret=client_secret)

if len(sys.argv) > 2:
    mood = sys.argv[1]
    sp = spotipy.Spotify(auth=token)
else:
    sys.exit()

def get_playlist_audio_features(username, playlist_id, sp):
    offset = 0
    songs = []
    items = []
    ids = []
    while True:
        content = sp.user_playlist_tracks(username, playlist_id, fields=None, limit=100, offset=offset, market=None)
        songs += content['items']
        if content['next'] is not None:
            offset += 100
        else:
            break

    for i in songs:
        ids.append(i['track']['id'])

    index = 0
    audio_features = []
    while index < len(ids):
        audio_features += sp.audio_features(ids[index:index + 50])
        index += 50

    features_list = []
    for features in audio_features:
        try:
            features_list.append([features['energy'], features['liveness'],
                              features['tempo'], features['speechiness'],
                              features['acousticness'], features['instrumentalness'],
                                  features['danceability'],
                              features['loudness'], features['valence'], features['uri']])
        except:
            continue

    df = pd.DataFrame(features_list, columns=['energy', 'liveness',
                                              'tempo', 'speechiness',
                                              'acousticness', 'instrumentalness',
                                              'danceability',
                                              'loudness',
                                              'valence', 'uri'])
    return df


mooddata = pd.DataFrame([])
results = sp.search(mood, limit=20, type='playlist')
results = ",".join(("{}={}".format(*i) for i in results.items()))
uri = re.findall("(spotify:user:spotify:\w+:\w+)", results)
#print(uri)
for item in uri:
    username = item.split(':')[2]
    playlist_id = item.split(':')[4]
    mooddata = mooddata.append(get_playlist_audio_features("spotify", playlist_id, sp=spotipy.Spotify(auth=token)))

mooddata.to_csv('{}.csv'.format(mood), index=False)
print(mooddata)
