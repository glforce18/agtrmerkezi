# Testing Documentation

Bu dokümantasyon, AGTR Merkezi projesinin kapsamlı test altyapısını açıklar.

## 📋 İçindekiler

- [Test Türleri](#test-türleri)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Yerel Test Çalıştırma](#yerel-test-çalıştırma)
- [Test Coverage](#test-coverage)
- [En İyi Pratikler](#en-iyi-pratikler)

## 🧪 Test Türleri

### Backend Tests (Python)

#### 1. Unit Tests
```bash
pytest tests/ -v -m "unit"
```

#### 2. Integration Tests
```bash
pytest tests/ -v -m "integration"
```

#### 3. API Tests
```bash
pytest tests/api/ -v
```

#### 4. Type Checking
```bash
mypy app/
```

#### 5. Code Formatting
```bash
# Check
black --check app/ tests/
isort --check-only app/ tests/

# Fix
black app/ tests/
isort app/ tests/
```

#### 6. Linting
```bash
flake8 app/ tests/
```

#### 7. Security Scan
```bash
bandit -r app/
```

#### 8. Database Migration Tests
```bash
pytest tests/test_migrations.py -v -m slow
```

### Frontend Tests (Vue + Vite)

#### 1. Unit Tests
```bash
cd frontend
npm run test
```

#### 2. Unit Tests with Coverage
```bash
cd frontend
npm run test:coverage
```

#### 3. Unit Tests with UI
```bash
cd frontend
npm run test:ui
```

#### 4. E2E Tests
```bash
cd frontend
npm run test:e2e
```

#### 5. E2E Tests with UI
```bash
cd frontend
npm run test:e2e:ui
```

#### 6. Linting
```bash
cd frontend
npm run lint
```

#### 7. Type Checking
```bash
cd frontend
npm run type-check
```

### Load Testing

#### K6 Load Tests
```bash
k6 run tests/load/api-load-test.js
```

#### With Custom Parameters
```bash
BASE_URL=http://localhost:8000 k6 run tests/load/api-load-test.js
```

## 🚀 GitHub Actions Workflows

### 1. Comprehensive CI (`comprehensive-ci.yml`)
**Tetiklenme:** Push ve PR (master, main, develop)

**İçerik:**
- Backend tests (Python 3.10, 3.11, 3.12)
- Frontend unit tests
- Frontend build check
- E2E tests (Playwright)
- Database migration tests

**Süre:** ~5-10 dakika

### 2. Security Scans (`security.yml`)
**Tetiklenme:** Push, PR, Haftalık (Pazar gecesi)

**İçerik:**
- Snyk dependency scanning
- OWASP dependency check
- CodeQL security analysis
- TruffleHog secret scanning
- Trivy container scanning

**Süre:** ~8-15 dakika

### 3. Performance Tests (`performance.yml`)
**Tetiklenme:** Push/PR (master, main), Haftalık (Pazartesi sabahı)

**İçerik:**
- Lighthouse performance audit
- K6 load testing
- Backend performance benchmarks
- Frontend bundle size analysis

**Süre:** ~10-15 dakika

### 4. Docker Build & Test (`docker.yml`)
**Tetiklenme:** Push ve PR

**İçerik:**
- Docker image build
- Security scan (Trivy)
- Basic functionality tests

**Süre:** ~3-5 dakika

### 5. Code Quality (`code-quality.yml`)
**Tetiklenme:** Push ve PR

**İçerik:**
- Python code quality (Black, isort, flake8, mypy, pylint, radon)
- JavaScript/Vue quality (ESLint, type checking)
- Code metrics ve statistics
- Accessibility tests

**Süre:** ~5-8 dakika

### 6. Quick Check (`quick-check.yml`)
**Tetiklenme:** Push (master, main)

**İçerik:**
- Hızlı syntax kontrolü
- Formatting check
- Basic linting

**Süre:** ~1-2 dakika

## 💻 Yerel Test Çalıştırma

### Backend Tests (Full Suite)
```bash
# Tüm testleri çalıştır
pytest tests/ -v --cov=app --cov-report=html

# Sadece unit tests
pytest tests/ -v -m "unit"

# Sadece integration tests
pytest tests/ -v -m "integration"

# Slow testleri hariç tut
pytest tests/ -v -m "not slow"

# Parallel test execution
pytest tests/ -n auto
```

### Frontend Tests (Full Suite)
```bash
cd frontend

# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Tüm testler
npm run test && npm run test:e2e
```

### Full Stack Test
```bash
# Terminal 1: Start backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend && npm run dev

# Terminal 3: Run E2E tests
cd frontend && npm run test:e2e
```

## 📊 Test Coverage

### Backend Coverage Hedefleri
- **Minimum:** 70%
- **Hedef:** 85%
- **İdeal:** 90%+

### Frontend Coverage Hedefleri
- **Minimum:** 60%
- **Hedef:** 75%
- **İdeal:** 85%+

### Coverage Raporlarını Görüntüleme

#### Backend
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

#### Frontend
```bash
cd frontend
npm run test:coverage
open coverage/index.html
```

## ✅ En İyi Pratikler

### Test Yazma Kuralları

1. **Test İsimlendirme**
   ```python
   # ✅ İyi
   def test_user_login_with_valid_credentials():
       pass

   # ❌ Kötü
   def test_login():
       pass
   ```

2. **Test Organizasyonu**
   ```python
   # Arrange (Hazırlık)
   user = create_test_user()

   # Act (İşlem)
   result = login(user.email, user.password)

   # Assert (Doğrulama)
   assert result.success is True
   ```

3. **Test İzolasyonu**
   - Her test bağımsız olmalı
   - Test sırası önemli olmamalı
   - Shared state kullanmaktan kaçının

4. **Fixture Kullanımı**
   ```python
   @pytest.fixture
   async def test_client():
       async with AsyncClient(app=app) as client:
           yield client
   ```

### GitHub Actions İpuçları

1. **Secrets Yönetimi**
   - `Settings > Secrets and variables > Actions`
   - Gerekli secrets:
     - `SNYK_TOKEN` (Snyk security scanning için)
     - `CODECOV_TOKEN` (Code coverage için - opsiyonel)

2. **Workflow Optimizasyonu**
   - Cache kullanımı (pip, npm)
   - Parallel job execution
   - Conditional steps

3. **Debugging**
   ```yaml
   - name: Debug step
     run: |
       echo "Event: ${{ github.event_name }}"
       echo "Branch: ${{ github.ref }}"
       ls -la
   ```

## 🔧 Troubleshooting

### Frontend Test Hataları

#### Node version mismatch
```bash
# Node 22+ gerekli
nvm install 22
nvm use 22
```

#### Playwright browser hatası
```bash
npx playwright install --with-deps
```

### Backend Test Hataları

#### Database connection
```bash
# PostgreSQL çalıştığından emin olun
sudo systemctl status postgresql

# Test database oluşturun
createdb agtrmerkezi_test
```

#### Import errors
```bash
# Dependencies'i yeniden yükleyin
pip install -r requirements.txt --force-reinstall
```

### CI/CD Hataları

#### Workflow fails on dependency install
- `package-lock.json` veya `requirements.txt` güncel mi?
- Cache temizlenmiş mi?

#### Timeout issues
- Timeout değerlerini artırın
- Parallel execution kullanın

## 📚 Kaynaklar

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [K6 Load Testing](https://k6.io/docs/)

## 🤝 Katkıda Bulunma

Yeni test eklerken:
1. Test coverage'ı düşürmeyin
2. Tüm testlerin geçtiğinden emin olun
3. Test dokümantasyonunu güncelleyin
4. Yeni test türleri için GitHub Actions ekleyin

---

**Son Güncelleme:** 2026-01-30
**Versiyon:** 2.0.0
