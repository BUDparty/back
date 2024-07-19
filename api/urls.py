from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ChapterViewSet, WordViewSet, SentenceViewSet, get_progress, mark_word_as_called, \
    mark_sentence_as_called, get_chapters, get_next_chapter, get_saved_words, get_saved_sentences, save_word, \
    update_word, update_sentence, get_chapter_learning_progress, SentenceListCreate, update_sentence_is_collect, \
    update_sentence_is_called, fetch_progress_data, fetch_incollect_words

router = DefaultRouter()
router.register(r'chapters', ChapterViewSet)
router.register(r'words', WordViewSet)
router.register(r'sentences', SentenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('chapters/<int:pk>/words/', ChapterViewSet.as_view({'get': 'words'}), name='chapter-words'),
    path('chapters/<int:pk>/sentences/', ChapterViewSet.as_view({'get': 'sentences'}), name='chapter-sentences'),
    path('words/<int:pk>/save/', WordViewSet.as_view({'post': 'save_word'})),
    path('sentences/<int:pk>/save/', SentenceViewSet.as_view({'post': 'save_sentence'})),
    path('get_progress/', get_progress, name='get_progress'),
    path('words/<int:word_id>/mark_called/', mark_word_as_called, name='mark_word_as_called'),
    path('sentences/<int:sentence_id>/mark_called/', mark_sentence_as_called, name='mark_sentence_as_called'),
    path('chapters/', get_chapters, name='get_chapters'),
    path('next_chapter/', get_next_chapter, name='get_next_chapter'),
    path('saved_words/', get_saved_words, name='get_saved_words'),
    path('saved_sentences/', get_saved_sentences, name='get_saved_sentences'),
    path('words/<int:word_id>/save/', save_word, name='save_word'),
    path('words/<int:word_id>/update/', update_word, name='update_word'),
    path('sentences/<int:sentence_id>/update/', update_sentence, name='update_sentence'),
    path('words/<int:pk>/update_accuracy/', WordViewSet.as_view({'post': 'update_accuracy'})),
    path('sentences/<int:pk>/update_accuracy/', SentenceViewSet.as_view({'post': 'update_accuracy'})),
    path('chapters/<int:pk>/incollect_words/', ChapterViewSet.as_view({'get': 'incollect_words'}), name='chapter-incollect-words'),
    path('chapters/<int:pk>/incollect_sentences/', ChapterViewSet.as_view({'get': 'incollect_sentences'}), name='chapter-incollect-sentences'),
    path('chapters/<int:pk>/accuracy/', ChapterViewSet.as_view({'get': 'accuracy'}), name='chapter-accuracy'),
    path('chapters/<int:chapter_id>/learning_progress/', get_chapter_learning_progress, name='chapter_learning_progress'),
    path('sentences/', SentenceListCreate.as_view(), name='sentence-list-create'),
    path('sentences/<int:pk>/', update_sentence_is_collect, name='update-sentence-is-collect'),
    path('', include(router.urls)),
    path('sentences/<int:pk>/update/', update_sentence_is_collect),
    path('sentences/<int:pk>/mark_called/', update_sentence_is_called),
    path('get_progress/', fetch_progress_data),
    path('chapters/<int:chapter_id>/incollect_words/', fetch_incollect_words),
    path('sentences/<int:sentence_id>/update/', update_sentence, name='update_sentence'),


]
