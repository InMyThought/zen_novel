from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from library import views, api_views  # Import views (HTML) dan api_views (JSON)

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- JALUR WEBSITE (HTML - Agar tampilan lama tetap jalan) ---
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),                                # <--- Tambahan Penting
    path('novel/<int:novel_id>/', views.detail, name='detail'),                  # <--- Tambahan Penting
    path('read/<int:novel_id>/<int:chapter_id>/', views.read_chapter, name='read'), # <--- Tambahan Penting
    
    # --- JALUR API (JSON - Untuk React/Vue nanti) ---
    path('api/novels/', api_views.novel_list, name='api_novel_list'),
    path('api/novels/<int:pk>/', api_views.novel_detail, name='api_novel_detail'),
    path('api/chapters/<int:pk>/', api_views.chapter_detail, name='api_chapter_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)