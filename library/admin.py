from django.contrib import admin
from .models import Novel, Chapter, Bookmark, UserSettings, Comment, Tag, NovelVote
from .utils import generate_chapters, get_epub_metadata

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'views', 'rating_score', 'uploaded_at')
    search_fields = ('title', 'author')
    list_filter = ('status', 'genre', 'tags')
    filter_horizontal = ('tags',)
    
    def save_model(self, request, obj, form, change):
        # 1. Simpan file fisik dulu (agar path-nya terbentuk)
        super().save_model(request, obj, form, change)

        # 2. Cek apakah ada file epub baru yang diupload
        if 'epub_file' in form.changed_data and obj.epub_file:
            try:
                # Ambil Metadata
                meta = get_epub_metadata(obj.epub_file.path)
                
                # --- LOGIKA SAT-SET ---
                updated = False
                
                # Isi Judul otomatis jika kosong atau masih default
                if not obj.title or obj.title == "New Novel" or obj.title == ".":
                    if meta.get('title'):
                        obj.title = meta['title']
                        updated = True
                
                # Isi Penulis otomatis jika kosong
                if not obj.author or obj.author == "Unknown":
                    if meta.get('author'):
                        obj.author = meta['author']
                        updated = True

                # Isi Sinopsis otomatis jika kosong
                if not obj.synopsis:
                    if meta.get('synopsis'):
                        obj.synopsis = meta['synopsis']
                        updated = True
                
                # Simpan ulang jika ada data yang terisi otomatis
                if updated:
                    obj.save()

                # 3. Generate Chapters (Hapus yang lama biar bersih)
                obj.chapters.all().delete()
                generate_chapters(obj)
                
            except Exception as e:
                self.message_user(request, f"Gagal proses EPUB: {e}", level='ERROR')
                
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'novel_title', 'text_snippet', 'created_at')
    search_fields = ('text', 'user__username')

    def novel_title(self, obj):
        return obj.chapter.novel.title
    
    def text_snippet(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

@admin.register(NovelVote)
class NovelVoteAdmin(admin.ModelAdmin):
    list_display = ('novel', 'user', 'score', 'created_at')

admin.site.register(Chapter)
admin.site.register(Bookmark)
admin.site.register(UserSettings)