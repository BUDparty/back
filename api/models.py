from django.db import models

class Chapter(models.Model):
    title = models.CharField(max_length=100)
    accuracy = models.FloatField(default=0.0)
    def __str__(self):
        return self.title

class Word(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='words', on_delete=models.CASCADE)
    korean_word = models.CharField(max_length=100)
    north_korean_word = models.CharField(max_length=100)
    is_called = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)
    is_collect = models.BooleanField(default=False)
    accuracy = models.FloatField(default=0.0)  # 단어 정확도 추가
    def __str__(self):
        return self.korean_word


class Sentence(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='sentences', on_delete=models.CASCADE)
    korean_sentence = models.CharField(max_length=255)
    north_korean_sentence = models.CharField(max_length=255)
    is_called = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)
    is_collect = models.BooleanField(default=False)
    accuracy = models.FloatField(default=0.0)

    def __str__(self):
        return self.korean_sentence
