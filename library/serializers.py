from rest_framework import serializers
from django.contrib.auth.models import User
# Pastikan semua model terimport, TERMASUK Bookmark
from .models import Novel, Chapter, UserSettings, Comment, Tag, Bookmark

# --- 1. Serializer Helper (Tag & Chapter) ---

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'uploaded_at']

# --- 2. Serializer Utama (List & Detail) ---

# KHUSUS HOME PAGE (Ringan)
class NovelListSerializer(serializers.ModelSerializer):
    # Field tambahan (computed)
    rating = serializers.FloatField(source='average_rating', read_only=True)
    chapter_count = serializers.IntegerField(source='chapters.count', read_only=True)

    class Meta:
        model = Novel
        # Genre sudah masuk disini, jadi di Home Page aman untuk filter/display
        fields = [
            'id', 'title', 'cover', 'genre', 'status', 
            'rating', 'chapter_count', 'uploaded_at','views'
        ]

# KHUSUS DETAIL PAGE (Lengkap dengan Bookmark & Tags)
class NovelDetailSerializer(serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField() # Custom Logic
    chapters = ChapterSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    rating = serializers.FloatField(source='average_rating', read_only=True)

    class Meta:
        model = Novel
        fields = [
            'id', 'title', 'author', 'synopsis', 'tags', 'cover', 
            'genre', 'status', 'rating', 'uploaded_at', 
            'chapters', 'is_bookmarked','views'
        ]

    # LOGIC BOOKMARK (Harus di dalam class, sejajar dengan Meta)
    def get_is_bookmarked(self, obj):
        # Mengambil user yang sedang request (dari token)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Cek di database apakah user ini punya bookmark novel ini
            return Bookmark.objects.filter(user=request.user, novel=obj).exists()
        return False

# --- 3. User & Fitur Lainnya ---

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['font_size', 'line_height', 'theme']

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'username', 'text', 'created_at']