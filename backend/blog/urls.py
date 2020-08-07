from django.urls import path
from blog import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('article', views.article, name='article'),
    path('article/<int:id>', views.article_id, name='article_id'),
    path('article/<int:id>/comment', views.article_id_comment, name='article_id_comment'),
    path('comment/<int:id>', views.comment_id, name='comment_id'),
    path('token', views.token, name='token'),
]
