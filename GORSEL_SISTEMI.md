# 🎨 AGTR Merkezi - Görsel Yönetim Sistemi

## Sistem Özeti

Projenize profesyonel bir görsel yönetim sistemi eklendi. Artık:
- ✅ Oyun logoları
- ✅ Forum kategori ikonları
- ✅ Site logo/favicon
- ✅ Banner görselleri
- ✅ Özel görseller

kolayca yüklenip yönetilebiliyor.

---

## 📁 Dosya Yapısı

```
static/images/
├── site/
│   ├── logo/          # Site logosu
│   ├── favicon/       # Favicon
│   ├── banner/        # Ana sayfa banner
│   └── og-image/      # Sosyal medya görseli
│
├── games/
│   ├── hldm/          # Half-Life DM logoları
│   ├── ag/            # Adrenaline Gamer logoları
│   └── cs16/          # Counter-Strike 1.6 logoları
│
├── forum/
│   ├── genel/         # Forum kategori ikonları
│   ├── duyurular/
│   └── yardim/
│
└── uploads/           # Kullanıcı yüklemeleri
```

---

## 🚀 Kullanım

### 1. Admin Paneli

Admin paneline giriş yapın:
```
https://agtrmerkezi.com/admin/media
```

**Özellikler:**
- Drag & drop görsel yükleme
- Anlık önizleme
- Format kontrolü (PNG, JPG, SVG, WebP)
- Boyut kontrolü (Max 5MB)
- Otomatik optimizasyon

### 2. API Kullanımı

#### Oyun Logosu Yükleme
```bash
curl -X POST https://agtrmerkezi.com/api/media/games/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@logo.png" \
  -F "game_type=hldm"
```

#### Forum İkonu Yükleme
```bash
curl -X POST https://agtrmerkezi.com/api/media/forum/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@icon.svg" \
  -F "category_slug=genel"
```

#### Site Logosu Yükleme
```bash
curl -X POST https://agtrmerkezi.com/api/media/site/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@logo.svg" \
  -F "media_type=logo"
```

### 3. Template'lerde Kullanım

#### Oyun Logosu
```jinja2
<!-- Oyun logosunu göster -->
<img src="{{ get_game_logo('hldm') }}" alt="Half-Life DM">

<!-- Oyun adı -->
<h3>{{ get_game_display_name('hldm') }}</h3>

<!-- Oyun rengi -->
<div style="background: {{ get_game_color('cs16') }}">
    Counter-Strike 1.6
</div>
```

#### Forum İkonu
```jinja2
{% set icon_data = get_forum_icon(category.slug, category.icon_class) %}

{% if icon_data.type == 'image' %}
    <img src="{{ icon_data.url }}" alt="{{ category.name }}">
{% else %}
    <i class="{{ icon_data.class }}"></i>
{% endif %}
```

#### Site Logo/Favicon
```jinja2
<!-- Logo -->
<img src="{{ get_site_logo() }}" alt="AGTR Merkezi">

<!-- Favicon -->
<link rel="icon" href="{{ get_site_favicon() }}">
```

---

## 🎨 Varsayılan Görseller

Sistem şu görseller ile geliyor:

### Site
- `/static/images/logo.svg` - AGTR Merkezi logosu
- `/static/images/favicon.svg` - 64x64 favicon

### Oyunlar
- `/static/images/games/hldm/logo.svg` - Half-Life DM
- `/static/images/games/ag/logo.svg` - Adrenaline Gamer
- `/static/images/games/cs16/logo.svg` - Counter-Strike 1.6

---

## 🔧 Özelleştirme

### 1. Font Awesome İkonları

Forum kategorileri için Font Awesome kullanabilirsiniz:

```python
# Veritabanında category.icon_class olarak kaydedin
category.icon_class = "fas fa-fire"  # Ateş ikonu
category.icon_class = "fas fa-trophy"  # Kupa
category.icon_class = "fas fa-crown"  # Taç
```

### 2. Özel Görseller

Admin panelinden yükleyebileceğiniz formatlar:
- **PNG** - Şeffaflık için ideal
- **SVG** - Vektörel, her boyutta keskin
- **JPG** - Fotoğraflar için
- **WebP** - Modern, optimize

### 3. Görsel Boyutları

**Önerilen Boyutlar:**
```
Logo:        200x60px (SVG tercih edilir)
Favicon:     64x64px veya 32x32px
Banner:      1920x400px
OG Image:    1200x630px
Game Logo:   150x150px
Forum Icon:  64x64px
```

---

## 📡 API Endpoint'leri

### GET Endpoints

```
GET /api/media/games/list          # Tüm oyun logolarını listele
GET /api/media/forum/list          # Forum ikonlarını listele
GET /api/media/site/list           # Site görsellerini listele
GET /api/media/default-icons       # Varsayılan Font Awesome ikonları
```

### POST Endpoints

```
POST /api/media/games/upload       # Oyun logosu yükle
POST /api/media/forum/upload       # Forum ikonu yükle
POST /api/media/site/upload        # Site görseli yükle
```

### DELETE Endpoints

```
DELETE /api/media/delete?url=/static/images/...  # Görsel sil
```

---

## 🎯 Örnek Kullanımlar

### Sunucu Paketlerinde Logo Gösterme

```jinja2
{% for package in packages %}
<div class="package-card">
    <img src="{{ get_game_logo(package.game_type) }}"
         alt="{{ get_game_display_name(package.game_type) }}"
         class="game-logo">
    <h4>{{ package.name }}</h4>
    <p style="color: {{ get_game_color(package.game_type) }}">
        {{ package.slots }} slot
    </p>
</div>
{% endfor %}
```

### Forum Kategorileri

```jinja2
{% for category in categories %}
<div class="forum-category">
    {% set icon = get_forum_icon(category.slug, category.icon_class) %}

    <div class="category-icon">
        {% if icon.type == 'image' %}
            <img src="{{ icon.url }}" alt="{{ category.name }}">
        {% else %}
            <i class="{{ icon.class }}"></i>
        {% endif %}
    </div>

    <div class="category-info">
        <h3>{{ category.name }}</h3>
        <p>{{ category.description }}</p>
    </div>
</div>
{% endfor %}
```

---

## 🔐 Güvenlik

- ✅ Sadece admin kullanıcılar yükleyebilir
- ✅ Dosya türü kontrolü
- ✅ Dosya boyutu limiti (5MB)
- ✅ Benzersiz dosya adları (UUID)
- ✅ Path traversal koruması

---

## 📊 Performans

- SVG kullanımı ile küçük dosya boyutları
- Lazy loading desteği
- CDN uyumlu yapı
- Browser caching

---

## 🎨 CSS Örneği

```css
/* Oyun logoları */
.game-logo {
    width: 150px;
    height: 150px;
    object-fit: contain;
    transition: transform 0.3s ease;
}

.game-logo:hover {
    transform: scale(1.1);
}

/* Forum ikonları */
.forum-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    padding: 8px;
    background: var(--icon-bg);
}

/* Site logosu */
.site-logo {
    max-height: 60px;
    width: auto;
}
```

---

## 🚀 Hızlı Başlangıç

1. **Admin paneline gir:**
   ```
   https://agtrmerkezi.com/admin/media
   ```

2. **İlk oyun logosunu yükle:**
   - "Oyun Logoları" tabına geç
   - Half-Life için logo seç
   - "Yükle" butonuna bas

3. **Template'de kullan:**
   ```jinja2
   <img src="{{ get_game_logo('hldm') }}">
   ```

4. **Sonucu gör:**
   Sunucu paketleri sayfasında logoyu göreceksiniz!

---

## 📞 Destek

Sorun yaşarsanız:
1. `/var/www/agtrmerkezi/logs/` altındaki logları kontrol edin
2. Dosya izinlerini kontrol edin: `chmod 755 static/images/`
3. Dosya boyutunu kontrol edin (Max 5MB)

---

## 🎉 Sonuç

Artık siteniz profesyonel görsellerle donatılmış durumda!

**Sonraki adımlar:**
- [ ] Tüm oyun logolarını yükle
- [ ] Forum kategorilerine özel ikonlar ekle
- [ ] Site logosunu özelleştir
- [ ] Sosyal medya görselleri ekle
