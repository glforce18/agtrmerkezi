# GitHub Actions Workflows

Bu dizin AGTR Merkezi projesi için GitHub Actions workflow'larını içerir.

## Mevcut Workflow'lar

### 1. CI - Backend Tests & Linting (`ci.yml`)
**Tetiklenme**: Her push ve PR (master, main, develop)

**Yapılanlar**:
- ✅ Python 3.10, 3.11, 3.12 sürümleri ile test
- ✅ PostgreSQL 15 test veritabanı
- ✅ Black code formatting kontrolü
- ✅ isort import sıralama kontrolü
- ✅ flake8 linting
- ✅ Bandit güvenlik taraması
- ✅ pytest ile unit testler
- ✅ Code coverage raporu
- ✅ Frontend build kontrolü

**Süre**: ~5-10 dakika

### 2. Quick Check (`quick-check.yml`)
**Tetiklenme**: Her push (master, main)

**Yapılanlar**:
- ✅ Hızlı syntax kontrolü
- ✅ Formatting kontrolü
- ✅ Import kontrolü
- ✅ Temel linting

**Süre**: ~1-2 dakika

## Workflow Durumlarını Görüntüleme

GitHub repository sayfasında "Actions" sekmesinden workflow çalışmalarını görebilirsiniz:

```
https://github.com/glforce18/agtrmerkezi/actions
```

## Badge'ler

README.md dosyanıza ekleyebileceğiniz badge'ler:

### CI Status
```markdown
![CI](https://github.com/glforce18/agtrmerkezi/workflows/CI%20-%20Backend%20Tests%20&%20Linting/badge.svg)
```

### Quick Check Status
```markdown
![Quick Check](https://github.com/glforce18/agtrmerkezi/workflows/Quick%20Check/badge.svg)
```

## Lokal Olarak Test Etme

Workflow'ları push etmeden önce lokal olarak test etmek için:

### Backend Linting
```bash
cd /var/www/agtrmerkezi

# Formatting check
black --check app/ tests/

# Auto-format
black app/ tests/

# Import sorting
isort --check-only app/ tests/
isort app/ tests/

# Linting
flake8 app/ tests/
```

### Backend Tests
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Frontend Build
```bash
cd frontend
npm ci
npm run build
```

## Hata Çözümleri

### "Black formatting issues found"
```bash
black app/ tests/
git add .
git commit --amend --no-edit
```

### "Import sorting issues found"
```bash
isort app/ tests/
git add .
git commit --amend --no-edit
```

### "Flake8 errors"
Linting hatalarını düzeltmek için raporlanan satırlara bakın ve düzeltin.

### "Tests failed"
```bash
# Lokal olarak test çalıştırın
pytest tests/ -v

# Spesifik test
pytest tests/test_specific.py -v
```

## Continue-on-error Neden Kullanıldı?

Bazı workflow adımlarında `continue-on-error: true` kullanılmıştır çünkü:

1. **Mevcut kod tabanında bazı linting hataları var**: Bunları zamanla düzeltmek için
2. **Testler henüz tam kapsamlı değil**: Yeni testler eklenirken workflow başarısız olmamalı
3. **Güvenlik uyarıları bilgilendirme amaçlı**: Kritik olmayan Bandit uyarıları

## İyileştirme Planı

- [ ] Continue-on-error bayraklarını kaldır (kod kalitesi arttıkça)
- [ ] Test coverage'ı %80+ hedefle
- [ ] Deployment workflow ekle
- [ ] Performance test workflow ekle
- [ ] E2E test workflow ekle

## Notlar

- PostgreSQL test veritabanı otomatik oluşturulur
- Her Python sürümü için ayrı job çalışır (paralel)
- Frontend build artifacts kaydedilir
- Test sonuçları ve coverage raporları artifact olarak saklanır
