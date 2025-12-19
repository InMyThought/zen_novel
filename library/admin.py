from django.contrib import admin
from .models import Novel, Chapter, NovelVote
from .utils import generate_chapters


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class ChapterInline(admin.TabularInline):
    model = Chapter
    fields = ('title', 'order')
    extra = 0

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'novel_title', 'text_snippet', 'created_at')
    search_fields = ('text', 'user__username')

    def novel_title(self, obj):
        return obj.chapter.novel.title
    
    def text_snippet(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'status', 'average_rating', 'uploaded_at')
    inlines = [ChapterInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'epub_file' in form.changed_data and obj.epub_file:
            obj.chapters.all().delete()
            generate_chapters(obj)

admin.site.register(Chapter)
admin.site.register(NovelVote)