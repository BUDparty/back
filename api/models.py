from django.db import models
# Chapter 모델은 학습 챕터를 나타냅니다.
class Chapter(models.Model):
    title = models.CharField(max_length=100)  # 챕터의 제목을 나타내는 필드입니다.
    accuracy = models.FloatField(default=0.0)  # 챕터의 정확도를 나타내는 필드입니다. 기본값은 0.0입니다.

    def __str__(self):
        return self.title  # 객체를 문자열로 표현할 때, 챕터의 제목을 반환합니다.

# Word 모델은 각 챕터의 단어를 나타냅니다.
class Word(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='words', on_delete=models.CASCADE)  # 단어가 속한 챕터와의 외래키 관계입니다.
    korean_word = models.CharField(max_length=100)  # 한국어 단어를 나타내는 필드입니다.
    north_korean_word = models.CharField(max_length=100)  # 북한어 단어를 나타내는 필드입니다.
    is_called = models.BooleanField(default=False)  # 단어가 호출되었는지 여부를 나타내는 필드입니다. 기본값은 False입니다.
    is_correct = models.BooleanField(default=False)  # 단어가 올바르게 맞춰졌는지 여부를 나타내는 필드입니다. 기본값은 False입니다.
    is_collect = models.BooleanField(default=False)  # 단어가 수집되었는지 여부를 나타내는 필드입니다. 기본값은 False입니다.
    accuracy = models.FloatField(default=0.0)  # 단어의 정확도를 나타내는 필드입니다. 기본값은 0.0입니다.

    def __str__(self):
        return self.korean_word  # 객체를 문자열로 표현할 때, 한국어 단어를 반환합니다.

class Sentence(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='sentences', on_delete=models.CASCADE)
    korean_sentence = models.TextField()
    north_korean_sentence = models.TextField()
    is_collect = models.BooleanField(default=False)
    is_called = models.BooleanField(default=False)
    accuracy = models.FloatField(default=0.0)
    recognized_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.korean_sentence


class AppSentence(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    korean_sentence = models.TextField()
    north_korean_sentence = models.TextField()
    is_called = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)
    is_collect = models.BooleanField(default=False)
    accuracy = models.FloatField(null=True, blank=True)
    recognized_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.korean_sentence
