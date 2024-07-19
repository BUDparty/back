from rest_framework import serializers

from .models import Word, Chapter, Sentence


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'chapter', 'korean_word', 'north_korean_word', 'is_called', 'is_correct', 'is_collect']

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'accuracy']

class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ['id', 'chapter', 'korean_sentence', 'north_korean_sentence', 'is_called', 'is_correct', 'is_collect']