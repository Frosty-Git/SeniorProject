# Authors: Tucker & Joe & Katie & Jacelynn
class GenresStack:
    """
    Manages the chosen genres, artists, and songs for the survey.
    We used a custom built url to keep track of what items were chosen
    in the survey form because we used AJAX.
    Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
    """
    def __init__(self, genres_string, artists_string, songs_string):
        """
        Constructor for GenresStack.
        """
        self.genres_stack = str(genres_string)
        self.artists_list = list(artists_string)
        self.songs_list = str(songs_string)
        # These are all the spotify playlist ids for these genres
        self.genres_options = {
            'alternative': '37i9dQZF1DX9GRpeH4CL0S',
            'anime': '37i9dQZF1DWT8aqnwgRt92',
            'blues': '37i9dQZF1DXd9rSDyQguIk',
            'rock': '37i9dQZF1DWXRqgorJj26U',
            'classical' : '37i9dQZF1DWWEJlAGA9gs0',
            'country' : '37i9dQZF1DX1lVhptIYRda',
            'disco' : '37i9dQZF1DX1MUPbVKMgJE',
            'electronic' : '37i9dQZF1DX4dyzvuaRJ0n',
            'emo' : '37i9dQZF1DX9wa6XirBPv8',
            'folk' : '37i9dQZF1DWYV7OOaGhoH0',
            'gospel' : '37i9dQZF1DXcb6CQIjdqKy',
            'grunge' : '37i9dQZF1DX11ghcIxjcjE',
            'hard-rock' : '37i9dQZF1DWWJOmJ7nRx0C',
            'hip-hop' : '37i9dQZF1DX0XUsuxWHRQd',
            'indie' : '37i9dQZF1DX2Nc3B70tvx0',
            'jazz' : '37i9dQZF1DXbITWG1ZJKYt',
            'k-pop' : '37i9dQZF1DX9tPFwDMOaN1',
            'latin' : '37i9dQZF1DX10zKzsJ2jva',
            'metal' : '37i9dQZF1DWTcqUzwhNmKv',
            'opera' : '2PjVPkj4a9kBvQIXaZ6UUt',
            'pop' : '37i9dQZF1DXcBWIGoYBM5M',
            'punk' : '37i9dQZF1DXa9wYJr1oMFq',
            'r-n-b' : '37i9dQZF1DX4SBhb3fqCJd',
            'reggae' : '37i9dQZF1DXbSbnqxMTGx9',
            'soul' : '37i9dQZF1DWULEW2RfoSCi',
        }
        # The key is format for a genre to be used as a genre seed in the
        # for recommendations in the query string, and in the URL "encoded"
        # query string. The value is how the genre will be displayed in HTML.
        self.genres_names = {
            'alternative': 'Alternative',
            'anime': 'Anime',
            'blues': 'Blues',
            'rock': 'Classic Rock',
            'classical' : 'Classical',
            'country' : 'Country',
            'disco' : 'Disco',
            'electronic' : 'Electronic',
            'emo' : 'Emo',
            'folk' : 'Folk',
            'gospel' : 'Gospel',
            'grunge' : 'Grunge',
            'hard-rock' : 'Hard Rock',
            'hip-hop' : 'Hip Hop',
            'indie' : 'Indie',
            'jazz' : 'Jazz',
            'k-pop' : 'K-pop',
            'latin' : 'Latin',
            'metal' : 'Metal',
            'opera' : 'Opera',
            'pop' : 'Pop',
            'punk' : 'Punk',
            'r-n-b' : 'R&B',
            'reggae' : 'Reggae',
            'soul' : 'Soul',
        }

    def pop(self):
        """
        Pops a genre off the stack. We use a query string in the URL to
        represent the stack, so the delimeter in said string is a '*'. Genres 
        are split off around each '*' in the stack.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        if '*' in self.genres_stack:
            genres = self.genres_stack.split('*') # 'rock*pop*country*' becomes ['rock', 'pop', 'country', '']
            # Last result is an empty string, so pop twice
            genres.pop() # ['rock', 'pop', 'country']
            genre_popped = genres.pop()  # 'country'
            new_genres = ""
            
            if len(genres) > 0:
                for genre in genres:
                    new_genres = new_genres + (genre + "*")
                self.genres_stack = new_genres
            else:
                self.genres_stack = "*"    
    
            return genre_popped

        else:
            self.genres_stack = "*"
            return ""

    def push(self, genre):
        """
        Push a genre onto the genre stack.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        self.genres_stack = self.genres_stack + (genre + "*")

    def isEmpty(self):
        """
        Determines if the genre stack is empty.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        result = False
        if len(self.genres_stack) is 0:
            result = True
        return result

    def get_playlist_id(self, genre):
        """
        Get the spotify playlist id associated with a genre from the
        genres_options dictionary
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        return self.genres_options[genre]

    def get_genre_name(self, genre):
        """
        Gets the name of a genre. The name displayed on the webpage is different
        than the name associated with the genre seeds for recommendations. For
        example 'r-n-b' would be displayed as 'R&B'
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        return str(self.genres_names[genre])

    def genresToString(self):
        """
        Converts the genres stack into a string.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        return str(self.genres_stack)

    def artistsToString(self):
        """
        Converts the artists a user selects as part of the survey into our "encoded"
        url query string.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        artists_string = ""
        for artist in list(self.artists_list):
            artists_string = artists_string + (artist + "*")
        return artists_string
    
    def artistsToList(self, artists_string):
        """
        Translates our "encoded" url into a simple list of artists.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        if '*' in artists_string:
            artists = artists_string.split('*')
            # Last result is an empty string, so pop it off
            return artists.pop()

    def songsToString(self):
        """
        Converts the songs a user selects as part of the survey into our "encoded"
        url query string.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        songs_string = ""
        if len(self.songs_list) > 0:
            for song in list(self.songs_list):
                songs_string = songs_string + (song + "*")
        else: 
            songs_string = "*"
        return songs_string
    
    def songsToList(self):
        """
        Translates our "encoded" url into a simple list of songs.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        if '*' in self.songs_list:
            songs = self.songs_list.split('*')
            # Last result is an empty string, so pop it off
            songs = songs[:-1]
            result = songs
            return result

    def extendSongList(self, new_list):
        """
        Adds newly chosen songs from the survey onto our "encoded" 
        song list.
        Last updated: 4/8/21 by Joseph Frost, Jacelynn Duranceau, 
                                Katie Lee, Tucker Elliott
        """
        if '*' == self.songs_list[0]:
            self.songs_list = ""
        for new_song in new_list:
            self.songs_list = self.songs_list + (new_song + "*")
        