from rest_framework import serializers
from .models import Novel, Chapter

# Serializer untuk Chapter (Dipakai di Detail Novel & Baca)
class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'uploaded_at']

# Serializer Ringan (Khusus untuk List di Halaman Depan)
class NovelListSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(source='average_rating', read_only=True)
    chapter_count = serializers.IntegerField(source='chapters.count', read_only=True)

    class Meta:
        model = Novel
        # HANYA ambil data penting, JANGAN ambil list chapters disini
        fields = ['id', 'title', 'cover', 'genre', 'status', 'rating', 'chapter_count', 'uploaded_at']

# Serializer Berat (Khusus untuk Halaman Detail saat diklik)
class NovelDetailSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    rating = serializers.FloatField(source='average_rating', read_only=True)

    class Meta:
        model = Novel
        fields = ['id', 'title', 'author', 'synopsis', 'cover', 'genre', 'status', 'rating', 'uploaded_at', 'chapters']