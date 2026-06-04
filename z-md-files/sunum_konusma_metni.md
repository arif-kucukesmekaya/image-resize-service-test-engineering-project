# Sunum Konuşma Metni (Arif'in Ağzından ve "Hocam" Hitabıyla)

Bu dosya, sunum esnasında slaytları geçerken Büşra Hocanıza hitaben yapacağınız samimi, saygılı ve teknik açıdan dolu dolu olan konuşma metnidir. Ders kapsamında öğrendiğiniz kavramlara atıfta bulunarak tasarlanmıştır.

---

### 🎙️ SLAYT 1: Giriş ve Kapak Slaytı
**Süre:** ~1 Dakika

*(Büşra Hocanıza bakarak tebessümle başlayın)*

"Büşra Hocam merhabalar, sunumuma hoş geldiniz.

Ben Arif Küçükeşmekaya. Bugün size, bu dönem sizden aldığım 'Bulut Bilişim Mimarilerinde Test Mühendisliği' dersi kapsamında hazırladığım dönem projemi sunacağım. 

Projemde, bulut mimarilerinde ölçeklenebilir ve dayanıklı bir **'Resim Boyutlandırma Mikroservisi'** geliştirdim. Sunumum boyunca uygulamanın kod yapısından ziyade, sizin de derste üzerinde çokça durduğunuz **test mühendisliği pratiklerini** bu projeye nasıl uyguladığımı anlatacağım. Birim testlerinden Playwright uçtan uca testlerine, k6 yük testlerinden Prometheus/Grafana gözlemlenebilirlik altyapısına kadar kurduğum test ve doğrulama mimarisini detaylandıracağım.

Dilerseniz projemizin çıkış noktası ve hedefleriyle başlayalım."

---

### 🎙️ SLAYT 2: Problem Tanımı ve Proje Hedefleri
**Süre:** ~1.5 Dakika

*(Slayt geçişi yapın)*

"Hocam, bildiğiniz gibi bulut mimarilerinde resim boyutlandırma gibi işlemler CPU ve bellek tarafında ciddi yük oluşturan operasyonlar. Geleneksel sistemlerde bunları test etmek kolay olsa da, iş cloud-native mikroservislere geldiğinde karşımıza bazı zorluklar çıkıyor:

İlk olarak, uygulamanın dış dünyayla olan bağımlılıkları (S3 nesne depolama, veritabanları gibi) test süreçlerini hem maliyetli hale getiriyor hem de internete bağımlı kılıyor. İkincisi, yüksek trafik altında API'nin nasıl tepki vereceğini lokalde görmemiz zor oluyor. Son olarak da canlıdaki sistemin sağlık durumunu anlık izleyemiyoruz.

Ben bu projede şu hedefleri önüme koydum:
* **Sıfır Maliyetle Test:** S3 gibi dış servisleri lokalde simüle edip hiçbir bulut maliyeti ödemeden entegrasyon testlerini koşturmak.
* **Tam Otomatik Test Piramidi:** Birim, entegrasyon ve uçtan uca test otomasyonunu kurmak.
* **Otomatik CI/CD Hattı:** Yazdığım kodda insan hatasını engellemek için her push işleminde testleri bulutta otomatik tetiklemek.
* **Canlı İzleme:** Performansı ve metrikleri Prometheus/Grafana ikilisiyle anlık grafiklerde görmek."

---

### 🎙️ SLAYT 3: Sistem Mimarisi (Architecture)
**Süre:** ~2 Dakika

*(Slayt geçişi yapın)*

"Hocam, uygulamanın mimarisini tamamen asenkron ve modern standartlarda kurguladım.

Backend tarafında asenkron çalışan, çok hızlı ve otomatik Swagger belgesi üreten **FastAPI** kullandım. Resim işleme işlerini ise **Pillow** kütüphanesiyle çözdüm.

Süreç şöyle işliyor:
Kullanıcı resmi ve istediği boyutları API'ye gönderiyor. API isteği alıp asenkron olarak resmi boyutlandırıyor. Boyutlanan resmi doğrudan **AWS S3** nesne depolama alanına yüklüyoruz. Hocam, geliştirme ve test aşamalarında maliyet yaratmaması için lokalde AWS S3'ün birebir simülasyonu olan **LocalStack** container'ını kullandım.

Yükleme bittikten sonra resme ait metadatayı (orijinal ve yeni boyutlar, dosya yolu ve işlem süresi gibi bilgileri) **PostgreSQL** veritabanına kaydediyoruz. Kullanıcıya ise güvenlik sebebiyle belirli bir süre geçerli olan indirme bağlantısı (Presigned URL) dönüyoruz.

Sistemin tamamını Docker Compose ile paketledim ve Kubernetes ortamında ölçeklenebilmesi için k8s manifestolarını da hazır hale getirdim."

---

### 🎙️ SLAYT 4: Test Stratejisi ve Test Piramidi
**Süre:** ~2 Dakika

*(Slayt geçişi yapın)*

"Hocam, projenin en çok önem verdiğim ve dersteki kazanımları yansıttığım kısmı burası. Tam anlamıyla katmanlı bir 'Test Piramidi' yapısı kurdum:

En altta **Birim (Unit) Testlerimiz** var. Burada API şemalarını ve resim boyutlandırma algoritmalarını test ettim. Bozuk resim verisi gönderilmesi veya sıfır genişlik girilmesi gibi sınır değerleri (boundary conditions) burada yakalıyoruz.

Orta katmanda **Entegrasyon (Integration) Testlerimiz** var. Mock kullanmak yerine gerçek PostgreSQL ve LocalStack S3 servislerini test ortamında ayağa kaldırarak veritabanı yazma/silme ve S3 dosya yükleme işlemlerini canlı test ettim.

En üstte ise **Uçtan Uca (E2E) Testlerimiz** yer alıyor. Burada **Playwright** otomasyon kütüphanesini kullandım. Test kodu tarayıcıyı açıyor, bir resim seçip yüklüyor, boyutlandırılmış halini indiriyor, DB'den metadatasını doğruluyor ve son olarak temiz bir ortam bırakmak için resmi siliyor.

Tüm bu testlerin sonucunda kod tabanımızın satır bazlı test kapsama oranı (coverage) **%76** olarak gerçekleşti. Böylece derste istediğiniz %70 barajını başarıyla geçmiş olduk."

---

### 🎙️ SLAYT 5: Performans ve Yük Testleri (k6)
**Süre:** ~1.5 Dakika

*(Slayt geçişi yapın)*

"Uygulamanın yüksek trafik altında nasıl davranacağını ölçmek için **Grafana k6** ile yük testleri koşturdum.

30 saniye boyunca sisteme sürekli artan yoğunlukta resim boyutlandırma istekleri göndererek sınırları zorladım. Bu testte özellikle şu üç metriği takip ettim:
1. **Request Rate (RPS):** Saniyede işlenen ortalama istek sayısı.
2. **Latency (Gecikme Süresi):** İsteklerin yanıtlanma sürelerini P95 ve P99 seviyesinde izledim. Böylece kullanıcıların %95'inin nasıl bir hız deneyimlediğini gördüm.
3. **Error Rate (Hata Oranı):** Yüksek yükte sunucunun hata verip vermediği.

FastAPI'nin asenkron yapısı sayesinde, yük altında dahi **%0 hata oranı** ile sistemi stabil tutmayı başardık ve gecikme sürelerini makul seviyelerde koruduk."

---

### 🎙️ SLAYT 6: Gözlemlenebilirlik (Observability)
**Süre:** ~1.5 Dakika

*(Slayt geçişi yapın)*

"Hocam, sistemin canlı durumunu izleyebilmek için **Prometheus** ve **Grafana** entegrasyonu yaptım.

Uygulamanın içine yerleştirdiğim özel sayaçlar sayesinde:
* `image_resize_requests_total` metriğiyle hangi formata (JPEG, PNG, WEBP) kaç istek geldiğini ve başarı durumlarını,
* `image_resize_duration_seconds` metriğiyle de boyutlandırma işlemlerinin kaç saniye sürdüğünü anlık olarak dışarıya Prometheus formatında sunuyoruz.

Prometheus bu verileri toplarken, Grafana da bunları görselleştiriyor. Burada kurulumu kolaylaştırmak için otomatik dashboard yükleme (auto-provisioning) özelliğini kullandım. Docker Compose çalıştığı anda Grafana'da **Image Resize Service Dashboard**'u hiçbir manuel ayara gerek kalmadan otomatik olarak hazır hale geliyor."

---

### 🎙️ SLAYT 7: Sürekli Entegrasyon (CI/CD Pipeline)
**Süre:** ~1.5 Dakika

*(Slayt geçişi yapın)*

"Hocam, projede her kod değişikliğinin güvenli olduğundan emin olmak için **GitHub Actions** üzerinde 5 aşamalı bir CI/CD hattı tasarladım:

1. **Lint (Ruff):** Kod stilini ve statik analiz kontrollerini yaparak kullanılmayan değişkenleri veya biçimlendirme hatalarını yakalıyor.
2. **Test (Pytest + LocalStack):** Github runner üzerinde geçici bir LocalStack container'ı başlatarak testleri koşuyor. Test kapsamı %70'in altındaysa derlemeyi durduruyor.
3. **Docker Build:** Uygulamanın Docker imajının sorunsuz derlendiğini doğruluyor.
4. **Newman API Testleri:** Docker Compose ile tüm servisleri ayağa kaldırıp, Postman API koleksiyonundaki testleri Newman aracıyla canlı container'lara karşı test ediyor.
5. **Smoke Test:** API'nin `/health` endpoint'ine curl atarak uygulamanın başarıyla ayağa kalktığını teyit ediyor.

Böylece hatalı veya testi geçmeyen hiçbir kod `main` branch'imize karışamıyor."

---

### 🎙️ SLAYT 8: Özet ve Canlı Demo Geçişi
**Süre:** ~1 Dakika

*(Slayt geçişi yapın)*

"Özetlemem gerekirse hocam; bu projede sadece çalışan bir kod yazmakla kalmadım; derste öğrendiğimiz test edilebilirlik, ölçeklenebilirlik, gözlemlenebilirlik ve sürekli entegrasyon prensiplerini bütünüyle hayata geçirdim.

Projenin tüm teknik detaylarını, k6 grafiklerini ve mimari şemasını içeren 6 sayfalık detaylı bir sunum raporunu da PDF formatında hazırladım.

Şimdi izninizle, tüm bu anlattıklarımı aşama aşama göstereceğim **7 Dakikalık Canlı Demo** kısmına geçmek istiyorum. 

Önce Docker ortamımızı inceleyecek, ardından lokal testlerimizi (Pytest ve Playwright E2E) çalıştıracak, k6 ile yük testi başlatıp Grafana grafiğindeki canlı yükselişi görecek ve son olarak GitHub üzerinde bir PR açarak CI/CD pipeline'ımızın otomatik çalışmasını izleyeceğiz.

Dinlediğiniz için çok teşekkür ederim hocam. Dilerseniz demoya geçebilirim."
