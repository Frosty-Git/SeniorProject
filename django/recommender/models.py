from django.db import models


class Musicdata(models.Model):
    acousticness = models.FloatField()
    artists = models.TextField()
    danceability = models.FloatField()
    duration_ms = models.FloatField()
    energy = models.FloatField()
    explicit = models.FloatField()
    id = models.TextField(primary_key=True)
    instrumentalness = models.FloatField()
    key = models.FloatField()
    liveness = models.FloatField()
    loudness = models.FloatField()
    mode = models.FloatField()
    name = models.TextField()
    popularity = models.FloatField()
    release_date = models.IntegerField()
    speechiness = models.FloatField()
    tempo = models.FloatField()
    valence = models.FloatField()
    year = models.IntegerField()


class GenreArtist(models.Model):
    id = models.TextField(primary_key=True)
    artists = models.TextField()
    acousticness = models.FloatField()
    danceability = models.FloatField()
    duration_ms = models.FloatField()
    energy = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    loudness = models.FloatField()
    speechiness = models.FloatField()
    tempo = models.FloatField()
    valence = models.FloatField()
    popularity = models.FloatField()
    key = models.FloatField()
    mode = models.FloatField()
    count = models.FloatField()
    genres = models.TextField(null=True, blank=True)
    