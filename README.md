# saddest-happiest-spotify-songs
a python code that creates a Spotify playlist of the happiest or saddest songs in the user's library

Create a file called config.py with variables: username, scope, redirect_uri, client_id, client_secret.  Assign "user-library-read playlist-read-private, playlist-modify-public" to scope, "http://google.com/" to redirect_uri, and enter personal information for the rest of the variables.

In the command prompt window, run "py get_genre_csv.py sad username" or "py get_genre_csv.py happy username", and insert your username where it says username.  After that, run "py spotify.py username sad" or "py spotify.py username happy", inserting your username where it says username.  After this a sad/happy playlist will be added to your spotify account.  
