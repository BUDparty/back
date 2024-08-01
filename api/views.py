import json
import logging
import os
import time

import requests
from django.shortcuts import render
from django.conf import settings

from django.shortcuts import get_object_or_404
from .models import Sentence, Word, Chapter
from rest_framework import generics, viewsets
from django.core import serializers
from django.db.models import Count, Q, Avg, Case, When, IntegerField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .serializers import WordSerializer, ChapterSerializer, SentenceSerializer

# WordViewSet은 Word 모델과 관련된 API 요청을 처리합니다.
class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()  # 모든 Word 객체를 쿼리합니다.
    serializer_class = WordSerializer  # WordSerializer를 사용하여 직렬화합니다.

    # 특정 챕터에서 is_collect가 False인 단어들을 반환합니다.
    @action(detail=True, methods=['get'])
    def incollect_words(self, request, pk=None):
        try:
            chapter = self.get_object()
            words = chapter.words.filter(is_collect=False)
            serializer = WordSerializer(words, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 단어를 저장된 상태로 업데이트합니다.
    @action(detail=True, methods=['post'])
    def save_word(self, request, pk=None):
        try:
            word = self.get_object()
            word.is_correct = True
            word.save()
            return JsonResponse({'status': '단어가 저장되었습니다'}, json_dumps_params={'ensure_ascii': False})
        except Word.DoesNotExist:
            return JsonResponse({'error': '단어를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 단어의 is_collect 상태를 업데이트합니다.
    @action(detail=True, methods=['post'])
    def update_is_collect(self, request, pk=None):
        try:
            word = self.get_object()
            is_collect = request.data.get('is_collect', None)
            if is_collect is not None:
                word.is_collect = bool(is_collect)
                word.save()
                return JsonResponse({'status': 'is_collect updated'}, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({'error': 'is_collect not provided'}, status=400, json_dumps_params={'ensure_ascii': False})
        except Word.DoesNotExist:
            return JsonResponse({'error': '단어를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 단어의 정확도를 업데이트합니다.
    @action(detail=True, methods=['post'])
    def update_accuracy(self, request, pk=None):
        try:
            word = self.get_object()
            accuracy = request.data.get('accuracy', 0.0)
            word.accuracy = accuracy
            word.save()
            return JsonResponse({'status': '단어 정확도가 업데이트되었습니다'}, json_dumps_params={'ensure_ascii': False})
        except Word.DoesNotExist:
            return JsonResponse({'error': '단어를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

# ChapterViewSet은 Chapter 모델과 관련된 API 요청을 처리합니다.
class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()  # 모든 Chapter 객체를 쿼리합니다.
    serializer_class = ChapterSerializer  # ChapterSerializer를 사용하여 직렬화합니다.

    # 특정 챕터의 모든 문장을 반환합니다.
    @action(detail=True, methods=['get'])
    def sentences(self, request, pk=None):
        try:
            chapter = self.get_object()
            sentences = chapter.sentences.all()
            serializer = SentenceSerializer(sentences, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 특정 챕터의 모든 단어를 반환합니다.
    @action(detail=True, methods=['get'])
    def words(self, request, pk=None):
        try:
            chapter = self.get_object()
            words = chapter.words.all()
            serializer = WordSerializer(words, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 특정 챕터에서 is_collect가 False인 단어들을 반환합니다.
    @action(detail=True, methods=['get'])
    def incollect_words(self, request, pk=None):
        try:
            chapter = self.get_object()
            words = chapter.words.filter(is_collect=False)
            serializer = WordSerializer(words, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 특정 챕터의 정확도를 계산하여 반환합니다.
    @action(detail=True, methods=['get'])
    def accuracy(self, request, pk=None):
        try:
            chapter = self.get_object()
            words = chapter.words.all()
            total_words = words.count()
            collect_words = words.filter(is_collect=True).count()
            accuracy = (collect_words / total_words) * 100 if total_words > 0 else 0
            return JsonResponse({'accuracy': accuracy}, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

# 전체 진행 상황을 반환하는 함수입니다.
def get_progress(request):
    chapters = Chapter.objects.all()
    progress_data = []

    for chapter in chapters:
        words = Word.objects.filter(chapter=chapter)
        total_words = words.count()
        called_words = words.filter(is_called=True).count()
        correct_words = words.filter(is_collect=True).count()
        progress = (called_words / total_words) * 100 if total_words > 0 else 0
        accuracy = (correct_words / total_words) * 100 if total_words > 0 else 0

        progress_data.append({
            'chapter_id': chapter.id,
            'chapter_title': chapter.title,
            'progress': progress,
            'accuracy': accuracy,
            'total_words': total_words,
            'called_words': called_words
        })

    completed_chapters = sum(1 for chapter in progress_data if chapter['progress'] == 100)
    overall_progress = sum(chapter['accuracy'] for chapter in progress_data) / len(progress_data) if progress_data else 0

    return JsonResponse({
        'progress_data': progress_data,
        'completed_chapters': completed_chapters,
        'overall_progress': overall_progress
    })

# 단어를 호출된 상태로 업데이트하는 함수입니다.
@csrf_exempt
def mark_word_as_called(request, word_id):
    if request.method == 'POST':
        try:
            word = Word.objects.get(id=word_id)
            word.is_called = True
            word.save()
            return JsonResponse({'status': 'success'})
        except Word.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Word not found'}, status=404)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

# 모든 챕터와 진행 상황을 반환하는 함수입니다.
def get_chapters(request):
    chapters = Chapter.objects.all()
    response_data = []
    for chapter in chapters:
        words = Word.objects.filter(chapter=chapter)
        total_words = words.count()
        called_words = words.filter(is_called=True).count()
        progress = (called_words / total_words) * 100 if total_words > 0 else 0
        response_data.append({
            'id': chapter.id,
            'title': chapter.title,
            'progress': progress,
        })
    return JsonResponse(response_data, safe=False)

# 문장을 호출된 상태로 업데이트하는 함수입니다.
@csrf_exempt
def mark_sentence_as_called(request, sentence_id):
    if request.method == 'POST':
        try:
            sentence = Sentence.objects.get(id=sentence_id)
            sentence.is_called = True
            sentence.save()
            return JsonResponse({'status': 'success'})
        except Sentence.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Sentence not found'}, status=404)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

# 저장된 문장을 반환하는 함수입니다.
@api_view(['GET'])
def get_saved_sentences(request):
    saved_sentences = Sentence.objects.filter(is_correct=True)
    serializer = SentenceSerializer(saved_sentences, many=True)
    return Response(serializer.data)

# 문장의 is_collect 상태를 업데이트하는 함수입니다.
@csrf_exempt
def update_sentence(request, sentence_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sentence = Sentence.objects.get(pk=sentence_id)
            sentence.is_collect = data.get('is_collect', sentence.is_collect)
            sentence.save()
            return JsonResponse({'status': 'success'}, status=200)
        except Sentence.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sentence not found'}, status=404)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

# 다음 챕터를 반환하는 함수입니다.
def get_next_chapter(request):
    chapters = Chapter.objects.all()
    for chapter in chapters:
        words = Word.objects.filter(chapter=chapter)
        total_words = words.count()
        called_words = words.filter(is_called=True).count()
        progress = (called_words / total_words) * 100 if total_words > 0 else 0
        if progress < 100:
            return JsonResponse({'id': chapter.id, 'title': chapter.title})
    return JsonResponse({'id': chapters.last().id, 'title': chapters.last().title})

# 저장된 단어를 반환하는 함수입니다.
@csrf_exempt
def fetch_saved_words(request):
    if request.method == 'GET':
        saved_words = Word.objects.filter(is_correct=True)
        data = serializers.serialize('json', saved_words)
        return JsonResponse(data, safe=False)

# 단어를 저장된 상태로 업데이트하는 함수입니다.
@csrf_exempt
def save_word(request, word_id):
    try:
        word = Word.objects.get(pk=word_id)
        word.saved = True
        word.save()
        return JsonResponse({'status': 'success'}, status=200)
    except Word.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Word not found'}, status=404)

# 저장된 단어를 반환하는 함수입니다.
@api_view(['GET'])
def get_saved_words(request):
    saved_words = Word.objects.filter(is_correct=True)
    serializer = WordSerializer(saved_words, many=True)
    return Response(serializer.data)

# 단어의 is_collect 상태를 업데이트하는 함수입니다.
@csrf_exempt
def update_word(request, word_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            word = Word.objects.get(pk=word_id)
            word.is_collect = data.get('is_collect', word.is_collect)
            word.save()
            return JsonResponse({'status': 'success'}, status=200)
        except Word.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Word not found'}, status=404)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

# SentenceViewSet은 Sentence 모델과 관련된 API 요청을 처리합니다.
class SentenceViewSet(viewsets.ModelViewSet):
    queryset = Sentence.objects.all()  # 모든 Sentence 객체를 쿼리합니다.
    serializer_class = SentenceSerializer  # SentenceSerializer를 사용하여 직렬화합니다.

    # 특정 챕터에서 is_collect가 False인 문장들을 반환합니다.
    @action(detail=True, methods=['get'])
    def incollect_sentences(self, request, pk=None):
        try:
            chapter = self.get_object()
            sentences = chapter.sentences.filter(is_collect=False)
            serializer = SentenceSerializer(sentences, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 문장을 저장된 상태로 업데이트합니다.
    @action(detail=True, methods=['post'])
    def save_sentence(self, request, pk=None):
        try:
            sentence = self.get_object()
            sentence.is_correct = True
            sentence.save()
            return JsonResponse({'status': '문장이 저장되었습니다'}, json_dumps_params={'ensure_ascii': False})
        except Sentence.DoesNotExist:
            return JsonResponse({'error': '문장을 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 문장의 is_collect 상태를 업데이트합니다.
    @action(detail=True, methods=['post'])
    def update_is_collect(self, request, pk=None):
        try:
            sentence = self.get_object()
            is_collect = request.data.get('is_collect', None)
            if is_collect is not None:
                sentence.is_collect = bool(is_collect)
                sentence.save()
                return JsonResponse({'status': 'is_collect updated'}, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({'error': 'is_collect not provided'}, status=400, json_dumps_params={'ensure_ascii': False})
        except Sentence.DoesNotExist:
            return JsonResponse({'error': '문장을 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    # 문장의 정확도를 업데이트합니다.
    @action(detail=True, methods=['post'])
    def update_accuracy(self, request, pk=None):
        try:
            sentence = self.get_object()
            accuracy = request.data.get('accuracy', 0.0)
            sentence.accuracy = accuracy
            sentence.save()
            return JsonResponse({'status': '문장 정확도가 업데이트되었습니다'}, json_dumps_params={'ensure_ascii': False})
        except Sentence.DoesNotExist:
            return JsonResponse({'error': '문장을 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

# 특정 챕터의 학습 진행도를 반환하는 함수입니다.
@api_view(['GET'])
def get_chapter_learning_progress(request, chapter_id):
    try:
        chapter = Chapter.objects.get(id=chapter_id)
        words = Word.objects.filter(chapter=chapter)
        sentences = Sentence.objects.filter(chapter=chapter)

        total_words = words.count()
        called_words = words.filter(is_called=True).count()
        word_progress = (called_words / total_words) * 100 if total_words > 0 else 0

        total_sentences = sentences.count()
        called_sentences = sentences.filter(is_called=True).count()
        sentence_progress = (called_sentences / total_sentences) * 100 if total_sentences > 0 else 0

        overall_progress = (word_progress + sentence_progress) / 2

        word_serializer = WordSerializer(words, many=True)
        sentence_serializer = SentenceSerializer(sentences, many=True)

        return JsonResponse({
            'progress': overall_progress,
            'words': word_serializer.data,
            'sentences': sentence_serializer.data
        })
    except Chapter.DoesNotExist:
        return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404)

# Sentence 모델의 리스트를 생성하고 조회하는 API 뷰입니다.
class SentenceListCreate(generics.ListCreateAPIView):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

    def get_queryset(self):
        chapter_id = self.request.query_params.get('chapterId', None)
        if chapter_id is not None:
            return self.queryset.filter(chapter__id=chapter_id)
        return self.queryset

# 문장의 is_collect 상태를 업데이트하는 API 뷰입니다.
@api_view(['PATCH'])
def update_sentence_is_collect(request, pk):
    try:
        sentence = Sentence.objects.get(pk=pk)
    except Sentence.DoesNotExist:
        return Response({'error': 'Sentence not found'}, status=404)

    sentence.is_collect = request.data.get('isCollect', sentence.is_collect)
    sentence.save()
    return Response(SentenceSerializer(sentence).data)

# 문장의 is_called 상태를 업데이트하는 API 뷰입니다.
@api_view(['POST'])
def update_sentence_is_called(request, pk):
    try:
        sentence = Sentence.objects.get(pk=pk)
        sentence.is_called = True
        sentence.save()
        return Response({'status': 'success'})
    except Sentence.DoesNotExist:
        return Response({'status': 'error', 'message': 'Sentence not found'}, status=404)

# 전체 진행 데이터를 반환하는 API 뷰입니다.
@api_view(['GET'])
def fetch_progress_data(request):
    # 진행 데이터 계산 로직을 구현하세요.
    progress_data = {
        'completedChapters': 5,  # 예시 값
        'overallProgress': 85,  # 예시 값
        'progressData': [
            # 예시 데이터
            {'chapterId': 1, 'chapterTitle': 'Chapter 1', 'progress': 75},
            {'chapterId': 2, 'chapterTitle': 'Chapter 2', 'progress': 80},
        ]
    }
    return Response(progress_data)

# 특정 챕터에서 is_collect가 False인 단어들을 반환하는 API 뷰입니다.
@api_view(['GET'])
def fetch_incollect_words(request, chapter_id):
    try:
        words = Word.objects.filter(chapter_id=chapter_id, is_collect=False)
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)
    except Word.DoesNotExist:
        return Response({'status': 'error', 'message': 'Words not found'}, status=404)

# 문장의 상태를 업데이트하는 API 뷰입니다.
@api_view(['PATCH'])
def update_sentence(request, sentence_id):
    try:
        sentence = Sentence.objects.get(pk=sentence_id)
    except Sentence.DoesNotExist:
        return Response({'status': 'error', 'message': 'Sentence not found'}, status=404)

    data = request.data
    is_correct = data.get('is_correct', sentence.is_correct)
    is_collect = data.get('is_collect', sentence.is_collect)

    sentence.is_correct = is_correct
    sentence.is_collect = is_collect
    sentence.save()

    serializer = SentenceSerializer(sentence)
    return Response(serializer.data, {'status': 'success'})



logger = logging.getLogger(__name__)

@api_view(['PUT'])
def update_sentence_accuracy_and_text(request, sentence_id):
    logger.debug(f'Received request for sentence_id: {sentence_id}')
    try:
        sentence = get_object_or_404(Sentence, id=sentence_id)
    except Sentence.DoesNotExist:
        logger.error(f'Sentence with id {sentence_id} not found')
        return JsonResponse({'status': 'error', 'message': 'Sentence not found'}, status=404)

    if request.method == 'PUT':
        data = request.data
        logger.debug(f'Request data: {data}')
        accuracy = data.get('accuracy', None)
        recognized_text = data.get('recognized_text', None)

        if accuracy is None or recognized_text is None:
            logger.error('Invalid data: accuracy or recognized_text is missing')
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

        try:
            sentence.accuracy = accuracy
            sentence.recognized_text = recognized_text
            sentence.save()
            logger.debug(f'Sentence updated successfully: {sentence}')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f'Error saving data: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@api_view(['GET'])
def fetch_evaluation_results(request, chapter_id):
    sentences = Sentence.objects.filter(chapter_id=chapter_id)
    serializer = SentenceSerializer(sentences, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def evaluation_results(request, chapter_id):
    sentences = Sentence.objects.filter(chapter_id=chapter_id)
    serializer = SentenceSerializer(sentences, many=True)
    return Response(serializer.data)




@api_view(['GET'])
def get_api_key(request):
    logger.debug('Received request for API key')
    api_key = settings.API_KEY
    logger.debug(f'Returning API key: {api_key}')
    return Response({'api_key': api_key})


def service_account(request):
    file_path = os.path.join(os.path.dirname(__file__), 'service_account.json')
    with open(file_path) as f:
        data = json.load(f)
    return JsonResponse(data)




TYPECAST_API_URL_ACTOR = 'https://typecast.ai/api/actor'
TYPECAST_API_URL_SPEAK = 'https://typecast.ai/api/speak'

@api_view(['POST'])
def typecast_speak(request):
    try:
        data = json.loads(request.body)
        text = data.get('text')

        headers = {
            'Authorization': f'Bearer {settings.TYPECAST_API_KEY}'
        }

        # get my actor
        response = requests.get(TYPECAST_API_URL_ACTOR, headers=headers)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to get actor'}, status=500)

        my_actors = response.json().get('result', [])
        if not my_actors:
            return JsonResponse({'error': 'No actors found'}, status=500)

        my_first_actor = my_actors[0]
        my_first_actor_id = my_first_actor['actor_id']

        # request speech synthesis
        response = requests.post(TYPECAST_API_URL_SPEAK, headers=headers, json={
            'text': text,
            'lang': 'auto',
            'actor_id': my_first_actor_id,
            'xapi_hd': True,
            'model_version': 'latest'
        })
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to request speech synthesis'}, status=500)

        speak_url = response.json()['result']['speak_v2_url']

        # polling the speech synthesis result
        for _ in range(120):
            response = requests.get(speak_url, headers=headers)
            ret = response.json()['result']
            # audio is ready
            if ret['status'] == 'done':
                audio_url = ret['audio_download_url']
                return JsonResponse({'audio_url': audio_url}, status=200)
            else:
                time.sleep(1)

        return JsonResponse({'error': 'Audio synthesis timed out'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)