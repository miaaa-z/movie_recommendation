import os
import django
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 添加 python_web 到路径
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MoviesRecommend.Movie_recommendation_system.settings")
django.setup()

from movie.models import User, Movie_rating, Movie
from movie.views import RecommendMovieView

# Precision@K 计算
def precision_at_k(recommended, actual, k=10):
    if not recommended:
        return 0
    hits = len(set(recommended[:k]) & set(actual))
    return hits / k

# 模拟评估某个用户（你可以换成数据库中真实存在的 user_id）
def test_user(user_id):
    view = RecommendMovieView()
    # 伪造 request 和 session
    class DummyRequest:
        session = {'user_id': user_id}
    view.request = DummyRequest()

    # 获取推荐结果
    recommended_movies = view.get_queryset()
    recommended_ids = [movie.id for movie in recommended_movies]

    # 获取该用户实际评分过的电影（真实“喜欢”的电影）
    actual_rated = list(Movie_rating.objects.filter(user_id=user_id).values_list('movie_id', flat=True))

    p = precision_at_k(recommended_ids, actual_rated)
    print(f"✅ 用户 {user_id} 的推荐精度 Precision@10 = {p:.4f}")

if __name__ == '__main__':
    # 使用你数据库里实际存在的 user_id（你可以改成别的）
    test_user(1)
