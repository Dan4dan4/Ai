from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, query_rag

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('query/', query_rag, name='query-rag'),
]
