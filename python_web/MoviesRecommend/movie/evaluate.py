import sys
import os
import random
import time
from collections import defaultdict
import django
import pandas as pd
import numpy as np
import xgboost as xgb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Movie_recommendation_system.settings")
django.setup()

from django.db.models import Max
from movie.models import Movie, Movie_rating, User

# get user ratings
def get_user_ratings():
    ratings = Movie_rating.objects.all()
    print(f" user rating numbers: {ratings.count()} ")
    user_ratings = defaultdict(dict)
    for r in ratings:
        user_ratings[r.user_id][r.movie_id] = r.score
    return user_ratings

# split training and test sets
def train_test_split(user_ratings, test_ratio=0.2):
    train, test = defaultdict(dict), defaultdict(dict)
    for user, movies in user_ratings.items():
        items = list(movies.items())
        random.shuffle(items)
        split = int(len(items) * (1 - test_ratio))
        for m, s in items[:split]:
            train[user][m] = s
        for m, s in items[split:]:
            test[user][m] = s
    return train, test

# the basic UserCF
def user_cf_recommend(user_id, train, K=10, N=10):
    target_ratings = train[user_id]
    sims = []
    for uid, ur in train.items():
        if uid == user_id:
            continue
        common = set(ur.keys()) & set(target_ratings.keys())
        sims.append((uid, len(common)))
    sims.sort(key=lambda x: -x[1])
    top_k = sims[:K]

    rec_scores = defaultdict(float)
    for uid, _ in top_k:
        for m, s in train[uid].items():
            if m not in target_ratings:
                rec_scores[m] += s
    return sorted(rec_scores, key=rec_scores.get, reverse=True)[:N]

# Pearson
def pearson_recommend(user_id, train, K=10, N=10):
    def pearson(r1, r2):
        common = set(r1.keys()) & set(r2.keys())
        if len(common) < 2:
            return 0
        avg1 = sum(r1[i] for i in common) / len(common)
        avg2 = sum(r2[i] for i in common) / len(common)
        num, denom1, denom2 = 0, 0, 0
        for i in common:
            a, b = r1[i] - avg1, r2[i] - avg2
            num += a * b
            denom1 += a * a
            denom2 += b * b
        if denom1 == 0 or denom2 == 0:
            return 0
        return num / (denom1 ** 0.5 * denom2 ** 0.5)

    target = train[user_id]
    sims = [(uid, pearson(target, ur)) for uid, ur in train.items() if uid != user_id]
    sims = [(uid, sim) for uid, sim in sims if sim > 0]
    sims.sort(key=lambda x: -x[1])
    top_k = sims[:K]

    rec_scores, weight = defaultdict(float), defaultdict(float)
    for uid, sim in top_k:
        for m, s in train[uid].items():
            if m not in target:
                rec_scores[m] += sim * s
                weight[m] += abs(sim)
    for m in rec_scores:
        rec_scores[m] /= weight[m]
    return sorted(rec_scores, key=rec_scores.get, reverse=True)[:N]

# XGBoost
def xgb_recommend(user_id, train, N=10, candidate_limit=300, train_limit=10000):
    data = []
    for uid, ratings in train.items():
        for mid, s in ratings.items():
            data.append({'user_id': uid, 'movie_id': mid, 'score': s, 'feat': mid % 10})
    df = pd.DataFrame(data)

    if train_limit is not None and len(df) > train_limit:
        df = df.sample(train_limit)

    df_train = df[df['user_id'] != user_id]
    X_train = df_train[['user_id', 'movie_id', 'feat']]
    y_train = df_train['score']
    dtrain = xgb.DMatrix(X_train, label=y_train)

    params = {'objective': 'rank:pairwise', 'eta': 0.1, 'max_depth': 4, 'verbosity': 0}
    model = xgb.train(params, dtrain, num_boost_round=15)

    user_rated = set(train[user_id].keys())
    all_candidates = Movie.objects.exclude(id__in=user_rated)
    if candidate_limit is not None:
        all_candidates = all_candidates.order_by('?')[:candidate_limit]

    test_data = pd.DataFrame([
        {'user_id': user_id, 'movie_id': m.id, 'feat': m.id % 10}
        for m in all_candidates
    ])
    dtest = xgb.DMatrix(test_data[['user_id', 'movie_id', 'feat']])
    preds = model.predict(dtest)
    test_data['pred'] = preds
    return test_data.sort_values(by='pred', ascending=False)['movie_id'].tolist()[:N]

# Hybrid
def hybrid_recommend(user_id, train, K=10, N=10, alpha=0.5):
    def pearson(r1, r2):
        common = set(r1.keys()) & set(r2.keys())
        if len(common) < 2:
            return 0
        avg1 = sum(r1[i] for i in common) / len(common)
        avg2 = sum(r2[i] for i in common) / len(common)
        num, denom1, denom2 = 0, 0, 0
        for i in common:
            a, b = r1[i] - avg1, r2[i] - avg2
            num += a * b
            denom1 += a * a
            denom2 += b * b
        if denom1 == 0 or denom2 == 0:
            return 0
        return num / (denom1 ** 0.5 * denom2 ** 0.5)

    user_ratings = train[user_id]
    sims = [(uid, pearson(user_ratings, ur)) for uid, ur in train.items() if uid != user_id]
    sims = [(uid, sim) for uid, sim in sims if sim > 0]
    sims.sort(key=lambda x: -x[1])
    top_k = sims[:K]

    user_cf_scores = defaultdict(float)
    sim_sum = defaultdict(float)
    for uid, sim in top_k:
        for m, s in train[uid].items():
            if m not in user_ratings:
                user_cf_scores[m] += sim * s
                sim_sum[m] += abs(sim)
    for m in user_cf_scores:
        user_cf_scores[m] /= sim_sum[m]

    #  # Extract all tags of the movies the user has rated
    rated_movies = Movie.objects.filter(id__in=user_ratings.keys()).prefetch_related('genre')
    tag_scores = defaultdict(int)
    for movie in rated_movies:
        for tag in movie.genre.all():
            tag_scores[tag.id] += 1

    # Only extract relevant candidate movies to avoid repeated queries
    item_cf_scores = defaultdict(float)
    for tag_id, count in tag_scores.items():
        related = Movie.objects.filter(genre__id=tag_id).exclude(id__in=user_ratings)
        for m in related:
            item_cf_scores[m.id] += count

    final_scores = defaultdict(float)
    all_movies = set(user_cf_scores) | set(item_cf_scores)
    for m in all_movies:
        u = user_cf_scores.get(m, 0)
        i = item_cf_scores.get(m, 0)
        final_scores[m] = alpha * u + (1 - alpha) * i

    return sorted(final_scores, key=final_scores.get, reverse=True)[:N]

# Precision@K
def precision_at_k(recommended, test_set, k=10):
    if not recommended:
        return 0
    hits = len(set(recommended[:k]) & set(test_set))
    return hits / k

# Recall@K
def recall_at_k(recommended, test_set, k=10):
    if not recommended:
        return 0
    hits = len(set(recommended[:k]) & set(test_set))
    return hits / len(test_set) if len(test_set) else 0

# F1-Score@K
def f1_at_k(recommended, test_set, k=10):
    precision = precision_at_k(recommended, test_set, k)
    recall = recall_at_k(recommended, test_set, k)
    if precision + recall == 0:
        return 0
    return 2 * precision * recall / (precision + recall)

# Main evaluation function
def evaluate_all_methods():
    print("Start evaluating recommendation algorithms...\n")
    user_ratings = get_user_ratings()
    print(f" Number of users: {len(user_ratings)}\n")
    train, test = train_test_split(user_ratings)

    methods = {
        'UserCF': user_cf_recommend,
        'PearsonCF': pearson_recommend,
        'XGBoost': xgb_recommend,
        'HybridCF': hybrid_recommend
    }

    for name, func in methods.items():
        print(f"Evaluating: {name}")
        total_precision = 0
        total_recall = 0
        total_f1 = 0
        user_count = 0

        for idx, user_id in enumerate(test):
            if name == 'XGBoost' and idx >= 300:
                break  # only  evaluate the first 300 users for XGBoost

            if name == 'XGBoost':
                recommended = func(user_id, train, N=10, candidate_limit=300, train_limit=8000)
            else:
                recommended = func(user_id, train)

            actual = list(test[user_id].keys())
            precision = precision_at_k(recommended, actual)
            recall = recall_at_k(recommended, actual)
            f1 = f1_at_k(recommended, actual)

            total_precision += precision
            total_recall += recall
            total_f1 += f1
            user_count += 1

        avg_precision = total_precision / user_count if user_count else 0
        avg_recall = total_recall / user_count if user_count else 0
        avg_f1 = total_f1 / user_count if user_count else 0

        print(f"{name} Precision@10: {avg_precision:.4f}")
        print(f"{name} Recall@10: {avg_recall:.4f}")
        print(f"{name} F1-Score@10: {avg_f1:.4f}\n")

if __name__ == '__main__':
    evaluate_all_methods()
