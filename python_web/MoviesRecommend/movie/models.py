from django.db import models
from django.db.models import Avg


# Genre table
class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name="type")

    class Meta:
        db_table = 'Genre'
        verbose_name = 'Movie type'
        verbose_name_plural = 'Movie type'

    def __str__(self):
        return self.name


# Movie table
class Movie(models.Model):
    name = models.CharField(max_length=256, verbose_name="Film title")
    imdb_id = models.IntegerField(verbose_name="imdb_id")
    time = models.CharField(max_length=256, blank=True, verbose_name="Time")
    genre = models.ManyToManyField(Genre, verbose_name="Type")
    release_time = models.CharField(max_length=256, blank=True, verbose_name="release_time")
    intro = models.TextField(blank=True, verbose_name="intro")
    director = models.CharField(max_length=256, blank=True, verbose_name="director")
    writers = models.CharField(max_length=256, blank=True, verbose_name="writers")
    actors = models.CharField(max_length=512, blank=True, verbose_name="actors")

    # Similarity between movies.
    # If A → B and B → A have different similarity values, set symmetrical=False.
    movie_similarity = models.ManyToManyField("self", through="Movie_similarity", symmetrical=False,
                                              verbose_name="Similar film")

    class Meta:
        db_table = 'Movie'
        verbose_name = 'Movie information'
        verbose_name_plural = 'Movie information'

    def __str__(self):
        return self.name

    # Get average score of this movie
    def get_score(self):
        result_dct = self.movie_rating_set.aggregate(Avg('score'))  # Format: {'score__avg': 3.125}
        try:
            result = round(result_dct['score__avg'], 1)  # Keep one decimal place
        except TypeError:
            return 0
        else:
            return result

    # Get the rating given by a specific user
    def get_user_score(self, user):
        return self.movie_rating_set.filter(user=user).values('score')

    # Get integer score range (for star display)
    def get_score_int_range(self):
        return range(int(self.get_score()))

    # Get the genre list
    def get_genre(self):
        genre_dct = self.genre.all().values('name')
        genre_lst = []
        for dct in genre_dct.values():
            genre_lst.append(dct['name'])
        return genre_lst

    # Get the most similar movies (default top 5)
    def get_similarity(self, k=5):
        similarity_movies = self.movie_similarity.all()[:k]
        return similarity_movies


# Movie similarity table
class Movie_similarity(models.Model):
    movie_source = models.ForeignKey(Movie, related_name='movie_source',
                                     on_delete=models.CASCADE, verbose_name="Source film")
    movie_target = models.ForeignKey(Movie, related_name='movie_target',
                                     on_delete=models.CASCADE, verbose_name="Target film")
    similarity = models.FloatField(verbose_name="similarity")

    class Meta:
        # Sort by similarity in descending order
        verbose_name = 'Movie_similarity'
        verbose_name_plural = 'Movie_similarity'


# User information table
class User(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="User name")
    password = models.CharField(max_length=256, verbose_name="password")
    email = models.EmailField(unique=True, verbose_name="email")
    rating_movies = models.ManyToManyField(Movie, through="Movie_rating")

    def __str__(self):
        return "<USER:( name: {:},password: {:},email: {:} )>".format(self.name,
                                                                      self.password, self.email)

    class Meta:
        db_table = 'User'
        verbose_name = 'User name'
        verbose_name_plural = 'User name'


# Movie rating table
class Movie_rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, verbose_name="User")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, unique=False, verbose_name="Movie")
    score = models.FloatField(verbose_name="Score")
    comment = models.TextField(blank=True, verbose_name="Comment")

    class Meta:
        db_table = 'Movie_rating'
        verbose_name = 'Movie rating information'
        verbose_name_plural = 'Movie rating information'


# Top 100 hottest movies table
class Movie_hot(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Movie name")
    rating_number = models.IntegerField(verbose_name="Number of graders")

    class Meta:
        db_table = 'Movie_hot'
        verbose_name = 'hottest movie'
        verbose_name_plural = 'hottest movie'


# Commands to apply model changes:
# python manage.py makemigrations
# python manage.py migrate
