from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    ChapterViewSet, WordViewSet, SentenceViewSet, get_progress, mark_word_as_called,
    mark_sentence_as_called, get_chapters, get_next_chapter, get_saved_words,
    get_saved_sentences, save_word, update_word, update_sentence, get_chapter_learning_progress,
    SentenceListCreate, update_sentence_is_collect, update_sentence_is_called,
    fetch_progress_data, fetch_incollect_words, update_sentence_accuracy_and_text, get_api_key, service_account,
    typecast_speak, chat_with_assistant
)

# DefaultRouter를 사용하여 ViewSet을 자동으로 라우팅합니다.
router = DefaultRouter()
router.register(r'chapters', ChapterViewSet)  # 'chapters' 엔드포인트를 ChapterViewSet에 연결합니다.
router.register(r'words', WordViewSet)        # 'words' 엔드포인트를 WordViewSet에 연결합니다.
router.register(r'sentences', SentenceViewSet) # 'sentences' 엔드포인트를 SentenceViewSet에 연결합니다.

# urlpatterns 리스트는 URL 패턴과 View를 매핑합니다.
urlpatterns = [
    path('', include(router.urls)),  # router.urls를 포함하여 기본 엔드포인트를 처리합니다.
    path('chapters/<int:pk>/words/', ChapterViewSet.as_view({'get': 'words'}), name='chapter-words'),  # 특정 챕터의 단어를 가져오는 엔드포인트입니다.
    path('chapters/<int:pk>/sentences/', ChapterViewSet.as_view({'get': 'sentences'}), name='chapter-sentences'),  # 특정 챕터의 문장을 가져오는 엔드포인트입니다.
    path('words/<int:pk>/save/', WordViewSet.as_view({'post': 'save_word'})),  # 단어를 저장하는 엔드포인트입니다.
    path('sentences/<int:pk>/save/', SentenceViewSet.as_view({'post': 'save_sentence'})),  # 문장을 저장하는 엔드포인트입니다.
    path('get_progress/', get_progress, name='get_progress'),  # 전체 진행 상황을 가져오는 엔드포인트입니다.
    path('words/<int:word_id>/mark_called/', mark_word_as_called, name='mark_word_as_called'),  # 단어를 호출된 상태로 마크하는 엔드포인트입니다.
    path('sentences/<int:sentence_id>/mark_called/', mark_sentence_as_called, name='mark_sentence_as_called'),  # 문장을 호출된 상태로 마크하는 엔드포인트입니다.
    path('chapters/', get_chapters, name='get_chapters'),  # 모든 챕터를 가져오는 엔드포인트입니다.
    path('next_chapter/', get_next_chapter, name='get_next_chapter'),  # 다음 챕터를 가져오는 엔드포인트입니다.
    path('saved_words/', get_saved_words, name='get_saved_words'),  # 저장된 단어들을 가져오는 엔드포인트입니다.
    path('saved_sentences/', get_saved_sentences, name='get_saved_sentences'),  # 저장된 문장들을 가져오는 엔드포인트입니다.
    path('words/<int:word_id>/save/', save_word, name='save_word'),  # 단어를 저장하는 엔드포인트입니다.
    path('words/<int:word_id>/update/', update_word, name='update_word'),  # 단어를 업데이트하는 엔드포인트입니다.
    path('sentences/<int:sentence_id>/update/', update_sentence, name='update_sentence'),  # 문장을 업데이트하는 엔드포인트입니다.
    path('words/<int:pk>/update_accuracy/', WordViewSet.as_view({'post': 'update_accuracy'})),  # 단어의 정확도를 업데이트하는 엔드포인트입니다.
    path('sentences/<int:pk>/update_accuracy/', SentenceViewSet.as_view({'post': 'update_accuracy'})),  # 문장의 정확도를 업데이트하는 엔드포인트입니다.
    path('chapters/<int:pk>/incollect_words/', ChapterViewSet.as_view({'get': 'incollect_words'}), name='chapter-incollect-words'),  # 특정 챕터의 틀린 단어들을 가져오는 엔드포인트입니다.
    path('chapters/<int:pk>/incollect_sentences/', ChapterViewSet.as_view({'get': 'incollect_sentences'}), name='chapter-incollect-sentences'),  # 특정 챕터의 틀린 문장들을 가져오는 엔드포인트입니다.
    path('chapters/<int:pk>/accuracy/', ChapterViewSet.as_view({'get': 'accuracy'}), name='chapter-accuracy'),  # 특정 챕터의 정확도를 가져오는 엔드포인트입니다.
    path('chapters/<int:chapter_id>/learning_progress/', get_chapter_learning_progress, name='chapter_learning_progress'),  # 특정 챕터의 학습 진행도를 가져오는 엔드포인트입니다.
    path('sentences/', SentenceListCreate.as_view(), name='sentence-list-create'),  # 문장을 생성하는 엔드포인트입니다.
    path('sentences/<int:pk>/', update_sentence_is_collect, name='update-sentence-is-collect'),  # 문장의 is_collect 상태를 업데이트하는 엔드포인트입니다.
    path('sentences/<int:pk>/mark_called/', update_sentence_is_called),  # 문장의 is_called 상태를 업데이트하는 엔드포인트입니다.
    path('get_progress/', fetch_progress_data),  # 전체 진행 데이터를 가져오는 엔드포인트입니다.
    path('chapters/<int:chapter_id>/incollect_words/', fetch_incollect_words),  # 특정 챕터의 틀린 단어들을 가져오는 엔드포인트입니다.
    path('sentences/<int:sentence_id>/update/', update_sentence, name='update_sentence'),  # 문장을 업데이트하는 엔드포인트입니다.
    path('next_chapter/', get_next_chapter, name='next_chapter'),
    path('get_progress/', get_progress, name='get_progress'),
    path('sentences/<int:sentence_id>/update_accuracy_and_text/', views.update_sentence_accuracy_and_text),
    path('chapters/<int:chapter_id>/evaluation_results/', views.evaluation_results, name='evaluation_results'),
    path('get-api-key/', get_api_key, name='get_api_key'),
    path('service-account/', service_account, name='service_account'),
    path('typecast-speak/', typecast_speak, name='typecast_speak'),
    path('chat-with-assistant/', chat_with_assistant, name='chat_with_assistant'),
]
