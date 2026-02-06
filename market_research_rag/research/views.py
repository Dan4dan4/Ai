from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from .models import Document
from .serializers import DocumentSerializer
from .rag_pipeline import run_rag_pipeline
from rest_framework.parsers import MultiPartParser, FormParser
from PyPDF2  import PdfReader
from datetime import date
import PyPDF2
from django.utils import timezone
import re

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

def extract_text(file):
    """Extract text from .txt or .pdf files"""
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.name.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    else:
        return ""
    

TEMP_DOCS = []

@api_view(["POST"])
def upload_document(request):
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    # extract content
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        content = ""
        for page in reader.pages:
            text = page.extract_text() or ""
            content += text + " "
    else:
        content = file.read().decode("utf-8")

    # clean extra whitespace
    content = re.sub(r'\s+', ' ', content).strip()

    # store in-memory for this session only
    TEMP_DOCS.append({
        "title": file.name,
        "company": "Unknown",
        "doc_type": "uploaded",
        "content": content,
        "date_filed": None  # optional
    })

    return Response({"status": "success"})