from rest_framework import serializers
from .models import Chapter, Word, Sentence, AppSentence

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'

class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = '__all__'

class AppSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSentence
        fields = '__all__'