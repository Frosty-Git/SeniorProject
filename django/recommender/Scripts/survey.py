# Authors: Tucker & Joe & Katie
class GenresStack:
    
    def __init__(self):
        self.genres_stack = ""
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

    def pop(self):
        return self.genres_stack.pop()

    def push(self, genre):
        self.genres_stack.append("/" + genre)

    def isEmpty(self):
        result = False
        if len(self.genres_stack) is 0:
            result = True
        return result

    def get_playlist_id(self, genre):
        return self.genres_options[genre]