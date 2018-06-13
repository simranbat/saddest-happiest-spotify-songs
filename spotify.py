from __future__ import print_function
import sys
import spotipy
import spotipy.util as util
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
from config import scope, redirect_uri, client_id, client_secret
from sklearn.preprocessing import scale
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

#authorization
client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
token = util.prompt_for_user_token(username=sys.argv[1],
                                   scope=scope,
                                   redirect_uri=redirect_uri,
                                   client_id=client_id,
                                   client_secret=client_secret)

if len(sys.argv) > 2:
    username = sys.argv[1]
    genre = sys.argv[2]
    if genre != "happy" and genre != "sad":
        print("add 'happy' or 'sad' argument")
        sys.exit()
    sp = spotipy.Spotify(auth=token)
else:
    print("add two arguments: username and genre ('happy' or 'sad')")
    sys.exit()


#get audio features for all songs in user's library
def get_library_audio_features(sp):
    offset = 0
    songs = []
    ids = []
    while True:
        content = sp.current_user_saved_tracks(limit=50, offset=offset)
        songs += content['items']
        if content['next'] is not None:
            offset += 50
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
                              features['time_signature'], features['danceability'],
                              features['key'], features['duration_ms'],
                              features['loudness'], features['valence'],
                              features['mode'], features['type'],
                              features['uri']])
        except:
            continue

    df = pd.DataFrame(features_list, columns=['energy', 'liveness',
                                              'tempo', 'speechiness',
                                              'acousticness', 'instrumentalness',
                                              'time_signature', 'danceability',
                                              'key', 'duration_ms', 'loudness',
                                              'valence', 'mode', 'type', 'uri'])
    return df


songs = get_library_audio_features(sp=spotipy.Spotify(auth=token))
songs.to_csv('{}.csv'.format(username), index=False)


#logistic regression machine learning algorithm
happy = pd.read_csv("happy.csv")
happy = happy[['energy', 'liveness', 'tempo', 'speechiness', 'instrumentalness', 'danceability', 'valence', 'acousticness', 'loudness']]
happy = happy.assign(genre=True)
sad = pd.read_csv("sad.csv")
sad = sad[['energy', 'liveness', 'tempo', 'speechiness', 'instrumentalness', 'danceability', 'valence', 'acousticness', 'loudness']]
sad = sad.assign(genre=False)
library = songs
library = library[['energy', 'liveness', 'tempo', 'speechiness', 'instrumentalness', 'danceability', 'valence', 'acousticness', 'loudness']]
frames = [happy, sad]
data = pd.concat(frames)

genre = pd.get_dummies(data['genre'], drop_first=True)
data.drop(['genre'], axis=1,inplace=True)
data = pd.concat([data, genre], axis=1)

subset_data = data.ix[:,(0, 1, 2, 3, 4, 5, 6, 7, 8)].values
y = data.ix[:,9].values
X = scale(subset_data)
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=.5, random_state=50)

LogReg = LogisticRegression()
LogReg.fit(X_train,y_train)
y_pred = LogReg.predict(X_test)

library1 = scale(library)
predictions = LogReg.predict_proba(library1)
predictions = pd.DataFrame(predictions)
library.loc[:, 'predictions'] = predictions[1]

og_data = songs
og_data.loc[:,'predictions'] = library['predictions']
og_data = og_data.sort_values(['predictions'])
sad = og_data[:25]
happy = og_data[-25:]


#create playlist
sp.trace=False
genre = sys.argv[2]
playlist = sp.user_playlist_create(username, name= genre + " playlist")
playlists = sp.user_playlists(username)
id = playlists['items'][0]['uri']
uri_list = []
if genre == "sad":
    for uri in sad['uri']:
        uri_list.append(uri)
    sp.user_playlist_add_tracks(username, playlist_id=id, tracks=uri_list)
else:
    for uri in happy['uri']:
        uri_list.append(uri)
    sp.user_playlist_add_tracks(username, playlist_id=id, tracks=uri_list)
