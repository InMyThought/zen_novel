import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from .models import Chapter
import os
import re

def generate_chapters(novel_instance):
    if not novel_instance.epub_file: return
    file_path = novel_instance.epub_file.path
    
    try:
        # --- LOGIKA EPUB ---
        if file_path.endswith('.epub'):
            book = epub.read_epub(file_path)
            # Auto-fill judul jika kosong
            if novel_instance.title == "New Novel" or not novel_instance.title:
                try:
                    novel_instance.title = book.get_metadata('DC', 'title')[0][0]
                    novel_instance.save()
                except: pass

            order_count = 1
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    title_tag = soup.find(['h1', 'h2', 'h3'])
                    
                    if title_tag:
                        title_text = title_tag.get_text().strip()
                    else:
                        title_text = f"Chapter {order_count}"
                    
                    text_content = ""
                    for p in soup.find_all('p'):
                        text_content += str(p)
                    
                    if len(text_content) > 100:
                        Chapter.objects.create(novel=novel_instance, title=title_text, content=text_content, order=order_count)
                        order_count += 1
                        
        # --- LOGIKA TXT ---
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split per paragraf (baris baru)
            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
            chunk_size = 50 # 50 Paragraf per chapter
            
            for i in range(0, len(paragraphs), chunk_size):
                chunk = paragraphs[i:i+chunk_size]
                body = "".join([f"<p>{p}</p>" for p in chunk])
                chap_num = (i // chunk_size) + 1
                
                Chapter.objects.create(
                    novel=novel_instance, 
                    title=f"Part {chap_num}", 
                    content=body, 
                    order=chap_num
                )
    except Exception as e:
        print(f"Error parsing: {e}")

def get_epub_metadata(epub_path):
    """
    Fungsi untuk menyedot metadata (Judul, Penulis, Sinopsis) dari file EPUB.
    """
    metadata = {}
    try:
        book = epub.read_epub(epub_path)
        
        # 1. Ambil Judul
        if book.get_metadata('DC', 'title'):
            metadata['title'] = book.get_metadata('DC', 'title')[0][0]
            
        # 2. Ambil Penulis (Creator)
        if book.get_metadata('DC', 'creator'):
            raw_author = book.get_metadata('DC', 'creator')[0][0]
            
            # Cek: Jika author ada isinya DAN bukan angka "0"
            if raw_author and str(raw_author).strip() != "0":
                metadata['author'] = raw_author
            else:
                # Jika "0", kita biarkan kosong agar Admin.py memakai default "Unknown"
                pass
            
        # 3. Ambil Sinopsis (Description)
        if book.get_metadata('DC', 'description'):
            raw_desc = book.get_metadata('DC', 'description')[0][0]
            # Bersihkan tag HTML (seperti <p>, <br>) dari sinopsis biar rapi
            clean_desc = re.sub('<[^<]+?>', '', raw_desc)
            metadata['synopsis'] = clean_desc
            
    except Exception as e:
        print(f"Gagal ambil metadata: {e}")
        
    return metadata
    """
    Fungsi untuk mengambil Judul, Sinopsis, dan Genre dari file EPUB
    """
    metadata = {
        'title': None,
        'synopsis': None,
        'genre': "General" # <--- Default Value jika di EPUB tidak ada info genre
    }

    try:
        book = epub.read_epub(epub_path)
        
        # 1. Ambil Title (Judul)
        if book.get_metadata('DC', 'title'):
            metadata['title'] = book.get_metadata('DC', 'title')[0][0]
            
        # 2. Ambil Description (Sinopsis)
        if book.get_metadata('DC', 'description'):
            synopsis = book.get_metadata('DC', 'description')[0][0]
            # Opsional: Bersihkan tag HTML sederhana jika perlu
            # synopsis = synopsis.replace('<p>', '').replace('</p>', '\n')
            metadata['synopsis'] = synopsis

        # 3. Ambil Subject (Genre) -- BAGIAN BARU
        subjects = book.get_metadata('DC', 'subject')
        if subjects:
            # EPUB bisa punya banyak subject, misal: ['Fantasy', 'Magic', 'Adventure']
            # Kita gabungkan jadi string: "Fantasy, Magic, Adventure"
            genre_list = [s[0] for s in subjects] 
            
            # Gabung pakai koma
            genre_str = ", ".join(genre_list)
            
            # Potong jika kepanjangan (karena max_length database cuma 100)
            if len(genre_str) > 100:
                genre_str = genre_str[:97] + "..."
            
            metadata['genre'] = genre_str

        return metadata
    
    except Exception as e:
        print(f"Gagal ekstrak metadata: {e}")
        return metadata