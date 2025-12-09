import os.path
import time

from django.contrib import messages
from django.db.models import Max, Count
from django.shortcuts import render, redirect, reverse
from django.views.generic import View, ListView, DetailView

from .forms import RegisterForm, LoginForm, CommentForm
from .models import User, Movie, Movie_rating, Movie_hot

BASE = os.path.dirname(os.path.abspath(__file__))


# Homepage view
class IndexView(ListView):
    model = Movie
    template_name = 'movie/index.html'
    paginate_by = 15
    context_object_name = 'movies'
    ordering = 'imdb_id'
    page_kwarg = 'p'

    # Return the first 1000 movies
    def get_queryset(self):
        return Movie.objects.filter(imdb_id__lte=1000)

    # Get context data
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IndexView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')  # Paginator object
        page_obj = context.get('page_obj')  # Current page object
        pagination_data = self.get_pagination_data(paginator, page_obj)  # Get pagination data
        context.update(pagination_data)  # Return updated context data
        return context

    # Get pagination data
    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# Popular movies view
class PopularMovieView(ListView):
    model = Movie_hot
    template_name = 'movie/hot.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    def get_queryset(self):
        # Initialize: calculate the top 100 movies with the most ratings and
        # save to database (not recommended to run every time)
        movies = Movie.objects.annotate(nums=Count('movie_rating__score')).order_by('-nums')[:100]
        for movie in movies:
            record = Movie_hot(movie=movie, rating_number=movie.nums)
            record.save()

        hot_movies = Movie_hot.objects.all().values("movie_id")
        movies = (Movie.objects.filter(id__in=hot_movies).annotate(nums=Max('movie_hot__rating_number')).order_by(
            '-nums'))
        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PopularMovieView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# Movie category view
class TagView(ListView):
    model = Movie
    template_name = 'movie/tag.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    # Get data
    def get_queryset(self):
        # No category selected
        if 'genre' not in self.request.GET.dict().keys() or self.request.GET.dict()['genre'] == "":
            movies = Movie.objects.all()
            return movies[100:200]
        # Category selected
        else:
            movies = Movie.objects.filter(genre__name=self.request.GET.dict()['genre'])
            print(movies)
            return movies[:100]

    # Pass data to template
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TagView, self).get_context_data(*kwargs)

        if 'genre' in self.request.GET.dict().keys():
            genre = self.request.GET.dict()['genre']
            context.update({'genre': genre})  # Pass genre information to template

        paginator = context.get('paginator')  # Get paginator object
        page_obj = context.get('page_obj')  # Current page object
        pagination_data = self.get_pagination_data(paginator, page_obj)  # Calculate pagination data
        context.update(pagination_data)  # Pass pagination data to context
        return context

    # Calculate pagination data
    # Purpose is to control the display of pagination buttons, avoiding too many page number buttons, making pagination more concise
    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# Search movie view
class SearchView(ListView):
    model = Movie
    template_name = 'movie/search.html'
    paginate_by = 15
    context_object_name = 'movies'
    page_kwarg = 'p'

    # Get search results
    def get_queryset(self):
        movies = Movie.objects.filter(name__icontains=self.request.GET.dict()['keyword'])
        # self.request.GET.dict()['keyword'] gets the search keyword from the URL
        return movies

    # Pass data to template
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchView, self).get_context_data(*kwargs)
        paginator = context.get('paginator')  # Get paginator object
        page_obj = context.get('page_obj')  # Current page object
        pagination_data = self.get_pagination_data(paginator, page_obj)  # Calculate pagination data
        context.update(pagination_data)  # Update pagination information
        context.update({'keyword': self.request.GET.dict()['keyword']})  # Pass search keyword
        return context

    # Calculate pagination data
    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number  # Get current page number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }


# Register view
class RegisterView(View):
    # get() method: render registration page (register.html)
    def get(self, request):
        return render(request, 'movie/register.html')
    # When users access /register/, Django will call the get() method, returning the registration page (register.html)

    # post() method: process registration form submission, validate and save user information
    def post(self, request):
        form = RegisterForm(request.POST)  # Bind submitted data to form
        if form.is_valid():  # Validate if form is valid
            form.save()  # Save user information to database
            return redirect(reverse('movie:index'))  # Registration successful, redirect to homepage

        else:
            # Form validation failed, redirect to registration page
            errors = form.get_errors()
            for error in errors:
                messages.info(request, error)  # Display error messages
            print(form.errors.get_json_data())  # Print error information in backend
            return redirect(reverse('movie:register'))  # Redirect back to registration page


# Login view
class LoginView(View):
    def get(self, request):
        return render(request, 'movie/login.html')

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            pwd = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            user = User.objects.filter(name=name, password=pwd).first()
            if user:
                if remember:
                    # Set to None, indicating to use global expiration time
                    request.session.set_expiry(None)
                else:
                    # Expire immediately
                    request.session.set_expiry(0)
                # Login successful, store current user id in session as identification
                request.session['user_id'] = user.id
                return redirect(reverse('movie:index'))

            else:
                messages.info(request, 'User name or password is incorrect!')
                return redirect(reverse('movie:login'))
        else:
            errors = form.get_errors()
            for error in errors:
                messages.info(request, error)
            return redirect(reverse('movie:login'))


# Logout, immediately destroy session
def UserLogout(request):
    request.session.set_expiry(-1)
    return redirect(reverse('movie:index'))


# Movie detail view
class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movie/detail.html'
    # Context object name
    context_object_name = 'movie'

    # Override get_context_data method, add rating parameters
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if user is logged in
        login = True
        try:
            user_id = self.request.session['user_id']
        except KeyError as e:
            login = False  # Not logged in

        # Get movie pk (here pk is id)
        pk = self.kwargs['pk']
        movie = Movie.objects.get(pk=pk)

        if login:
            # Already logged in, get current user's rating history
            user = User.objects.get(pk=user_id)

            rating = Movie_rating.objects.filter(user=user, movie=movie).first()
            # Default values
            score = 0
            comment = ''
            if rating:
                score = rating.score
                comment = rating.comment
            context.update({'score': score, 'comment': comment})

        similarity_movies = movie.get_similarity()
        # Get the most similar movies to current movie
        context.update({'similarity_movies': similarity_movies})
        # Check if logged in, don't show rating page if not logged in
        context.update({'login': login})

        return context

    # Accept rating form, pk is the current movie's database primary key id
    def post(self, request, pk):
        form = CommentForm(request.POST)
        if form.is_valid():
            # Get score and comment
            score = form.cleaned_data.get('score')
            comment = form.cleaned_data.get('comment')
            # Get user and movie
            user_id = request.session['user_id']
            user = User.objects.get(pk=user_id)
            movie = Movie.objects.get(pk=pk)

            # Update a record
            rating = Movie_rating.objects.filter(user=user, movie=movie).first()
            if rating:
                # If exists, update
                # print(rating)
                rating.score = score
                rating.comment = comment
                rating.save()
            else:
                # If not exists, add
                rating = Movie_rating(user=user, movie=movie, score=score, comment=comment)
                rating.save()
            messages.info(request, "Review success!")
        else:
            # Form validation failed
            messages.info(request, "The score cannot be empty!")
        return redirect(reverse('movie:detail', args=(pk,)))


# Rating history view
class RatingHistoryView(DetailView):
    model = User
    template_name = 'movie/history.html'
    # Context object name
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        # Add objects here: current user's rated movies history
        context = super().get_context_data(**kwargs)
        user_id = self.request.session['user_id']
        user = User.objects.get(pk=user_id)
        # Get ratings
        ratings = Movie_rating.objects.filter(user=user).order_by('-score')
        context.update({'ratings': ratings})
        return context


# Delete rating comment data
def delete_recode(request, pk):
    movie = Movie.objects.get(pk=pk)
    user_id = request.session['user_id']
    user = User.objects.get(pk=user_id)
    rating = Movie_rating.objects.get(user=user, movie=movie)
    rating.delete()
    messages.info(request, f"delete {movie.name} successfully！")
    # Redirect to rating history
    return redirect(reverse('movie:history', args=(user_id,)))


# Recommend movie view
class RecommendMovieView(ListView):
    model = Movie
    template_name = 'movie/recommend.html'
    paginate_by = 15
    context_object_name = 'movies'
    ordering = 'movie_rating__score'
    page_kwarg = 'p'

    def __init__(self):
        super().__init__()
        # Most similar 20 users
        self.K = 20
        # Recommend 10 movies
        self.N = 10
        # Store current user's rated movies querySet
        self.cur_user_movie_qs = None

    # Get user similarity
    def get_user_sim(self):
        # User similarity dictionary, format is { user_id1:val , user_id2:val , ... }
        user_sim_dct = dict()
        '''Get similarity between users, store in user_sim_dct'''
        # Get current user
        cur_user_id = self.request.session['user_id']
        cur_user = User.objects.get(pk=cur_user_id)
        # Get other users
        other_users = User.objects.exclude(pk=cur_user_id)  # All users except current user

        # Current user's rated movies
        self.cur_user_movie_qs = Movie.objects.filter(user=cur_user)

        # Calculate the number of movies both current user and other users have rated
        for user in other_users:
            # Record number of common interests
            user_sim_dct[user.id] = len(Movie.objects.filter(user=user) & self.cur_user_movie_qs)

        # Sort by key value, return K most similar users (more common rated movies)
        print("user similarity calculated!")
        # Format [ (user, value), (user, value), ... ]
        return sorted(user_sim_dct.items(), key=lambda x: -x[1])[:self.K]

    # Get recommended movies (sorted by similar users' total score)
    def get_recommend_movie(self, user_lst):
        # Movie interest value dictionary, { movie:value, movie:value , ...}
        movie_val_dct = dict()
        # User, similarity
        for user, _ in user_lst:
            # Get movies rated by similar users that are not in current user's rating list, with score
            # field for calculating interest
            movie_set = Movie.objects.filter(user=user).exclude(id__in=self.cur_user_movie_qs).annotate(
                score=Max('movie_rating__score'))
            for movie in movie_set:
                movie_val_dct.setdefault(movie, 0)
                # Accumulate user ratings
                movie_val_dct[movie] += movie.score
        return sorted(movie_val_dct.items(), key=lambda x: -x[1])[:self.N]

    # Get data
    def get_queryset(self):
        s = time.time()
        # Get the most similar K users list
        user_lst = self.get_user_sim()
        # Get recommended movie ids
        movie_lst = self.get_recommend_movie(user_lst)
        # print(movie_lst)
        result_lst = []
        for movie, _ in movie_lst:
            result_lst.append(movie)
        e = time.time()
        print(f"Algorithm recommended time:{e - s}time！")
        return result_lst

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RecommendMovieView, self).get_context_data(*kwargs)
        print(context)
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')
        pagination_data = self.get_pagination_data(paginator, page_obj)
        context.update(pagination_data)
        return context

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
            left_has_more = False
        else:
            left_pages = range(current_page - around_count, current_page)
            left_has_more = True

        if current_page >= paginator.num_pages - around_count - 1:
            right_pages = range(current_page + 1, paginator.num_pages + 1)
            right_has_more = False
        else:
            right_pages = range(current_page + 1, current_page + 1 + around_count)
            right_has_more = True
        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }