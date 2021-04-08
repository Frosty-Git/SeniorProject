# Authors: Tucker & Joe & Katie
class GenresStack:
    def __init__(self, genres_string, artists_string):
        self.genres_stack = str(genres_string)
        self.artists_list = list(artists_string)
        self.songs_list = []
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
        if '*' in self.genres_stack:
            genres = self.genres_stack.split('*') # 'rock*pop*country*' becomes ['rock', 'pop', 'country', '']
            print("Genres " + str(genres))
            # Last result is an empty string, so pop twice
            genres.pop() # ['rock', 'pop', 'country']
            genre_popped = genres.pop()  # 'country'
            print("Popped " + genre_popped)
            self.genre_stack = ""
            for genre in genres:
                self.genre_stack = self.genre_stack + (genre + "*")
            
            return genre_popped

        else:
            return ""

    def push(self, genre):
        self.genres_stack = self.genres_stack + (genre + "*")

    def isEmpty(self):
        result = False
        if len(self.genres_stack) is 0:
            result = True
        return result

    def get_playlist_id(self, genre):
        return self.genres_options[genre]

    def get_genre_name(self, genre):
        return str(self.genres_names[genre])

    def genresToString(self):
        return str(self.genres_stack)

    def artistsToString(self):
        artists_string = ""
        for artist in list(self.artists_list):
            artists_string = artists_string + (artist + "*")
        return artists_string