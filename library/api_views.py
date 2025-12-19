from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Novel, Chapter
from .serializers import NovelListSerializer, NovelDetailSerializer, ChapterSerializer

@api_view(['GET'])
def novel_list(request):
    """
    API List Novel dengan Paginasi, Search, dan Filter.
    Output: JSON berisi count, next, previous, dan results.
    """
    query = request.GET.get('q')
    genre = request.GET.get('genre')
    
    # Ambil semua novel, urutkan dari yang terbaru
    novels = Novel.objects.all().order_by('-uploaded_at')

    # Logika Filter & Search
    if query:
        novels = novels.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if genre:
        novels = novels.filter(genre__iexact=genre)

    # Aktifkan Paginasi (Halaman 1, 2, 3...)
    paginator = PageNumberPagination()
    paginator.page_size = 12 # Bebas atur mau berapa per load
    result_page = paginator.paginate_queryset(novels, request)

    # Pakai Serializer RINGAN (NovelListSerializer)
    serializer = NovelListSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def novel_detail(request, pk):
    """Mengambil detail lengkap satu novel beserta chapter-nya"""
    novel = get_object_or_404(Novel, pk=pk)
    # Pakai Serializer LENGKAP (NovelDetailSerializer)
    serializer = NovelDetailSerializer(novel)
    return Response(serializer.data)

@api_view(['GET'])
def chapter_detail(request, pk):
    """Mengambil isi teks chapter"""
    chapter = get_object_or_404(Chapter, pk=pk)
    serializer = ChapterSerializer(chapter)
    data = serializer.data
    data['content'] = chapter.content
    
    # Navigasi Smart (ID chapter sebelum dan sesudahnya)
    next_chap = Chapter.objects.filter(novel=chapter.novel, order__gt=chapter.order).order_by('order').first()
    prev_chap = Chapter.objects.filter(novel=chapter.novel, order__lt=chapter.order).order_by('-order').first()
    
    data['next_chapter_id'] = next_chap.id if next_chap else None
    data['prev_chapter_id'] = prev_chap.id if prev_chap else None
    data['novel_id'] = chapter.novel.id
    
    return Response(data)