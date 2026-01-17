# ============================================
# AGTR v6.0 - Forum Modülü Tam Kurulum
# FASE1 + FASE2 TAMAMLANDI
# ============================================

## 📦 Paket İçeriği

```
agtr_v6_full/
├── app/
│   ├── api/
│   │   ├── admin/
│   │   │   ├── forum_categories.py   # Admin kategori CRUD API
│   │   │   └── forum_topics.py       # Admin konu/yanıt CRUD API
│   │   └── forum.py                  # User forum API (public)
│   └── models/
│       └── forum.py                  # Forum SQLAlchemy modelleri
├── templates/
│   ├── admin/
│   │   ├── forum_categories.html     # Admin kategori yönetimi
│   │   └── forum_topics.html         # Admin konu yönetimi
│   └── user/
│       ├── forum.html                # Forum ana sayfa
│       ├── forum_category.html       # Kategori detay (konular)
│       ├── forum_topic.html          # Konu detay (yanıtlar)
│       └── forum_new.html            # Yeni konu açma
├── static/
│   ├── css/
│   │   └── agtr-ui.css               # Toast/Modal stilleri
│   └── js/
│       └── agtr-ui.js                # Global UI kütüphanesi
├── KURULUM.md                        # Bu dosya
└── migration.sql                     # Database migration
```


## 🚀 Hızlı Kurulum (5 Adım)

### Adım 1: Dosyaları Kopyala
```bash
cd /var/www/agtrmerkezi

# API dosyaları
cp agtr_v6_full/app/api/forum.py app/api/
cp agtr_v6_full/app/api/admin/forum_categories.py app/api/admin/
cp agtr_v6_full/app/api/admin/forum_topics.py app/api/admin/

# Model dosyası
cp agtr_v6_full/app/models/forum.py app/models/

# Template dosyaları
cp agtr_v6_full/templates/admin/*.html templates/admin/
cp agtr_v6_full/templates/user/*.html templates/user/

# Static dosyalar
cp agtr_v6_full/static/css/agtr-ui.css static/css/
cp agtr_v6_full/static/js/agtr-ui.js static/js/
```

### Adım 2: Router'ları Kaydet
`app/main.py` dosyasına ekle:

```python
# Forum API routers
from app.api.forum import router as forum_router
from app.api.admin.forum_categories import router as forum_categories_router
from app.api.admin.forum_topics import router as forum_topics_router

# Include routers
app.include_router(forum_router, prefix="/api")
app.include_router(forum_categories_router, prefix="/api")
app.include_router(forum_topics_router, prefix="/api")
```

### Adım 3: Model Import
`app/models/__init__.py` dosyasına ekle:

```python
from app.models.forum import ForumCategory, ForumTopic, ForumReply
```

User model'e relationship ekle (`app/models/user.py`):

```python
# User class içine ekle
forum_topics = relationship("ForumTopic", back_populates="author")
forum_replies = relationship("ForumReply", back_populates="author")
```

### Adım 4: Database Migration
```bash
mysql -u root -p agtrmerkezi < migration.sql
```

### Adım 5: Base Template Güncellemeleri

**templates/admin/base.html** ve **templates/user/base.html** dosyalarına:

```html
<!-- HEAD içine CSS ekle -->
<link rel="stylesheet" href="{{ url_for('static', path='css/agtr-ui.css') }}">

<!-- BODY sonuna JS ekle (Bootstrap'tan sonra) -->
<script src="{{ url_for('static', path='js/agtr-ui.js') }}"></script>
```

**Admin sidebar'a ekle** (templates/admin/base.html):

```html
<li class="nav-item">
    <a class="nav-link {{ 'active' if request.url.path == '/admin/forum-categories' else '' }}" href="/admin/forum-categories">
        <i class="fas fa-folder-tree me-2"></i>Forum Kategorileri
    </a>
</li>
<li class="nav-item">
    <a class="nav-link {{ 'active' if request.url.path == '/admin/forum-topics' else '' }}" href="/admin/forum-topics">
        <i class="fas fa-comments me-2"></i>Forum Konuları
    </a>
</li>
```

**User navbar'a ekle** (templates/user/base.html):

```html
<li class="nav-item">
    <a class="nav-link {{ 'active' if '/forum' in request.url.path else '' }}" href="/forum">
        <i class="fas fa-comments me-2"></i>Forum
    </a>
</li>
```


## 📄 Route Tanımlamaları

`app/routes/admin.py` dosyasına ekle:

```python
@router.get("/forum-categories")
async def forum_categories_page(request: Request, current_user: User = Depends(get_current_admin_user)):
    return templates.TemplateResponse("admin/forum_categories.html", {"request": request, "user": current_user})

@router.get("/forum-topics")
async def forum_topics_page(request: Request, current_user: User = Depends(get_current_admin_user)):
    return templates.TemplateResponse("admin/forum_topics.html", {"request": request, "user": current_user})
```

`app/routes/user.py` veya `app/routes/forum.py` dosyasına ekle:

```python
@router.get("/forum")
async def forum_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse("user/forum.html", {"request": request, "user": current_user})

@router.get("/forum/category/{category_slug}")
async def forum_category_page(request: Request, category_slug: str, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse("user/forum_category.html", {
        "request": request, 
        "user": current_user,
        "category_slug": category_slug
    })

@router.get("/forum/topic/{topic_slug}")
async def forum_topic_page(request: Request, topic_slug: str, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse("user/forum_topic.html", {
        "request": request, 
        "user": current_user,
        "topic_slug": topic_slug
    })

@router.get("/forum/new")
async def forum_new_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("user/forum_new.html", {"request": request, "user": current_user})

@router.get("/forum/all")
async def forum_all_topics_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse("user/forum_category.html", {
        "request": request, 
        "user": current_user,
        "category_slug": None  # Tüm konular
    })
```


## 🔄 Restart
```bash
sudo systemctl restart agtrmerkezi
```


## 📊 API Endpoints Özeti

### Admin API
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | /api/admin/forum/categories | Tüm kategoriler |
| POST | /api/admin/forum/categories | Yeni kategori |
| PUT | /api/admin/forum/categories/{id} | Kategori güncelle |
| DELETE | /api/admin/forum/categories/{id} | Kategori sil |
| GET | /api/admin/forum/topics | Tüm konular |
| POST | /api/admin/forum/topics | Yeni konu (admin) |
| PUT | /api/admin/forum/topics/{id} | Konu güncelle |
| DELETE | /api/admin/forum/topics/{id} | Konu sil |
| GET | /api/admin/forum/topics/{id}/replies | Yanıtları getir |
| DELETE | /api/admin/forum/replies/{id} | Yanıt sil |

### User API (Public)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | /api/forum/categories | Aktif kategoriler |
| GET | /api/forum/categories/{slug} | Kategori detayı |
| GET | /api/forum/categories/{slug}/topics | Kategorinin konuları |
| GET | /api/forum/topics | Son konular |
| GET | /api/forum/topics/{slug} | Konu detayı |
| POST | /api/forum/topics | Yeni konu (auth) |
| GET | /api/forum/topics/{slug}/replies | Yanıtlar |
| POST | /api/forum/topics/{slug}/replies | Yanıt ekle (auth) |
| GET | /api/forum/stats | İstatistikler |


## 🎨 Toast/Modal Kullanımı

### Toast Bildirimleri
```javascript
// Başarılı
showToast('İşlem başarılı!', 'success');

// Hata
showToast('Bir hata oluştu', 'error');

// Uyarı
showToast('Dikkat!', 'warning');

// Bilgi
showToast('Bilginize', 'info');

// Özel süre (ms)
showToast('10 saniye görünür', 'info', { duration: 10000 });
```

### Onay Modal
```javascript
const result = await AGTR.confirm({
    title: 'Silmek istiyor musunuz?',
    message: 'Bu işlem geri alınamaz.',
    confirmText: 'Evet, Sil',
    cancelText: 'Vazgeç',
    confirmClass: 'btn-danger'
});

if (result) {
    // Silme işlemi
}
```

### Alert Modal
```javascript
await AGTR.alert({
    title: 'Başarılı!',
    message: 'Kayıt işlemi tamamlandı.',
    icon: 'fas fa-check-circle',
    iconColor: 'text-success'
});
```

### Prompt Modal
```javascript
const value = await AGTR.prompt({
    title: 'Kategori Adı',
    message: 'Yeni kategori adını girin:',
    placeholder: 'örn: Genel Tartışma'
});

if (value) {
    console.log('Girilen:', value);
}
```

### Loading Overlay
```javascript
AGTR.showLoading('Veriler yükleniyor...');
// ... işlem ...
AGTR.hideLoading();
```

### API Fetch Helper
```javascript
const { success, data, error } = await AGTR.fetch('/api/forum/categories', {
    method: 'POST',
    body: JSON.stringify({ name: 'Test' })
});

if (success) {
    showToast('Kaydedildi', 'success');
} else {
    showToast(error, 'error');
}
```


## ✅ Tamamlanan Özellikler

### FASE1 (6/6)
- ✅ announcements.html
- ✅ packages.html  
- ✅ coupons.html (+API PUT/DELETE)
- ✅ tickets.html
- ✅ Forum kategori CRUD (admin)
- ✅ Toast/Modal standart sistemi

### FASE2 (4/4)
- ✅ Forum konu CRUD (admin)
- ✅ Forum yanıt yönetimi (admin)
- ✅ User panel forum sayfaları (4 sayfa)
- ✅ User forum API (public)

**TOPLAM: 10/10 ✅ TAMAMLANDI!**


## 📝 Notlar

- Tüm API'lar REST standartlarına uygun
- Türkçe karakter desteği (slug'larda otomatik dönüşüm)
- Responsive tasarım (mobile uyumlu)
- Toast bildirimleri max 5 adet gösterilir
- Konular pinned (sabit) olarak işaretlenebilir
- Konular locked (kilitli) olarak işaretlenebilir
- View count otomatik artırılır
- Pagination desteği mevcut
