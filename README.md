# Movie Recommendation System

A Django web app that recommends movies with user-based collaborative filtering (User-CF) on the MovieLens dataset. Users can browse, search, rate and review movies, and get a personal top-10 list based on what similar users liked.

Group coursework project, University of Liverpool, 2025.

## Features

- **Browse**: home page, top-100 most-rated movies, filter by genre, search by title
- **Accounts**: register, log in, log out (session based)
- **Rate and review**: give a movie a score and a comment, view or delete your rating history
- **Movie detail page**: metadata, average score, and the most similar movies
- **Personal recommendations**: a top-10 list computed with User-CF
- **Offline evaluation**: a script that compares four recommendation methods with Precision@10, Recall@10 and F1@10

## How the recommendation works

The live recommendation page is `RecommendMovieView` in [`movie/views.py`](python_web/MoviesRecommend/movie/views.py).

1. **Find similar users.** For every other user, count how many movies both of you have rated. That count is the similarity.
2. **Keep the top K.** Sort by similarity and keep the 20 most similar users (`K = 20`).
3. **Collect candidates.** Take the movies those users rated that you have not rated yet.
4. **Score and rank.** Add up the neighbours' ratings for each candidate and return the 10 highest (`N = 10`).

The "similar movies" block on the detail page reads precomputed item-to-item similarity from the `Movie_similarity` table.

## Offline evaluation

[`movie/evaluate.py`](python_web/MoviesRecommend/movie/evaluate.py) splits each user's ratings 80/20 into train and test, then scores four methods on the held-out ratings:

| Method | Idea |
| --- | --- |
| `UserCF` | Similarity = number of co-rated movies (same as the live page) |
| `PearsonCF` | Similarity = Pearson correlation of ratings, weighted average of neighbours' scores |
| `XGBoost` | Pairwise ranking model (`rank:pairwise`) trained on rating rows |
| `HybridCF` | Pearson User-CF blended with a genre-overlap score (`alpha = 0.5`) |

It prints Precision@10, Recall@10 and F1@10 for each method.

## Tech stack

- **Backend**: Python, Django 3.2
- **Database**: MySQL (through PyMySQL)
- **Frontend**: Django templates, Bootstrap, jQuery
- **Evaluation**: pandas, NumPy, XGBoost

## Project structure

```
python_web/MoviesRecommend/
├── manage.py
├── Movie_recommendation_system/   # project settings and root URLs
├── movie/
│   ├── models.py                  # Genre, Movie, User, Movie_rating, Movie_similarity, Movie_hot
│   ├── views.py                   # pages and the User-CF recommendation
│   ├── evaluate.py                # offline comparison of four methods
│   ├── forms.py, urls.py, admin.py
│   └── static/movie/
│       ├── info/                  # MovieLens CSV files
│       └── poster/                # movie posters
├── templates/movie/               # HTML pages
└── static/                        # Bootstrap, CSS, JS
```

## Getting started

### Prerequisites

- Python 3.9+
- MySQL 8

### Setup

```bash
git clone https://github.com/miaaa-z/movie_recommendation.git
cd movie_recommendation/python_web/MoviesRecommend

python -m venv .venv
source .venv/bin/activate
pip install "Django==3.2.*" pymysql pandas numpy xgboost
```

Create the database:

```sql
CREATE DATABASE db_movie_recommend CHARACTER SET utf8mb4;
```

Set your own MySQL user and password in `Movie_recommendation_system/settings.py` under `DATABASES`, then create the tables and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/movie/.

### Data

The CSV files in `movie/static/movie/info/` hold the dataset:

| File | Rows | Content |
| --- | --- | --- |
| `movies.csv` | 9,742 | MovieLens movie id, title, genres |
| `ratings.csv` | 100,836 | Ratings from 610 users: user id, movie id, rating, timestamp |
| `info.csv` | 9,742 | Movie details: runtime, release date, intro, director, writers, cast |
| `movie_similarity.csv` | 97,240 | Precomputed movie-to-movie similarity |

These need to be loaded into the MySQL tables before the pages show any movies. The import step is not scripted in this repository yet.

### Run the evaluation

With the database loaded:

```bash
python movie/evaluate.py
```

## Roadmap

- Add `requirements.txt` and a management command that imports the CSV files
- Read the secret key and database credentials from environment variables
- Store passwords with Django's password hashers
- Cache each user's recommendation list so it is not recomputed on every page load

## Data source

Ratings and movie list come from the [MovieLens](https://grouplens.org/datasets/movielens/) latest-small dataset by GroupLens Research.

> F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems 5, 4, Article 19.
