from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from .models import Document
from .serializers import DocumentSerializer
from .rag_pipeline import run_rag_pipeline
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.

# Document CRUD using viewset
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

# RAG query endpoint POST
@api_view(['POST'])
def query_rag(request):
    """
    expects JSON: {"query": "your question"}
    returns LLM answer
    """
    query = request.data.get("query")
    if not query:
        return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

    response = run_rag_pipeline(query)
    return Response({"response": response})


@api_view(['POST'])
def ask_rag(request):

    query = request.data.get("query")

    if not query:
        return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    answer = run_rag_pipeline(query)

    return Response({"answer": answer})

# allows the upload of documents via API
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_document(request):
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    Document.objects.create(
        title=file.name,
        company="Unknown",
        doc_type="uploaded",
        content=file.read().decode("utf-8") 
    )

    return Response({"status": "success"})