# Sunum ve Proje Dokümantasyon Kılavuzu
**Ders:** Bulut Mimarilerinde Test Mühendisliği (Test Engineering in Cloud Architectures)  
**Proje:** Resim Boyutlandırma Mikroservisi (Image Resize Service)

Bu kılavuz, projenizin tüm klasör ve dosya yapısını, kullanılan teknolojileri ve sunum sırasında hocanıza anlatabileceğiniz **Test Mühendisliği** kavramlarını detaylandırmak için hazırlanmıştır.

---

## 📂 Proje Dizin Yapısı (Directory Structure)

```text
image-resize-service/
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD (GitHub Actions) iş akışı
├── app/                          # Uygulama kaynak kodları (FastAPI Backend)
│   ├── database.py               # Veritabanı bağlantısı ve session yönetimi
│   ├── main.py                   # API Endpoint'leri ve uygulama ana giriş kapısı
│   ├── metrics.py                # Prometheus özel metrik tanımlamaları
│   ├── models.py                 # SQLAlchemy (Veritabanı) ORM Modelleri
│   ├── schemas.py                # Pydantic (Veri Doğrulama) şemaları
│   └── services.py               # Resim işleme (Pillow) & S3 (Boto3) servisleri
├── ui/                           # Ön Yüz (Frontend)
│   └── index.html                # Vanilla JS & CSS ile tasarlanmış SPA arayüzü
├── tests/                        # Test Otomasyon Dizinleri
│   ├── e2e/
│   │   └── test_playwright.py    # Playwright ile uçtan uca tarayıcı testleri
│   ├── integration/
│   │   ├── test_api.py           # API Endpoint entegrasyon testleri
│   │   ├── test_db.py            # SQLite/PostgreSQL veritabanı entegrasyon testleri
│   │   └── test_s3.py            # S3 (Moto ile mock'lanmış) entegrasyon testleri
│   ├── unit/
│   │   ├── test_resize.py        # Pillow resim boyutlandırma algoritmik birim testleri
│   │   └── test_schemas.py       # Pydantic girdi doğrulama birim testleri
│   ├── conftest.py               # Pytest fixture'ları, mock'lar ve test veritabanı ayarları
│   └── factories.py              # Faker ile dinamik test verisi üretici fabrikalar
├── monitoring/                   # İzlenebilirlik (Observability)
│   ├── prometheus.yml            # Prometheus metrik toplama konfigürasyonu
│   └── grafana_dashboard.json    # Grafana Dashboard şablonu (3 adet özel grafik)
├── performance/                  # Yük ve Performans Testi
│   └── k6_script.js              # Grafana k6 yük testi senaryosu
├── postman/                      # API Test Koleksiyonları
│   └── collection.json           # Postman / Newman entegrasyonu için koleksiyon dosyası
├── k8s/                          # Kubernetes Dağıtım Dosyaları
│   ├── configmap.yaml            # Çevre değişkenleri tanımları
│   ├── deployment.yaml           # Pod ve replika tanımları
│   └── service.yaml              # Servis (LoadBalancer) tanımı
├── Dockerfile                    # İki aşamalı (Multi-stage) Docker imaj tanımı
├── docker-compose.yml            # Tüm yapıyı (App, DB, LocalStack, Prometheus, Grafana) tek tuşla kaldıran dosya
├── pytest.ini                    # Pytest çalışma ve kapsama (coverage) kuralları
├── requirements.txt              # Üretim ortamı bağımlılıkları
├── requirements-dev.txt          # Test ve geliştirme ortamı bağımlılıkları
└── README.md                     # Genel proje kılavuzu ve mimari şema
```

---

## 📄 Dosya Rolleri ve Detayları

### 1. Backend (`app/`)
* **`main.py`**: API'nin omurgasıdır. `/resize`, `/images`, `/images/{id}` ve `/health` endpoint'lerini barındırır. FastAPI'nin `lifespan` özelliğini kullanarak uygulama başlarken veritabanı tablolarını ve S3 kovanını (bucket) otomatik oluşturur.
* **`database.py`**: SQLite (geliştirme) veya PostgreSQL (canlı ortam) bağlantılarını yönetir. Thread-safe oturum yönetimi sunar.
* **`models.py`**: Veritabanındaki `ImageRecord` tablosunu tanımlar. Yüklenen resmin orijinal adı, S3 anahtarı (key), genişlik, yükseklik ve oluşturulma tarihi gibi metadataları saklar.
* **`schemas.py`**: Gelen isteklerin (örneğin genişlik `10` ile `5000` piksel arasında mı?) ve dönen yanıtların biçimini Pydantic ile doğrular.
* **`services.py`**:
  * **`ImageResizeService`**: Pillow kütüphanesini kullanarak resim boyutunu en-boy oranını bozmadan ayarlar, format dönüşümü (JPEG, PNG, WEBP) ve kalite optimizasyonu yapar.
  * **`S3Service`**: AWS S3 API'si ile konuşur. Güvenli olması açısından resimlerin adını rastgele UUID'ler haline getirerek path traversal (dizin aşımı) açıklarını engeller. Dosyalara erişim için süreli **Presigned URL** üretir.
* **`metrics.py`**: Prometheus için özel metrikler tanımlar (Örn: Toplam boyutlandırılan resim sayısı, resim boyutlandırmanın milisaniye cinsinden süresi).

### 2. Frontend (`ui/`)
* **`index.html`**: Vanilla CSS ile koyu tema (dark mode) tasarımı içerir. Güvenlik kuralları gereği, XSS açıklarını önlemek adına `innerHTML` yerine güvenli DOM metotları (`textContent`, `createElement`) kullanılarak yazılmıştır. API'den gelen verileri dinamik listeler.

### 3. Test Katmanı (`tests/`)
* **`conftest.py`**: Testlerin kalbidir. SQLite veritabanını `:memory:` (bellek içi) olarak ayarlar ve her testte sıfırlanmasını sağlar. AWS S3 bağlantılarını engellemek ve taklit etmek için `moto` kütüphanesini burada devreye sokar.
* **`factories.py`**: Testler sırasında elle veri girmek yerine, `factory-boy` ve `Faker` kullanarak rastgele ve gerçekçi resim kayıtları üretir.
* **`unit/`**: Sadece kodun en küçük birimlerini test eder. Pillow'un resmi doğru boyutlandırıp boyutlandırmadığını veya şemaların yanlış girdileri engelleyip engellemediğini test eder. Veritabanına veya S3'e bağlanmaz (Çok hızlıdır).
* **`integration/`**: API, DB ve S3'ün birbiriyle uyumunu test eder. Veritabanına yazma, S3'e dosya atma ve FastAPI endpoint yanıtlarının doğruluğunu test eder.
* **`e2e/`**: Playwright aracı ile tarayıcıyı (Chromium) arka planda gerçekten açar. Resim yükleme butonuna tıklar, resmin ekranda belirdiğini doğrular ve silme butonunun işlevselliğini uçtan uca test eder.

---

## 🎓 Sunum Sırasında Anlatılacak Temel Test Mühendisliği Kavramları

Sınıfta sunum yaparken projenin sadece kodlanmasından ziyade **nasıl test edildiğine** odaklanmanız hocanızın çok hoşuna gelecektir. İşte vurgulamanız gereken anahtar noktalar:

### 1. Test Piramidi (Test Pyramid) Uygulaması
Projeyi test piramidine uygun tasarladık:
* **Unit Tests (Birim Testler):** Çok hızlı çalışan, bağımlılığı olmayan testler (En altta ve en fazla sayıda olanlar).
* **Integration Tests (Entegrasyon Testleri):** API, DB ve S3'ün birbirleriyle olan iletişimini test eden orta katman.
* **E2E Tests (Uçtan Uca Testler):** Kullanıcı senaryolarını tarayıcıda taklit eden Playwright testleri (En üstte, en yavaş ama en gerçekçi testler).

### 2. Mocking vs Emulation (Taklit Etme ve Simüle Etme)
Bulut mimarilerinde dış servis bağımlılıkları test etmeyi zorlaştırır. Biz bu problemi iki farklı yöntemle çözdük:
* **Mocking (Testlerde):** Pytest çalışırken gerçek bir AWS faturası çıkmaması ve internet gerekmemesi için **`moto`** kütüphanesini kullandık. `moto` AWS S3'ü RAM üzerinde taklit eder.
* **Emulation (Geliştirmede):** Docker Compose ortamında yerel bir AWS gibi davranan **`LocalStack`** kullandık. Bu sayede kodumuz hiçbir değişiklik gerekmeden yarın gerçek AWS'ye taşınabilir.

### 3. Kod Kapsama Oranı (Code Coverage)
* Sunumda testlerimizin kodun ne kadarını çalıştırdığını gösteren **%80.97**'lik test kapsamını vurgulayın. `pytest-cov` ile satır satır hangi kodun testten geçtiğini raporlayabiliyoruz.

### 4. Yük ve Performans Testi (Load Testing)
* **Grafana k6** kullanarak sisteme anlık yük bindiren bir test scripti hazırladık. Bu sayede API'nin yüksek trafik altında ne kadar sürede yanıt verdiğini (latency) ve saniyede kaç isteği (RPS) karşılayabildiğini ölçebiliyoruz.

### 5. Sürekli Entegrasyon (CI/CD Pipeline)
* GitHub Actions entegrasyonu sayesinde projeye yeni bir kod eklendiğinde sistem otomatik olarak:
  1. Kod stilini kontrol eder.
  2. Tüm testleri (Playwright dahil) koşturur.
  3. Kapsama oranının belirlenen sınırın altına düşmediğinden emin olur.

### 6. Güvenli Kodlama (Secure Coding)
* **Girdi Sınırlandırması:** Maksimum resim boyutu `10MB` ile sınırlandırıldı. Boyutlandırma genişlikleri `10px` - `5000px` arasına kısıtlandı. (DDoS ve bellek şişirme saldırılarına karşı koruma).
* **Dosya Yolları Güvenliği (Path Injection & Traversal):** Kullanıcının yüklediği dosya adı doğrudan S3'e yazılmıyor. Sistem rastgele UUID'ler üretiyor. Böylece `../../etc/passwd` gibi zararlı dosya adı manipülasyonları engelleniyor.
* **XSS Koruması:** Ön yüzde `innerHTML` kullanılmadı, sadece tarayıcının güvenli text elementleri tercih edildi.
