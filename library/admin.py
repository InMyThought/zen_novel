from django.contrib import admin
from .models import Novel, Chapter, Bookmark, UserSettings, Comment, Tag, NovelVote
from .utils import generate_chapters, get_epub_metadata

# =====================================================
# 1. INLINE: FITUR ADD MULTI CHAPTER (Editing Masal)
# =====================================================
class ChapterInline(admin.TabularInline):
    model = Chapter
    fields = ('title', 'order', 'chapter_index')
    extra = 1  # Baris kosong untuk tambah manual
    show_change_link = True # Tombol edit detail

# =====================================================
# 2. TAG ADMIN
# =====================================================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

# =====================================================
# 3. NOVEL ADMIN (Auto EPUB + Multi Chapter)
# =====================================================
@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'total_chapters', 'views', 'uploaded_at')
    search_fields = ('title', 'author')
    list_filter = ('status', 'genre', 'tags', 'uploaded_at')
    filter_horizontal = ('tags',)
    
    # Menambahkan editor chapter di dalam halaman novel
    inlines = [ChapterInline] 
    
    readonly_fields = ('views', 'rating_score')

    def total_chapters(self, obj):
        return obj.chapters.count()
    total_chapters.short_description = 'Chapters'

    # Logika Upload EPUB Otomatis
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if 'epub_file' in form.changed_data and obj.epub_file:
            try:
                meta = get_epub_metadata(obj.epub_file.path)
                updated = False
                
                # Isi data otomatis jika kosong
                if not obj.title or obj.title in ["New Novel", "."]:
                    if meta.get('title'):
                        obj.title = meta['title']
                        updated = True
                
                if not obj.author or obj.author == "Unknown":
                    if meta.get('author'):
                        obj.author = meta['author']
                        updated = True

                if not obj.synopsis:
                    if meta.get('synopsis'):
                        obj.synopsis = meta['synopsis']
                        updated = True
                
                if updated:
                    obj.save()

                # Generate ulang chapter dari EPUB
                obj.chapters.all().delete()
                generate_chapters(obj)
                self.message_user(request, f"Sukses ekstrak chapter dari {obj.epub_file.name}", level='SUCCESS')
                
            except Exception as e:
                self.message_user(request, f"Gagal proses EPUB: {e}", level='ERROR')

# =====================================================
# 4. CHAPTER ADMIN (Search Chapter)
# =====================================================
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'novel_link', 'order', 'chapter_index', 'uploaded_at')
    
    # Fitur Search: Cari judul chapter atau judul novel
    search_fields = ('title', 'novel__title') 
    
    list_filter = ('uploaded_at',)
    autocomplete_fields = ['novel'] # Biar ringan loadnya
    list_per_page = 50 
    ordering = ('novel', 'order')

    def novel_link(self, obj):
        return obj.novel.title
    novel_link.short_description = 'Novel'
    novel_link.admin_order_field = 'novel__title'

# =====================================================
# 5. ADMIN LAINNYA (Fixed Bookmark)
# =====================================================

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    # Disesuaikan dengan models.py Anda: last_read_chapter & updated_at
    list_display = ('user', 'novel', 'last_read_chapter', 'updated_at')
    search_fields = ('user__username', 'novel__title')
    
    # Autocomplete field yang benar
    autocomplete_fields = ['user', 'novel', 'last_read_chapter']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'novel_title', 'text_snippet', 'created_at')
    search_fields = ('text', 'user__username')
    list_filter = ('created_at',)
    
    # Jika Comment punya field chapter & user, bisa pakai ini:
    autocomplete_fields = ['chapter', 'user']

    def novel_title(self, obj):
        return obj.chapter.novel.title if obj.chapter and obj.chapter.novel else "-"
    
    def text_snippet(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

@admin.register(NovelVote)
class NovelVoteAdmin(admin.ModelAdmin):
    list_display = ('novel', 'user', 'score', 'created_at')
    list_filter = ('score',)

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'font_size')
    search_fields = ('user__username',)