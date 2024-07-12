from rest_framework import serializers
from .models import Word, Chapter

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'chapter', 'korean_word', 'north_korean_word', 'is_called', 'is_correct']

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title']


