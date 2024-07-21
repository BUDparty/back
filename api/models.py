from django.db import models

class Chapter(models.Model):
    title = models.CharField(max_length=100)
    def __str__(self):
        return self.title

class Word(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='words', on_delete=models.CASCADE)
    korean_word = models.CharField(max_length=100)
    north_korean_word = models.CharField(max_length=100)
    is_called = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return self.korean_word



