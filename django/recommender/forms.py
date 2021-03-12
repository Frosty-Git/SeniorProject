from django import forms

class SearchForm(forms.Form):
    artist = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    from_year = forms.IntegerField(required=False)
    to_year = forms.IntegerField(required=False)

class OurSearchForm(forms.Form):
    term = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}))
    
    priorities = (
        ('Default','Select A Priority'),
        ('Song','Song'),
        ('Artist','Artist'),
        ('Album','Album'),
    )
    priority = forms.MultipleChoiceField(choices=priorities)