from django.db import models

# Create your models here.
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()  # هنا رح يكون في XSS
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  # تخزين Plaintext = ضعف أمني
