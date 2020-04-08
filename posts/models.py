from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.from django.db import models
User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user")
    text = models.TextField()
    created = models.DateTimeField("date published", auto_now_add=True)


class Group(models.Model):
    title = models.CharField(max_length = 200)
    slug = models.SlugField(unique = True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_author")
    conract = models.EmailField
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=True, null=True, related_name="group")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    