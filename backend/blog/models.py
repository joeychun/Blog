from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=64)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        related_name = "written_articles",
        on_delete = models.CASCADE,
    )

class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        related_name = "commented_articles",
        on_delete = models.CASCADE,
    )
    content = models.TextField()
    author = models.ForeignKey(
        User,
        related_name = "written_comments",
        on_delete = models.CASCADE,
    )
