# Bulut Mimarilerinde Test Mühendisliği Dönem Projesi Sunum Raporu

**Hocam Merhaba,**

Bu raporda, "Bulut Mimarilerinde Test Mühendisliği" dersi kapsamında geliştirdiğim ve tüm test otomasyon süreçlerini uçtan uca kurguladığım **Resim Boyutlandırma Mikroservisi (Image Resize Service)** projesini, kullandığım teknolojileri, mimari kararlarımı ve özellikle test mühendisliği yaklaşımlarımı detaylıca açıklayacağım. 

Projeyi tamamen çalışır, konteynerize edilmiş ve **%80.97 kod kapsama oranıyla (test coverage)** teslim edilmeye hazır hale getirdim.

---

## 🏛️ 1. Genel Mimari ve İş Akışı

Hocam, geliştirdiğim mikroservis temel olarak kullanıcılardan aldığı resimleri en-boy oranını bozmadan boyutlandıran, bunları bulut depolama servisine yükleyen ve metadata bilgilerini veritabanında saklayan bir yapıya sahiptir. 

Sistemin iş akışı şu adımlardan oluşmaktadır:
1. **İstek (Request):** İstemci (tarayıcı veya API istemcisi), `/resize` endpoint'ine boyutlandırmak istediği resmi ve hedef ölçüleri (genişlik, yükseklik, kalite, format) gönderir.
2. **Doğrulama (Validation):** FastAPI ve Pydantic modelleri istek parametrelerini doğrular. Dosyanın boş olup olmadığını ve boyutunun **10MB** sınırını aşıp aşmadığını kontrol eder.
3. **Boyutlandırma (Processing):** Pillow kütüphanesi yardımıyla resim bellekte işlenir. En-boy oranı korunarak hedef boyutlara indirgenir.
4. **Bulut Depolama (S3):** Güvenlik amacıyla dosyanın orijinal adı değiştirilerek benzersiz bir UUID (örn: `a3f5b8...webp`) atanır ve AWS S3 (veya yerelde LocalStack) üzerine yüklenir.
5. **Veri Kaydı (Database):** Dosyanın orijinal ismi, S3 üzerindeki yolu, boyutu, yeni genişlik/yükseklik değerleri veritabanına (SQLite/PostgreSQL) kaydedilir.
6. **Güvenli Erişim (Presigned URL):** Kullanıcıya resmin doğrudan S3 linkini vermek yerine, belirli bir süre geçerli olan (1 saat) güvenli bir **Presigned URL** üretilerek yanıt olarak dönülür.

---

## 🛠️ 2. Teknolojik Tercihlerim ve Gerekçeleri

Hocam, projede modern bulut standartlarını yakalamak adına şu araçları tercih ettim:

* **FastAPI (Python):** Hızlı, asenkron yapıda çalışan ve otomatik OpenAPI (Swagger UI) belgelendirmesi üreten bir web çatısı olduğu için tercih ettim. Performansı yük testlerinde de oldukça başarılı sonuçlar verdi.
* **Pillow:** Python ekosistemindeki en olgun ve hızlı resim işleme kütüphanesidir. Format dönüştürme (JPEG, PNG, WEBP) ve sıkıştırma kalitesi ayarlarını bununla gerçekleştirdim.
* **SQLAlchemy & PostgreSQL/SQLite:** Geliştirme aşamasında lokalde işimizi kolaylaştırması için SQLite kullandım. Ancak canlı ortama geçişte PostgreSQL kullanabilmek amacıyla SQLAlchemy ORM katmanını kullandım. Böylece kodda hiçbir değişiklik yapmadan çevre değişkeniyle DB değiştirebiliyoruz.
* **LocalStack & Moto (AWS S3 Simülasyonu):** Sunumun en can alıcı kısımlarından biri burası hocam. Gerçek bir AWS hesabı açıp fatura ödememek ve internet bağımlılığı yaşamamak için testlerde **Moto** kütüphanesini, lokal çalışma ortamında ise Docker üzerinde çalışan **LocalStack**'i kullandım.
* **Prometheus & Grafana:** Sistemimizin "gözlemlenebilirlik" (observability) durumunu test etmek amacıyla `/metrics` endpoint'i üzerinden Prometheus'a özel metrikler besledim ve Grafana panelleri hazırladım.
* **Docker & Kubernetes:** Uygulamayı hem Docker Compose ile çoklu konteyner olarak hem de Kubernetes (Minikube) manifestleri ile küme üzerinde ölçeklenebilir şekilde ayağa kaldırabiliyoruz.

---

## 🧪 3. Test Mühendisliği Yaklaşımım (Detaylı Analiz)

Hocam, dersimizin temel odağı olan **Test Mühendisliği** prensiplerini projenin her aşamasına entegre ettim. Projede **Test Piramidi** yapısını birebir uyguladım:

### A. Birim Testler (Unit Tests - `tests/unit/`)
Bu katmanda hiçbir dış servis (veritabanı veya S3 gibi) bağlantısı kurmadan, sadece fonksiyonel mantığı test ettim:
* **Algoritma Testleri (`test_resize.py`):** Pillow'un resmi en-boy oranını bozmadan doğru boyutlandırıp boyutlandırmadığını, kalite parametresinin dosya boyutunu etkileyip etkilemediğini, hatalı byte'lar gönderildiğinde sistemin doğru hata fırlatıp fırlatmadığını kontrol ettim.
* **Şema Doğrulama (`test_schemas.py`):** Pydantic şemalarının negatif genişlik/yükseklik değerlerini, 5000 piksel üzerindeki aşırı büyük boyut isteklerini veya desteklenmeyen dosya formatlarını (örn: BMP, GIF) doğru şekilde bloklayıp bloklamadığını doğruladım.

### B. Entegrasyon Testleri (Integration Tests - `tests/integration/`)
Burada sistem parçalarının birbiriyle uyumunu test ettim:
* **S3 Entegrasyonu (`test_s3.py`):** `moto` kütüphanesinin `@mock_aws` dekoratörünü kullanarak, RAM üzerinde sahte bir S3 ayağa kaldırdım. Kodumuzun gerçekten S3 bucket oluşturabildiğini, dosya yükleyebildiğini, presigned URL üretebildiğini ve sildiğini doğruladım.
* **Veritabanı Entegrasyonu (`test_db.py`):** Testler çalışırken diskteki veritabanını kirletmemek için bellek içi (SQLite `:memory:`) bir veritabanı yarattım. Tablolara yazma ve okuma işlemlerinin bütünlüğünü test ettim.
* **API Entegrasyonu (`test_api.py`):** FastAPI `TestClient` kullanarak HTTP istekleri attım. `/resize` endpoint'ine resim gönderildiğinde arka planda hem DB'ye yazıldığını hem de S3'e dosyanın gittiğini test ettim.

### C. Uçtan Uca Testler (E2E Tests - `tests/e2e/`)
Sistemi gerçek bir kullanıcının gözünden test etmek için **Playwright** kullandım:
* **Arayüz Senaryoları (`test_playwright.py`):** Test çalışırken arka planda headless (arayüzsüz) bir Chromium tarayıcısı açılır.
* `ui/index.html` sayfasını ziyaret eder, dosya yükleme girdisine bir test resmi yükler, yükle butonuna tıklar.
* Sonuç kartının ekranda belirdiğini, indirilebilir linkin oluştuğunu doğrular.
* Ardından silme butonuna tıklayarak resmin hem arayüzden hem de sistemden silindiğini doğrular.

### D. Performans ve Yük Testleri (Load Testing - `performance/`)
Sistemimizin yük altında nasıl davrandığını ölçmek için **Grafana k6** kullandık:
* `k6_script.js` dosyasında yazdığım senaryoda, sanal kullanıcılar (VUs) oluşturarak sisteme sürekli resim yükleme ve boyutlandırma istekleri gönderdim.
* Bu yük testi sırasında FastAPI'nin yanıt sürelerini (p95 latency) ve saniyede işleyebildiği istek sayısını (RPS) analiz ettim.

### E. Kod Kapsama Oranı (Code Coverage)
* Yazdığım tüm test senaryolarını koşturduğumuzda **%80.97**'lik bir kapsama oranına ulaşıyoruz. Bu değer, ders kapsamında hedeflenen %70 sınırının oldukça üzerindedir ve kritik işlevlerin (core business logic) tamamının testler tarafından güvence altına alındığını göstermektedir.

---

## 🔒 4. Güvenlik ve Dayanıklılık (Secure Coding)

Hocam, bulut uygulamalarında güvenlik en kritik konulardan biridir. Bu projede özellikle şu güvenlik önlemlerini aldım:
1. **Dosya Boyutu Sınırı (DDoS Koruması):** Kullanıcıların çok büyük boyutlu resimler yükleyerek sunucu belleğini tüketmesini (Out Of Memory hatası) önlemek için FastAPI middleware seviyesinde **10MB sınırlandırması** yaptım.
2. **Dizin Aşımı Koruması (Path Traversal Prevention):** Kullanıcı resminin adını doğrudan diskte veya S3'te saklamıyoruz. Kullanıcı `../../etc/passwd` gibi zararlı bir dosya adı gönderse bile, sistem bunu arka planda rastgele bir **UUIDv4** isme dönüştürür.
3. **XSS (Cross-Site Scripting) Koruması:** Ön yüz arayüzünde (Frontend), API'den gelen verileri ekrana yazdırırken asla `innerHTML` kullanmadım. Tamamen tarayıcının güvenli `textContent` ve `createElement` metotlarını kullanarak kötü niyetli Javascript kodlarının çalıştırılmasını engelledim.

---

## 🚀 5. Projeyi Nasıl Çalıştırabilirsiniz?

Hocam, projeyi sizin de kendi bilgisayarınızda kolayca deneyebilmeniz için tüm adımları Dockerize ettim.

### Adım 1: Docker Compose ile Her Şeyi Kaldırma
Bilgisayarınızda sadece Docker kurulu olması yeterlidir. Proje kök dizininde şu komutu çalıştırarak uygulamayı, PostgreSQL'i, LocalStack'i, Prometheus ve Grafana'yı tek seferde başlatabilirsiniz:
```bash
docker compose up -d
```

### Adım 2: Erişim Adresleri
* **Arayüz:** `http://localhost:8000` (FastAPI üzerinden statik arayüzü sunuyoruz, resmi buradan yükleyebilirsiniz)
* **Swagger API Belgeleri:** `http://localhost:8000/docs`
* **Prometheus Metrikleri:** `http://localhost:9090`
* **Grafana Panelleri:** `http://localhost:13000` (Giriş: `admin` / `admin` - İçeride resim sayısı ve gecikme süresini izleyen hazır grafikler mevcuttur)

### Adım 3: Testleri Çalıştırma
Eğer testleri kendi bilgisayarınızda yerel olarak koşturmak isterseniz:
```bash
# Sanal ortamı aktif etme ve bağımlılıkları yükleme
source venv/bin/activate
pip install -r requirements-dev.txt

# Testleri çalıştırma
PYTHONPATH=. venv/bin/pytest
```

### Adım 4: S3'teki Dosyaları Listeleme (AWS CLI ile Doğrulama)
Hocam, projemiz LocalStack kullandığı için yerel S3 kovanımızda (bucket) biriken resimleri doğrulamak için bilgisayarınıza hiçbir AWS programı kurmadan, resmi `aws-cli` Docker konteynerini kullanarak şu komutla S3'teki dosyaları listeleyebilirsiniz:
```bash
docker run --rm -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test -e AWS_DEFAULT_REGION=us-east-1 --network=host amazon/aws-cli --endpoint-url=http://localhost:4566 s3 ls s3://image-resize-bucket/resized/
```

---

## 📝 Özet ve Sonuç

Hocam, bu projede sadece çalışan bir kod yazmakla kalmadım; bulut ortamında çalışan bir uygulamanın **güvenilirliğini**, **hızını**, **güvenliğini** ve **izlenebilirliğini** test mühendisliği araçlarıyla (Pytest, Moto, Playwright, k6, Prometheus) garanti altına aldım. Proje, modern bir bulut mikroservisinin sahip olması gereken tüm standartları karşılamaktadır.

Değerlendirmenize ve takdirinize sunuyorum.
