from django.db import models

class Page(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)
    blog_image = models.ImageField(upload_to='photos/blogs', blank=True)

    def __str__(self):
        return self.title
# Create your models here.
