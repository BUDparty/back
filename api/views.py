from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Word, Chapter
from .serializers import WordSerializer, ChapterSerializer
import openai

class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer

    @action(detail=True, methods=['post'])
    def save_word(self, request, pk=None):
        try:
            word = self.get_object()
            word.is_correct = True
            word.save()
            return JsonResponse({'status': '단어가 저장되었습니다'}, json_dumps_params={'ensure_ascii': False})
        except Word.DoesNotExist:
            return JsonResponse({'error': '단어를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer

    @action(detail=True, methods=['get'])
    def words(self, request, pk=None):
        try:
            chapter = self.get_object()
            words = chapter.words.all()
            serializer = WordSerializer(words, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})




