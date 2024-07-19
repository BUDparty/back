import json


from .models import Sentence
from rest_framework import generics
from django.core import serializers
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Avg, Case, When, IntegerField



from .models import Word, Chapter, Sentence
from .serializers import WordSerializer, ChapterSerializer, SentenceSerializer


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer


    @action(detail=True, methods=['get'])
    def incollect_words(self, request, pk=None):
        try:
            chapter = self.get_object()
            words = chapter.words.filter(is_collect=False)
            serializer = WordSerializer(words, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    @action(detail=True, methods=['post'])
    def save_word(self, request, pk=None):
        try:
            word = self.get_object()
            word.is_correct = True
            word.save()
            return JsonResponse({'status': '단어가 저장되었습니다'}, json_dumps_params={'ensure_ascii': False})
        except Word.DoesNotExist:
            return JsonResponse({'error': '단어를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

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

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer



    @action(detail=True, methods=['get'])
    def sentences(self, request, pk=None):
        try:
            chapter = self.get_object()
            sentences = chapter.sentences.all()
            serializer = SentenceSerializer(sentences, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    @action(detail=True, methods=['get'])
    def words(self, request, pk=None):
        try:
            chapter = self.get_object()
            words = chapter.words.all()
            serializer = WordSerializer(words, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    @action(detail=True, methods=['get'])
    def incollect_words(self, request, pk=None):
        try:
            chapter = self.get_object()
            words = chapter.words.filter(is_collect=False)
            serializer = WordSerializer(words, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

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


@api_view(['GET'])
def get_saved_sentences(request):
    saved_sentences = Sentence.objects.filter(is_correct=True)
    serializer = SentenceSerializer(saved_sentences, many=True)
    return Response(serializer.data)


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

@csrf_exempt
def fetch_saved_words(request):
    if request.method == 'GET':
        saved_words = Word.objects.filter(is_correct=True)
        data = serializers.serialize('json', saved_words)
        return JsonResponse(data, safe=False)

@csrf_exempt
def save_word(request, word_id):
    try:
        word = Word.objects.get(pk=word_id)
        word.saved = True
        word.save()
        return JsonResponse({'status': 'success'}, status=200)
    except Word.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Word not found'}, status=404)

@api_view(['GET'])
def get_saved_words(request):
    saved_words = Word.objects.filter(is_correct=True)
    serializer = WordSerializer(saved_words, many=True)
    return Response(serializer.data)


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
class SentenceViewSet(viewsets.ModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

    @action(detail=True, methods=['get'])
    def incollect_sentences(self, request, pk=None):
        try:
            chapter = self.get_object()
            sentences = chapter.sentences.filter(is_collect=False)
            serializer = SentenceSerializer(sentences, many=True)
            return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '챕터를 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

    @action(detail=True, methods=['post'])
    def save_sentence(self, request, pk=None):
        try:
            sentence = self.get_object()
            sentence.is_correct = True
            sentence.save()
            return JsonResponse({'status': '문장이 저장되었습니다'}, json_dumps_params={'ensure_ascii': False})
        except Sentence.DoesNotExist:
            return JsonResponse({'error': '문장을 찾을 수 없습니다'}, status=404, json_dumps_params={'ensure_ascii': False})

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


class SentenceListCreate(generics.ListCreateAPIView):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

    def get_queryset(self):
        chapter_id = self.request.query_params.get('chapterId', None)
        if chapter_id is not None:
            return self.queryset.filter(chapter__id=chapter_id)
        return self.queryset

@api_view(['PATCH'])
def update_sentence_is_collect(request, pk):
    try:
        sentence = Sentence.objects.get(pk=pk)
    except Sentence.DoesNotExist:
        return Response({'error': 'Sentence not found'}, status=404)

    sentence.is_collect = request.data.get('isCollect', sentence.is_collect)
    sentence.save()
    return Response(SentenceSerializer(sentence).data)

@api_view(['POST'])
def update_sentence_is_called(request, pk):
    try:
        sentence = Sentence.objects.get(pk=pk)
        sentence.is_called = True
        sentence.save()
        return Response({'status': 'success'})
    except Sentence.DoesNotExist:
        return Response({'status': 'error', 'message': 'Sentence not found'}, status=404)


@api_view(['GET'])
def fetch_progress_data(request):
    # Implement your progress calculation logic here
    progress_data = {
        'completedChapters': 5,  # Example value
        'overallProgress': 85,  # Example value
        'progressData': [
            # Example data
            {'chapterId': 1, 'chapterTitle': 'Chapter 1', 'progress': 75},
            {'chapterId': 2, 'chapterTitle': 'Chapter 2', 'progress': 80},
        ]
    }
    return Response(progress_data)



@api_view(['GET'])
def fetch_incollect_words(request, chapter_id):
    try:
        words = Word.objects.filter(chapter_id=chapter_id, is_collect=False)
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)
    except Word.DoesNotExist:
        return Response({'status': 'error', 'message': 'Words not found'}, status=404)



@api_view(['PATCH'])
def update_sentence(request, sentence_id):
    try:
        sentence = Sentence.objects.get(pk=sentence_id)
    except Sentence.DoesNotExist:
        return Response({'status': 'error', 'message': 'Sentences not found'}, status=404)

    data = request.data
    is_correct = data.get('is_correct', sentence.is_correct)
    is_collect = data.get('is_collect', sentence.is_collect)

    sentence.is_correct = is_correct
    sentence.is_collect = is_collect
    sentence.save()

    serializer = SentenceSerializer(sentence)
    return Response(serializer.data, {'status': 'success'})