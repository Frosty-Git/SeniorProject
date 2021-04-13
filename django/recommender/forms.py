from django import forms

class SearchForm(forms.Form):
    artist = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    from_year = forms.IntegerField(required=False)
    to_year = forms.IntegerField(required=False)
    
class OurSearchForm(forms.Form):
    term = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}), required=False)

class ArtistForm(forms.Form):
    artist_name = forms.CharField(label='Artist name', max_length=100)

class SongForm(forms.Form):
    song_title = forms.CharField(label='Song title', max_length=100)

class SurveyForm(forms.Form):
    artist_name = forms.CharField(label='Artist name', max_length=100)
    test_hidden_field = forms.CharField(label='Hidden Field', max_length=100)