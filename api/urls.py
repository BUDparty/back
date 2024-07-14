from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views import ChapterViewSet, WordViewSet



router = DefaultRouter()
router.register(r'chapters', ChapterViewSet)
router.register(r'words', WordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('chapters/<int:pk>/words/', ChapterViewSet.as_view({'get': 'words'}), name='chapter-words'),
    path('words/<int:pk>/save/', WordViewSet.as_view({'post': 'save_word'})),

]