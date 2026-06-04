# Image Resize Service — Claude Code Prompt

> Bu dosyayı Claude Code'a olduğu gibi yapıştır.
> Her bölüm bir görev bloğudur; Claude Code sırayla uygular.

---

## PROJE TANIMI

"Bulut Mimarilerinde Test Mühendisliği" dersi dönem projesi.
Amaç: Basit bir mikroservis için endüstri standardında test ve dağıtım altyapısı kurmak.

**Servis:** Image Resize Service
- Kullanıcı bir resim yükler
- Servis resmi istenen boyuta getirir (Pillow ile)
- Boyutlandırılmış resmi LocalStack S3'e yükler
- Metadata'yı veritabanına (SQLite geliştirme / PostgreSQL prod) kaydeder
- Kullanıcıya kayıt ID'si ve presigned URL döner

---

## KLASÖR YAPISI

Aşağıdaki yapıyı tam olarak oluştur:

```
image-resize-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── database.py
│   └── metrics.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── factories.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_resize.py
│   │   └── test_schemas.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_s3.py
│   │   └── test_db.py
│   └── e2e/
│       ├── __init__.py
│       └── test_playwright.py
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
├── monitoring/
│   ├── prometheus.yml
│   └── grafana_dashboard.json
├── performance/
│   └── k6_script.js
├── postman/
│   └── collection.json
├── ui/
│   └── index.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── pytest.ini
└── README.md
```

---

## DOSYA AÇIKLAMALARI VE İÇERİKLERİ

### `app/database.py`
**Ne yapar:** SQLAlchemy engine ve session factory'yi kurar.
Geliştirmede SQLite (`./dev.db`), prod'da `DATABASE_URL` env değişkeninden PostgreSQL kullanır.
`get_db()` fonksiyonu FastAPI dependency injection ile her request'e ayrı session verir,
request bitince session otomatik kapanır.

```python
# İçermesi gerekenler:
# - SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
# - engine = create_engine(...) — SQLite için check_same_thread=False ekle
# - SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# - Base = declarative_base()
# - def get_db() -> Generator — yield db, finally db.close()
```

---

### `app/models.py`
**Ne yapar:** Veritabanı tablo şemasını tanımlar. `ImageRecord` adında tek bir SQLAlchemy modeli içerir.
Bu model; orijinal dosya adı, S3 bucket/key, boyutlar, dosya boyutu ve yükleme zamanı gibi
metadata'yı saklar. Tablo adı `image_records` olacak.

```python
# İçermesi gerekenler:
# class ImageRecord(Base):
#   __tablename__ = "image_records"
#   id: int (primary key, autoincrement)
#   original_filename: str (nullable=False)
#   s3_bucket: str
#   s3_key: str (unique=True)
#   original_width: int
#   original_height: int
#   resized_width: int
#   resized_height: int
#   file_size_bytes: int
#   content_type: str (default "image/jpeg")
#   created_at: datetime (default=utcnow)
```

---

### `app/schemas.py`
**Ne yapar:** Pydantic v2 modelleri — FastAPI'nin request/response doğrulaması için.
`ResizeRequest` gelen parametreleri, `ImageResponse` dönüş verisini,
`ImageListResponse` liste endpoint'ini tanımlar.
`model_config = ConfigDict(from_attributes=True)` ile ORM nesnelerini doğrudan dönüştürür.

```python
# İçermesi gerekenler:
# class ResizeRequest(BaseModel):
#   width: int = Field(gt=0, le=4096)
#   height: int = Field(gt=0, le=4096)
#   quality: int = Field(default=85, ge=1, le=100)
#   format: Literal["JPEG","PNG","WEBP"] = "JPEG"
#
# class ImageResponse(BaseModel):
#   id, original_filename, s3_bucket, s3_key
#   original_width, original_height, resized_width, resized_height
#   file_size_bytes, content_type, created_at, presigned_url: str | None = None
#   model_config = ConfigDict(from_attributes=True)
#
# class ImageListResponse(BaseModel):
#   items: list[ImageResponse]
#   total: int
```

---

### `app/services.py`
**Ne yapar:** İş mantığının kalbi. İki ana servis içerir:
1. `ImageResizeService` — Pillow ile resmi belleğe yükler, boyutlandırır, bytes olarak döner
2. `S3Service` — boto3 ile LocalStack/AWS S3'e bağlanır; upload, presigned URL üretme ve silme işlemlerini yapar

S3 bağlantısı için `AWS_ENDPOINT_URL` env varsa (LocalStack) onu kullanır,
yoksa gerçek AWS'e bağlanır. Bucket yoksa otomatik oluşturur.

```python
# ImageResizeService içermesi gerekenler:
# - def resize(image_bytes: bytes, width: int, height: int, quality: int, fmt: str) -> tuple[bytes, int, int]
#   PIL.Image.open(BytesIO(image_bytes)) → thumbnail veya resize → BytesIO → return bytes, w, h
# - def get_image_dimensions(image_bytes: bytes) -> tuple[int, int]
#
# S3Service içermesi gerekenler:
# - __init__: boto3.client("s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL"), ...)
# - def upload(bucket: str, key: str, data: bytes, content_type: str) -> None
# - def generate_presigned_url(bucket: str, key: str, expiry: int = 3600) -> str
# - def delete(bucket: str, key: str) -> None
# - def ensure_bucket(bucket: str) -> None
```

---

### `app/metrics.py`
**Ne yapar:** Prometheus metriklerini tanımlar. `prometheus-fastapi-instrumentator` kütüphanesini
kullanarak FastAPI app'e otomatik HTTP metriklerini ekler (`/metrics` endpoint açar).
Ek olarak üç custom counter/histogram tanımlar:
- `resize_operations_total` (counter) — toplam boyutlandırma sayısı
- `resize_duration_seconds` (histogram) — boyutlandırma süresi
- `s3_upload_duration_seconds` (histogram) — S3 yükleme süresi

```python
# İçermesi gerekenler:
# from prometheus_fastapi_instrumentator import Instrumentator
# from prometheus_client import Counter, Histogram
#
# RESIZE_TOTAL = Counter("resize_operations_total", "Total resize ops", ["status","format"])
# RESIZE_DURATION = Histogram("resize_duration_seconds", "Resize duration", buckets=[.01,.05,.1,.5,1,2])
# S3_UPLOAD_DURATION = Histogram("s3_upload_duration_seconds", "S3 upload duration")
#
# def setup_metrics(app: FastAPI) -> None:
#   Instrumentator().instrument(app).expose(app)
```

---

### `app/main.py`
**Ne yapar:** FastAPI uygulamasının giriş noktası. Tüm endpointleri barındırır,
lifespan ile uygulama başlarken DB tablolarını ve S3 bucket'ını oluşturur,
CORS middleware ekler, metrics setup'ı çağırır.

**Endpoint listesi (tümünü yaz):**

| Method | Path | Açıklama |
|--------|------|----------|
| `POST` | `/resize` | Multipart form: `file` (UploadFile) + `width` + `height` + `quality` + `format` parametreleri alır. Resmi boyutlandırır, S3'e yükler, DB'ye kaydeder, `ImageResponse` döner. |
| `GET` | `/images` | Tüm kayıtları sayfalı döner (`skip`, `limit` query param). `ImageListResponse` döner. |
| `GET` | `/images/{image_id}` | Tek kayıt + presigned URL üretip döner. 404 varsa HTTPException. |
| `DELETE` | `/images/{image_id}` | DB kaydını ve S3 objesini siler. 204 döner. |
| `GET` | `/health` | `{"status": "ok", "timestamp": ...}` döner. Smoke test için. |
| `GET` | `/metrics` | Prometheus scrape (metrics.py setup eder). |

```python
# S3 key formatı: f"resized/{uuid4().hex}_{filename}"
# S3_BUCKET = os.getenv("S3_BUCKET", "image-resize-bucket")
# lifespan içinde: Base.metadata.create_all(bind=engine) ve s3_service.ensure_bucket(S3_BUCKET)
```

---

### `tests/conftest.py`
**Ne yapar:** Pytest fixture'larının merkezi. Tüm testlerin ortak ihtiyaçlarını karşılar:
- `db_session` — in-memory SQLite ile her test için temiz DB
- `client` — TestClient (app dependency override ile `db_session`'ı enjekte eder)
- `mock_s3` — moto ile S3'ü mocklar, gerçek AWS'e istek atmaz
- `sample_image_bytes` — 100x100 kırmızı JPEG bytes (Pillow ile oluştur, dosyadan okuma)
- `s3_service` — mock S3 ile S3Service instance'ı

```python
# Önemli: app.dependency_overrides[get_db] = lambda: db_session kullan
# Her test sonunda override temizle
# moto: @mock_aws dekoratörü yerine fixture içinde mock_s3() context manager kullan
```

---

### `tests/factories.py`
**Ne yapar:** Factory Boy ile gerçekçi test verisi üretir.
`ImageRecordFactory` SQLAlchemy modelini Faker verileriyle doldurur.
Gerçek bir S3 key'i simüle eden `s3_key`, rastgele boyutlar, dosya boyutları üretir.

```python
# İçermesi gerekenler:
# import factory
# from factory.alchemy import SQLAlchemyModelFactory
# from faker import Faker
# from app.models import ImageRecord
#
# fake = Faker()
#
# class ImageRecordFactory(SQLAlchemyModelFactory):
#   class Meta:
#     model = ImageRecord
#     sqlalchemy_session_persistence = "commit"
#
#   original_filename = factory.LazyFunction(lambda: fake.file_name(extension="jpg"))
#   s3_bucket = "image-resize-bucket"
#   s3_key = factory.LazyFunction(lambda: f"resized/{fake.uuid4()}.jpg")
#   original_width = factory.LazyFunction(lambda: fake.random_int(min=100, max=4000))
#   original_height = factory.LazyFunction(lambda: fake.random_int(min=100, max=4000))
#   resized_width = factory.LazyFunction(lambda: fake.random_int(min=50, max=800))
#   resized_height = factory.LazyFunction(lambda: fake.random_int(min=50, max=800))
#   file_size_bytes = factory.LazyFunction(lambda: fake.random_int(min=1000, max=500000))
#   content_type = "image/jpeg"
#   created_at = factory.LazyFunction(datetime.utcnow)
```

---

### `tests/unit/test_resize.py`
**Ne yapar:** `ImageResizeService`'i izole unit testler. Dış bağımlılık yok (S3, DB yok).
Coverage hedefi bu modül için %90+.

```python
# Test edilmesi gereken durumlar:
# 1. test_resize_returns_correct_dimensions — 200x200 resmi 100x100'e boyutlandırınca doğru boyut
# 2. test_resize_jpeg_output — çıktı bytes geçerli JPEG mi (PIL.Image.open ile doğrula)
# 3. test_resize_png_format — PNG formatında çıktı
# 4. test_resize_webp_format — WEBP formatında çıktı
# 5. test_get_image_dimensions — orijinal boyutları doğru okur mu
# 6. test_resize_invalid_bytes — bozuk bytes girince ValueError fırlatır mı
# 7. test_resize_quality_affects_size — quality=10 vs quality=95, dosya boyutu farkı
# 8. test_resize_aspect_ratio — thumbnail modda aspect ratio korunuyor mu
```

---

### `tests/unit/test_schemas.py`
**Ne yapar:** Pydantic şema doğrulamalarını test eder. FastAPI'ye istek atmaz.

```python
# Test edilmesi gereken durumlar:
# 1. test_resize_request_valid — geçerli parametreler kabul edilir
# 2. test_resize_request_invalid_width — width=0 veya negatif RedirectResponse değil ValidationError
# 3. test_resize_request_max_dimension — 4097 genişlik reddedilir
# 4. test_resize_request_invalid_format — "GIF" formatı reddedilir
# 5. test_image_response_from_orm — SQLAlchemy modeli from_orm ile dönüşür
```

---

### `tests/integration/test_api.py`
**Ne yapar:** FastAPI endpoint'lerini TestClient ile end-to-end test eder (ama S3 mock'lu).
Gerçek HTTP istekleri simüle eder, response kodları ve body'leri kontrol eder.

```python
# Test edilmesi gereken durumlar (3 adet integration test zorunlu, 6 yaz):
# 1. test_resize_endpoint_success — POST /resize 200 döner, response body ImageResponse formatında
# 2. test_resize_endpoint_invalid_file — geçersiz dosya (txt) 400/422 döner
# 3. test_get_images_empty — GET /images boş DB'de [] döner
# 4. test_get_image_by_id — POST sonra GET /images/{id} çalışır
# 5. test_delete_image — POST sonra DELETE 204 döner
# 6. test_health_endpoint — GET /health 200 ve status:ok döner
#
# Fixtures: client, mock_s3, sample_image_bytes kullan
```

---

### `tests/integration/test_s3.py`
**Ne yapar:** S3Service'i moto ile mock edilmiş AWS S3'e karşı test eder.
Gerçek boto3 çağrıları yapılır ama moto bunları yakalar, LocalStack gerekmez.

```python
# Test edilmesi gereken durumlar:
# 1. test_upload_and_retrieve — upload sonrası bucket'ta obje var mı
# 2. test_presigned_url_generated — URL string mi, boş değil mi
# 3. test_delete_removes_object — sil sonrası obje yok
# 4. test_ensure_bucket_idempotent — iki kez çağrılınca hata vermez
```

---

### `tests/integration/test_db.py`
**Ne yapar:** Testcontainers ile gerçek PostgreSQL container'ı ayağa kaldırır ve
veritabanı işlemlerini test eder. Bu testler biraz yavaştır (container başlatma süresi).

```python
# İçermesi gerekenler:
# from testcontainers.postgres import PostgresContainer
#
# @pytest.fixture(scope="module")
# def pg_engine():
#   with PostgresContainer("postgres:15-alpine") as pg:
#     engine = create_engine(pg.get_connection_url())
#     Base.metadata.create_all(engine)
#     yield engine
#
# Test edilmesi gereken durumlar (2 adet zorunlu):
# 1. test_create_image_record — Factory ile kayıt oluştur, ID atandı mı kontrol et
# 2. test_query_image_records — 5 kayıt ekle, hepsini çek, sayı doğru mu
```

---

### `tests/e2e/test_playwright.py`
**Ne yapar:** Playwright ile tarayıcı üzerinden gerçek kullanıcı senaryolarını çalıştırır.
Bunun için `ui/index.html` adında basit bir web arayüzü gerekir.
Testler `pytest-playwright` ile çalışır.

```python
# 3 senaryo (zorunlu):
# 1. test_upload_and_see_result
#    - Sayfayı aç
#    - Dosya seç (sample JPEG)
#    - Width=300, Height=300 gir
#    - "Resize" butonuna tıkla
#    - Sonuç kartının görünmesini bekle (data-testid="result-card")
#    - Başarı mesajı içeriyor mu kontrol et
#
# 2. test_list_images_after_upload
#    - Upload yap
#    - "List Images" butonuna tıkla
#    - Tabloda en az 1 satır var mı kontrol et
#
# 3. test_delete_image
#    - Upload yap
#    - Listele
#    - İlk satırdaki Delete butonuna tıkla
#    - Confirm dialog'u kabul et
#    - Satırın tablodan kalktığını kontrol et
```

---

### `ui/index.html`
**Ne yapar:** Playwright testlerinin çalışacağı minimal web arayüzü.
Sadece test edilebilir olmak için tasarlanmıştır (süslü görünmesi şart değil).
Vanilla HTML + JavaScript, CDN dependency yok, `fetch` API kullanır.

```html
<!-- İçermesi gerekenler:
- <input type="file" id="file-input" accept="image/*">
- <input type="number" id="width-input" value="300">
- <input type="number" id="height-input" value="300">
- <select id="format-select"> JPEG / PNG / WEBP </select>
- <button id="resize-btn">Resize</button>
- <div data-testid="result-card" id="result-card" hidden> — sonuç gösterir
- <button id="list-btn">List Images</button>
- <table id="images-table"> — satırların data-testid="image-row" olmalı
- Her satırda <button class="delete-btn" data-id="...">Delete</button>
- JavaScript: fetch("/resize", { method: "POST", body: FormData })
- JavaScript: fetch("/images") ile tabloyu doldur
- JavaScript: fetch("/images/{id}", { method: "DELETE" }) ile sil
- API_BASE_URL = window.location.origin üzerinden dinamik al
-->
```

---

### `Dockerfile`
**Ne yapar:** İki aşamalı (multi-stage) Docker imajı.
- **Stage 1 (builder):** `python:3.11-slim` üzerinde bağımlılıkları `/install`'a kurar
- **Stage 2 (runtime):** Sadece build artifact'larını kopyalar, geliştirme araçları olmaz.
Final imaj ~200MB hedef. Non-root user (`appuser`) ile çalışır.

```dockerfile
# Stage 1: builder
# FROM python:3.11-slim AS builder
# WORKDIR /install
# COPY requirements.txt .
# RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: runtime
# FROM python:3.11-slim
# COPY --from=builder /install /usr/local
# WORKDIR /app
# COPY app/ ./app/
# COPY ui/ ./ui/
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser
# EXPOSE 8000
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### `docker-compose.yml`
**Ne yapar:** Lokal geliştirme ortamını tek komutla ayağa kaldırır.
4 servis içerir: `app`, `db` (PostgreSQL), `localstack` (AWS S3 simülasyonu), `grafana`+`prometheus`.

```yaml
# services:
#   app:
#     build: .
#     ports: ["8000:8000"]
#     environment:
#       DATABASE_URL: postgresql://postgres:postgres@db:5432/imagedb
#       AWS_ENDPOINT_URL: http://localstack:4566
#       AWS_ACCESS_KEY_ID: test
#       AWS_SECRET_ACCESS_KEY: test
#       AWS_DEFAULT_REGION: us-east-1
#       S3_BUCKET: image-resize-bucket
#     depends_on: [db, localstack]
#
#   db:
#     image: postgres:15-alpine
#     environment: {POSTGRES_DB: imagedb, POSTGRES_PASSWORD: postgres}
#     volumes: [postgres_data:/var/lib/postgresql/data]
#
#   localstack:
#     image: localstack/localstack:3
#     ports: ["4566:4566"]
#     environment: {SERVICES: s3, DEFAULT_REGION: us-east-1}
#
#   prometheus:
#     image: prom/prometheus:latest
#     volumes: [./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml]
#     ports: ["9090:9090"]
#
#   grafana:
#     image: grafana/grafana:latest
#     ports: ["3000:3000"]
#     environment: {GF_SECURITY_ADMIN_PASSWORD: admin}
#     volumes: [grafana_data:/var/lib/grafana]
#
# volumes: postgres_data, grafana_data
```

---

### `requirements.txt`
**Ne yapar:** Production bağımlılıkları. Runtime'da gerekli olan minimum paket seti.

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
sqlalchemy>=2.0.0
pillow>=10.3.0
boto3>=1.34.0
python-multipart>=0.0.9
pydantic>=2.7.0
prometheus-fastapi-instrumentator>=6.1.0
prometheus-client>=0.20.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
```

---

### `requirements-dev.txt`
**Ne yapar:** Sadece test ve geliştirme ortamında gerekli paketler.
Production imajına girmez.

```
-r requirements.txt
pytest>=8.2.0
pytest-cov>=5.0.0
pytest-asyncio>=0.23.0
pytest-playwright>=0.5.0
httpx>=0.27.0
factory-boy>=3.3.0
faker>=25.0.0
moto[s3]>=5.0.0
testcontainers[postgres]>=4.5.0
locust>=2.28.0
```

---

### `pytest.ini`
**Ne yapar:** Pytest konfigürasyonu. Test discovery, coverage ayarları ve marker tanımları.

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=70
    -v
markers =
    unit: Unit testler (harici bağımlılık yok)
    integration: Integration testler (mock servisler)
    e2e: Playwright end-to-end testler
    slow: Yavaş testler (testcontainers)
```

---

### `monitoring/prometheus.yml`
**Ne yapar:** Prometheus'a hangi hedefleri scrape edeceğini söyler.
`app:8000/metrics` endpoint'ini 15 saniyede bir sorgular.

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "image-resize-service"
    static_configs:
      - targets: ["app:8000"]
    metrics_path: /metrics
```

---

### `monitoring/grafana_dashboard.json`
**Ne yapar:** Grafana'ya import edilecek hazır dashboard JSON.
3 panel içerir (zorunlu minimum):
1. **Request Rate** — `rate(http_requests_total[1m])` — saniyedeki istek sayısı
2. **P95 Latency** — `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` — 95. yüzdelik gecikme
3. **Resize Operations** — `rate(resize_operations_total[1m])` — boyutlandırma işlem hızı

Tam bir Grafana dashboard JSON nesnesi yaz (uid, panels, datasource, templating dahil).
datasource uid olarak `"prometheus"` kullan.

---

### `performance/k6_script.js`
**Ne yapar:** k6 ile yük testi senaryosu. 50 sanal kullanıcı, 30 saniye boyunca
`POST /resize` endpoint'ine gerçek JPEG dosyası göndererek p95 latency ölçer.

```javascript
// İçermesi gerekenler:
// import http from 'k6/http';
// import { check, sleep } from 'k6';
// import { Trend, Counter } from 'k6/metrics';
//
// export const options = {
//   vus: 50,
//   duration: '30s',
//   thresholds: {
//     http_req_duration: ['p(95)<2000'],  // p95 < 2sn
//     http_req_failed: ['rate<0.05'],      // hata oranı < %5
//   },
// };
//
// const resizeDuration = new Trend('resize_duration');
// const resizeErrors = new Counter('resize_errors');
//
// export default function () {
//   // open('sample.jpg') ile test resmi aç VEYA programatik binary oluştur
//   // FormData ile POST /resize?width=300&height=300 gönder
//   // check ile 200 kontrolü yap
//   // resizeDuration.add(response.timings.duration)
//   // sleep(1)
// }
//
// export function handleSummary(data) {
//   return { 'performance/results.json': JSON.stringify(data) };
// }
```

---

### `postman/collection.json`
**Ne yapar:** Newman ile CI'da otomatik çalışacak Postman koleksiyonu.
5 istek içerir, her biri test script'leri ile birlikte.

```json
// Koleksiyon yapısı (tam JSON olarak yaz):
// {
//   "info": { "name": "Image Resize Service", "schema": "..." },
//   "variable": [{ "key": "baseUrl", "value": "http://localhost:8000" }],
//   "item": [
//     {
//       "name": "Health Check",
//       "request": { "method": "GET", "url": "{{baseUrl}}/health" },
//       "event": [{ "listen": "test", "script": "pm.test('status 200', () => pm.response.to.have.status(200))" }]
//     },
//     {
//       "name": "Resize Image",
//       "request": { "method": "POST", "url": "{{baseUrl}}/resize",
//         "body": { "mode": "formdata", "formdata": [
//           { "key": "file", "type": "file", "src": "sample.jpg" },
//           { "key": "width", "value": "300" },
//           { "key": "height", "value": "300" }
//         ]}
//       },
//       "event": [{ "listen": "test", "script":
//         "pm.test('has id', () => pm.expect(pm.response.json()).to.have.property('id'));\npm.environment.set('imageId', pm.response.json().id);"
//       }]
//     },
//     { "name": "List Images", GET /images, test: array döndü mü },
//     { "name": "Get Image By ID", GET /images/{{imageId}}, test: id eşleşiyor mu },
//     { "name": "Delete Image", DELETE /images/{{imageId}}, test: 204 döndü mü }
//   ]
// }
```

---

### `k8s/configmap.yaml`
**Ne yapar:** Kubernetes ConfigMap — uygulamanın environment değişkenlerini pod'dan bağımsız saklar.
Bu sayede aynı Docker imajı farklı ortamlarda (dev/staging/prod) farklı config ile çalışır.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: image-resize-config
  namespace: default
data:
  AWS_ENDPOINT_URL: "http://localstack-service:4566"
  AWS_DEFAULT_REGION: "us-east-1"
  S3_BUCKET: "image-resize-bucket"
  LOG_LEVEL: "info"
```

---

### `k8s/deployment.yaml`
**Ne yapar:** Kubernetes Deployment — uygulamayı Minikube üzerinde 2 replica olarak çalıştırır.
Liveness ve readiness probe `/health` endpoint'ini kullanır.
ConfigMap'i environment variable olarak mount eder.
Secret'lardan (DATABASE_URL, AWS credentials) env var alır.

```yaml
# apiVersion: apps/v1
# kind: Deployment
# metadata: name: image-resize-service
# spec:
#   replicas: 2
#   selector: matchLabels: app: image-resize-service
#   template:
#     spec:
#       containers:
#       - name: app
#         image: image-resize-service:latest
#         imagePullPolicy: Never  # Minikube local image için
#         ports: [containerPort: 8000]
#         envFrom: [configMapRef: name: image-resize-config]
#         env:
#           - name: DATABASE_URL
#             valueFrom: secretKeyRef: name: app-secrets, key: database-url
#         livenessProbe:
#           httpGet: path: /health, port: 8000
#           initialDelaySeconds: 10, periodSeconds: 30
#         readinessProbe:
#           httpGet: path: /health, port: 8000
#           initialDelaySeconds: 5, periodSeconds: 10
#         resources:
#           requests: {memory: "128Mi", cpu: "100m"}
#           limits: {memory: "512Mi", cpu: "500m"}
```

---

### `k8s/service.yaml`
**Ne yapar:** Kubernetes Service — pod'ları dış dünyaya açar.
`NodePort` tipiyle Minikube'de `minikube service image-resize-service` komutuyla erişilebilir olur.

```yaml
# apiVersion: v1
# kind: Service
# metadata: name: image-resize-service
# spec:
#   type: NodePort
#   selector: app: image-resize-service
#   ports:
#   - port: 80, targetPort: 8000, nodePort: 30080
```

---

### `.github/workflows/ci.yml`
**Ne yapar:** GitHub Actions CI/CD pipeline. Her push ve pull request'te tetiklenir.
5 sıralı job içerir; önceki başarısız olursa sonraki çalışmaz.

```yaml
# name: CI/CD Pipeline
# on: push (branches: main, develop), pull_request
#
# jobs:
#
#   lint:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-python@v5 (python-version: "3.11")
#       - run: pip install ruff
#       - run: ruff check app/ tests/
#
#   test:
#     needs: lint
#     runs-on: ubuntu-latest
#     services:
#       localstack:
#         image: localstack/localstack:3
#         ports: ["4566:4566"]
#         env: {SERVICES: s3}
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-python@v5
#       - run: pip install -r requirements-dev.txt
#       - run: pytest tests/unit tests/integration --cov=app --cov-fail-under=70
#       - uses: actions/upload-artifact@v4 (path: htmlcov/)
#
#   docker-build:
#     needs: test
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - uses: docker/setup-buildx-action@v3
#       - run: docker build -t image-resize-service:${{ github.sha }} .
#       - run: docker save image-resize-service:${{ github.sha }} | gzip > image.tar.gz
#       - uses: actions/upload-artifact@v4 (path: image.tar.gz)
#
#   newman:
#     needs: docker-build
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - run: docker compose up -d app localstack db
#       - run: sleep 10  # servisin ayağa kalkması için bekle
#       - run: npx newman run postman/collection.json --env-var baseUrl=http://localhost:8000
#       - run: docker compose down
#
#   smoke:
#     needs: newman
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - run: docker compose up -d
#       - run: sleep 10
#       - run: curl -f http://localhost:8000/health
#       - run: echo "Smoke test passed!"
#       - run: docker compose down
```

---

### `.env.example`
**Ne yapar:** Geliştiricilere hangi environment variable'ların gerekli olduğunu gösterir.
Gerçek değerleri `.env` dosyasında saklanır (git'e commit edilmez).

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/imagedb
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=image-resize-bucket
LOG_LEVEL=info
```

---

### `README.md`
**Ne yapar:** Projenin kapısı. Hem değerlendirici hem de yeni geliştirici için
"sıfırdan çalışır hale getir" rehberi ve mimari özet içerir.

```markdown
# Image Resize Service

## Proje Özeti
FastAPI tabanlı mikroservis. Resim yükle → Pillow ile boyutlandır → LocalStack S3'e kaydet.
"Bulut Mimarilerinde Test Mühendisliği" dersi dönem projesi.

## Mimari
[Buraya mimari diyagram eklenecek — draw.io veya Mermaid]

## Hızlı Başlangıç
\`\`\`bash
git clone <repo>
cd image-resize-service
cp .env.example .env
docker compose up -d
# → http://localhost:8000/docs  (Swagger UI)
# → http://localhost:3000       (Grafana — admin/admin)
# → http://localhost:9090       (Prometheus)
\`\`\`

## Testleri Çalıştır
\`\`\`bash
pip install -r requirements-dev.txt
pytest tests/unit tests/integration -v          # Hızlı testler
pytest tests/ -v                                 # Tüm testler (yavaş)
pytest --cov=app --cov-report=html               # Coverage raporu
\`\`\`

## Performans Testi
\`\`\`bash
k6 run performance/k6_script.js
\`\`\`

## Kubernetes (Minikube)
\`\`\`bash
minikube start
eval $(minikube docker-env)
docker build -t image-resize-service:latest .
kubectl apply -f k8s/
minikube service image-resize-service
\`\`\`

## API Endpoint'leri
| Method | Path | Açıklama |
|--------|------|----------|
| POST | /resize | Resim yükle ve boyutlandır |
| GET | /images | Tüm kayıtları listele |
| GET | /images/{id} | Tek kayıt + presigned URL |
| DELETE | /images/{id} | Kaydı ve S3'teki dosyayı sil |
| GET | /health | Sağlık kontrolü |
| GET | /metrics | Prometheus metrikleri |

## Teknik Yığın
- **Servis:** FastAPI + Uvicorn
- **Resim İşleme:** Pillow
- **Veritabanı:** SQLite (dev) / PostgreSQL (prod) + SQLAlchemy
- **Depolama:** AWS S3 — LocalStack ile simüle edilir
- **Test:** Pytest + moto + Testcontainers + Playwright
- **CI/CD:** GitHub Actions
- **İzleme:** Prometheus + Grafana
- **Performans:** k6
- **Container:** Docker (multi-stage) + Docker Compose
- **Orkestrasyon:** Kubernetes (Minikube)
```

---

## SON TALİMATLAR

1. Yukarıdaki **tüm dosyaları** oluştur — hiçbirini atlama.
2. Her dosyanın başına `# Bu dosya: [kısa açıklama]` yorumu ekle.
3. Kodlar çalışır olmalı — import hatası, syntax hatası olmamalı.
4. `pytest tests/unit tests/integration` komutu hatasız geçmeli.
5. `docker compose build` hatasız tamamlanmalı.
6. Type hint'leri kullan (mypy uyumlu).
7. Her fonksiyonun docstring'i olsun.
8. Hiçbir yerde hardcoded secret veya credentials olmasın — hepsi env var.
9. `app/main.py` içinde FastAPI app nesnesi `app` adında olsun (uvicorn için).
10. Testlerde `assert` yerine pytest assertion kullan (hata mesajları daha açıklayıcı).i


"Hocam, sistemimiz endüstri standardı olan 'Bounding Box' prensibine göre çalışıyor. Resimlerin orijinal oranlarını bozup yamulmalarını engellemek için Pillow'un thumbnail algoritmasını kullandık. Böylece resimler deforme olmadan hedef çerçevenin içine güvenle sığıyor."


