from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Word, Chapter
from .serializers import WordSerializer, ChapterSerializer

import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

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



from django.http import JsonResponse
from .models import Word
from django.db.models import Count, Q

def get_progress(request):
    chapters = Word.objects.values('chapter_id').annotate(
        total_words=Count('id'),
        called_words=Count('id', filter=Q(is_called=True)),
        progress=Count('id', filter=Q(is_called=True)) * 100.0 / Count('id')
    )

    progress_data = [
        {
            'chapter_id': chapter['chapter_id'],
            'chapter_title': f'챕터 {chapter["chapter_id"]}',
            'progress': chapter['progress'],
            'total_words': chapter['total_words'],
            'called_words': chapter['called_words']
        }
        for chapter in chapters
    ]

    completed_chapters = sum(1 for chapter in progress_data if chapter['progress'] == 100)
    overall_progress = sum(chapter['progress'] for chapter in progress_data) / len(progress_data) if progress_data else 0

    return JsonResponse({
        'progress_data': progress_data,
        'completed_chapters': completed_chapters,
        'overall_progress': overall_progress
    })




