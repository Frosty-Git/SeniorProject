from django import forms
    
class OurSearchForm(forms.Form):
    """
    The search bar on the home page.
    """
    term = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}))

class ArtistForm(forms.Form):
    """
    Jame's artist analyzer search bar.
    """
    artist_name = forms.CharField(label='Artist name', max_length=100)

class SongForm(forms.Form):
    """
    Jame's song analyzer search bar.
    """
    song_title = forms.CharField(label='Song title', max_length=100)

# class SurveyForm(forms.Form):
#     artist_name = forms.CharField(label='Artist name', max_length=100)
#     test_hidden_field = forms.CharField(label='Hidden Field', max_length=100)