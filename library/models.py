from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.core.files import File 
from PIL import Image              
from io import BytesIO
import os

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Novel(models.Model):
    STATUS_CHOICES = [('Ongoing', 'Ongoing'), ('Completed', 'Completed')]
    
    title = models.CharField(max_length=255, blank=True, default="New Novel") 
    author = models.CharField(max_length=255, default="Unknown", blank=True)
    alternative_title = models.CharField(max_length=500, blank=True, null=True, help_text="Judul Asli / Jepang / Sinonim")
    synopsis = models.TextField(blank=True, null=True, help_text="Ringkasan cerita")
    genre = models.CharField(max_length=100, default="Action", help_text="Contoh: Fantasy, Romance")
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ongoing')
    cover = models.ImageField(upload_to='covers/', null=True, blank=True)
    
    views = models.IntegerField(default=0)
    rating_score = models.FloatField(default=0.0)
    
    epub_file = models.FileField(upload_to='epubs/', null=True, blank=True, help_text="Upload .epub/.txt di sini")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def save(self, *args, **kwargs):
        # 1. Logika Auto Alternative Title
        if not self.alternative_title or self.alternative_title == "{title}":
            self.alternative_title = self.title
        
        # 2. Logika Kompresi Cover
        if self.cover:
            # Pastikan tidak kompres berulang jika sudah .webp
            if not self.cover.name.lower().endswith('.webp'):
                self.compress_cover()
                
        super().save(*args, **kwargs)

    def compress_cover(self):
        """
        Fungsi untuk mengubah cover menjadi WebP dan kompresi kualitas
        """
        try:
            img = Image.open(self.cover)
            
            # Ubah ke RGB jika transparan agar kompatibel dengan WebP
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            temp_handle = BytesIO()
            img.save(temp_handle, format='WebP', quality=80, method=6)
            temp_handle.seek(0)

            current_name = os.path.splitext(self.cover.name)[0]
            new_name = f"{current_name}.webp"

            # Simpan tanpa memicu save() berulang (save=False)
            self.cover.save(new_name, File(temp_handle), save=False)
        except Exception as e:
            print(f"Gagal kompres: {e}")

    def average_rating(self):
        avg = self.votes.aggregate(Avg('score'))['score__avg']
        return round(avg, 1) if avg else 0.0

    def __str__(self):
        return self.title

class Chapter(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.FloatField(default=0.0)
    chapter_index = models.FloatField(default=0, help_text="Nomor asli dari judul chapter")
    uploaded_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.novel.title} - {self.title}"

class NovelVote(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('novel', 'user')

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='bookmarked_by')
    last_read_chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_in_library = models.BooleanField(default=False) 

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('user', 'novel')

    def __str__(self):
        return f"{self.user.username} - {self.novel.title}"

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    font_size = models.IntegerField(default=18)
    line_height = models.FloatField(default=1.8)
    theme = models.CharField(max_length=20, default='dark') 
    
    def __str__(self):
        return f"Settings for {self.user.username}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.chapter.title}"