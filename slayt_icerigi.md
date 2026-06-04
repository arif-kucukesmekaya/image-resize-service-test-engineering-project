# 📊 Slayt İçerikleri ve Sunum Konuşma Notları

Bu dosya, sunum slaytlarınızda yer alacak kısa maddeleri, tasarım önerilerini ve sunum esnasında slayt slayt okuyabileceğiniz / anlatabileceğiniz detaylı **konuşma notlarını** içerir.

---

## 🖥️ Slayt 1: Giriş ve Proje Başlığı
* **Slayt Başlığı:** Bulut Mimarilerinde Test Mühendisliği: Resim Boyutlandırma Mikroservisi
* **Slayt Alt Başlığı:** Cloud-Native Image Resizing & Storage Infrastructure with Robust Test Automation
* **Görsel/Tasarım Önerisi:** Koyu mavi/mor tonlarında premium bir arka plan, projenin ana logosu veya şık bir teknoloji ikonu.
* **Slayt Maddeleri:**
  * FastAPI tabanlı asenkron mikroservis mimarisi
  * AWS S3 depolama ve SQLAlchemy ORM altyapısı
  * Test Piramidi (Unit, Integration, E2E) uyumluluğu
  * Sürekli Entegrasyon (CI/CD) ve Gözlemlenebilirlik (Observability)
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Hocam merhaba. Bugün sizlere 'Bulut Mimarilerinde Test Mühendisliği' dersi kapsamında geliştirdiğim 'Resim Boyutlandırma Mikroservisi' projesini sunacağım. Projemiz, modern bir bulut uygulamasının sahip olması gereken tüm asenkron çalışma standartlarına göre yazıldı. Bugün size uygulamanın sadece nasıl çalıştığını değil, bir test mühendisi gözüyle nasıl otomatik olarak doğrulandığını, yük testlerine nasıl tabi tutulduğunu ve bulut ortamında nasıl izlendiğini aşama aşama aktaracağım."*

---

## 🖥️ Slayt 2: Problemin Tanımı ve Resim Boyutlandırma İhtiyacı
* **Slayt Başlığı:** Ölçeklenebilir Sistemlerde Resim Depolama Sorunları
* **Görsel/Tasarım Önerisi:** Bozulmuş/uzamış bir resim görseli ile en-boy oranı korunmuş düzgün bir görselin yan yana karşılaştırması.
* **Slayt Maddeleri:**
  * Milyonlarca kullanıcının farklı boyutlarda görseller yüklemesi
  * Sunucu belleğinin (RAM) büyük dosyalarla şişmesi (OOM Tehlikesi)
  * Resimlerin esnetilerek görsel kalitesinin bozulması (Distortion)
  * Doğrudan erişime açık bulut depolama kovanlarının yarattığı güvenlik riskleri
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Bulut mimarilerinde resim yükleme ve işleme süreçleri en büyük darboğazlardan biridir. Farklı ekran boyutları için resimleri boyutlandırmak zorundayız. Ancak bu işlemi yaparken üç temel sorunla karşılaşıyoruz: Birincisi, büyük dosyaların sunucu belleğini tüketmesi. İkincisi, resimlerin en-boy oranları bozulduğunda ürün görsellerinin yamulması. Üçüncüsü ise dosyaların bulutta güvensiz saklanması. Bu projeyle tüm bu problemleri standartlara uygun şekilde çözmeyi hedefledik."*

---

## 🖥️ Slayt 3: Sistem Mimarisi ve İş Akışı
* **Slayt Başlığı:** Sistem Mimarisi ve İstek Akışı (Sequence Diagram)
* **Görsel/Tasarım Önerisi:** Proje mimarisinin akış diyagramı (README.md'deki Mermaid şeması).
* **Slayt Maddeleri:**
  * **İstemci:** Resim ve hedef boyutları POST isteğiyle gönderir.
  * **FastAPI:** İstek şemalarını doğrular, Pillow motorunu çağırır.
  * **Pillow:** Resmi en-boy oranını bozmadan bellekte boyutlandırır.
  * **LocalStack S3:** Resim dosyasını bulut kovanına güvenli UUID ile kaydeder.
  * **PostgreSQL / SQLAlchemy:** Metadata kaydını yazar ve istemciye geçici Presigned URL döner.
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Hocam, sistemimizin mimari akışı bu diyagramda görünüyor. İstemciden gelen istek öncelikle FastAPI middleware katmanında doğrulanıyor. Ardından Pillow kütüphanesi resmi bellekte işliyor. İşlenen resim, yerelde AWS S3 API'sini simüle eden LocalStack servisine yükleniyor. Veritabanına dosya yolu yazıldıktan sonra kullanıcıya doğrudan dosya linki yerine süreli bir Presigned URL veriliyor. Bu sayede verilerimiz S3 içerisinde tamamen gizli ve güvenli kalıyor."*

---

## 🖥️ Slayt 4: Endüstri Standardı: Bounding Box (En-Boy Oranı Koruma) Mantığı
* **Slayt Başlığı:** Bounding Box Nedir? Görsel Bütünlüğün Korunması
* **Görsel/Tasarım Önerisi:** 200x300 piksel boyutlarında bir kutu içerisine yerleşen dikey bir telefon fotoğrafı ile yatay bir televizyon fotoğrafının şematik gösterimi.
* **Slayt Maddeleri:**
  * Genişlik ve Yükseklik değerlerinin maksimum sınır (çerçeve) olarak kabul edilmesi
  * Pillow `thumbnail` algoritması ile otomatik oran hesaplama
  * Resimlerin asla esnetilmemesi (Yamulma koruması)
  * *Örnek:* 1600x900 (16:9) resmi 200x300 kutuya sığdırıldığında 200x112 piksele düşürülür.
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Kullanıcı arayüzünde hem genişlik hem yükseklik seçtiriyoruz ancak resim her zaman kare olmuyor. Bunun nedeni 'Bounding Box' yani sınır kutusu prensibidir. Girdiğimiz ölçüler resmin sığacağı maksimum çerçeveyi belirler. Pillow'un `thumbnail` fonksiyonu, resmin en-boy oranını bozmadan bu kutunun içine sığabilecek en büyük boyutları hesaplar. Böylece görsellerimiz hiçbir zaman esneyerek kalitesini kaybetmez."*

---

## 🖥️ Slayt 5: Test Stratejisi ve Test Piramidi Yaklaşımı
* **Slayt Başlığı:** Test Piramidi (Test Pyramid) ve Kalite Güvencesi
* **Görsel/Tasarım Önerisi:** En altta Unit, ortada Integration, en üstte E2E testlerin olduğu klasik piramit şeması.
* **Slayt Maddeleri:**
  * **Unit Tests (%60):** En hızlı, izole ve yoğun katman (Algoritmalar ve şemalar).
  * **Integration Tests (%30):** API, DB ve S3 servislerinin uyum testi.
  * **E2E Tests (%10):** Playwright ile gerçek tarayıcıda kullanıcı senaryoları.
  * **Kod Kapsama Oranı (Coverage):** Toplamda **%80.55** başarılı test kapsamı.
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Test mühendisliği dersimizin temeli olan Test Piramidi yapısını projemizde tam anlamıyla hayata geçirdik. Hızlı ve izole çalışan birim testlerden başladık, servislerin haberleşmesini test eden entegrasyon testleriyle devam ettik ve en tepeye Playwright ile arayüz testlerimizi koyduk. Toplamda %80.55'lik kod kapsamına ulaştık. Bu oran kritik iş mantığımızın tamamının otomatik testler güvencesinde olduğunu kanıtlıyor."*

---

## 🖥️ Slayt 6: Birim (Unit) Testleri ve Girdi Doğrulama
* **Slayt Başlığı:** Birim Testler ve Pydantic Şema Güvenliği
* **Görsel/Tasarım Önerisi:** `test_resize.py` ve `test_schemas.py` dosyalarından kod kesitleri.
* **Slayt Maddeleri:**
  * Pillow boyutlandırma mantığının ve kalitesinin doğrulanması
  * Geçersiz resim byte'ları gönderildiğinde fırlatılan hataların testi
  * Pydantic ile negatif değerlerin veya 5000px üzeri aşırı girdilerin engellenmesi
  * Dış servislere (S3, DB) bağımlı olmadan milisaniyeler içinde çalışma
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Birim testlerimizde kodumuzun dış dünyayla olan bağlantısını tamamen keserek saf fonksiyonel mantığı test ettik. Pillow'un resimleri doğru sıkıştırıp sıkıştırmadığını ve en-boy oranını doğru hesapladığını doğruladık. Pydantic şema testlerimizde ise API'ye gelebilecek hatalı boyut veya formattaki isteklerin daha sunucuya yük getirmeden kapıda nasıl engellendiğini test ettik."*

---

## 🖥️ Slayt 7: Entegrasyon Testleri (Moto ile AWS S3 Mocking)
* **Slayt Başlığı:** Mocking Stratejisi: Moto & In-Memory SQLite
* **Görsel/Tasarım Önerisi:** Sol tarafta buluttaki AWS simgesi, sağ tarafta ise bilgisayar belleğindeki (RAM) Moto simgesi.
* **Slayt Maddeleri:**
  * **Moto (`mock_aws`):** AWS S3 API çağrılarını RAM'de simüle eder.
  * Gerçek AWS hesabı ve internet bağlantısı gereksinimini ortadan kaldırma
  * SQLite `StaticPool` ile bellek içi (in-memory) izole test veritabanı
  * API endpoints (`TestClient`) üzerinden uçtan uca entegrasyon doğrulaması
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Bulut mimarilerini test ederken en büyük zorluk dış servis bağımlılıklarıdır. Her test çalıştığında gerçek AWS S3'e dosya yüklemek hem yavaştır hem de maliyetlidir. Biz bu problemi çözmek için **Moto** kütüphanesini kullandık. Moto, AWS servislerini bilgisayarın belleğinde taklit eder. Veritabanı için de in-memory SQLite kullanarak testlerin tamamen izole, hızlı ve ücretsiz çalışmasını sağladık."*

---

## 🖥️ Slayt 8: Playwright ile Uçtan Uca (E2E) Tarayıcı Testleri
* **Slayt Başlığı:** Playwright ile Gerçek Tarayıcı Otomasyonu
* **Görsel/Tasarım Önerisi:** Otomatik test koşan Playwright tarayıcı penceresinin ekran görüntüsü.
* **Slayt Maddeleri:**
  * Gerçek Chromium tarayıcısı üzerinde otomatik senaryo koşumu
  * Resim yükleme, parametre girme ve boyutlandırma butonuna tıklama simülasyonu
  * Tarayıcı onay kutularının (Delete confirm dialog) otomatik yakalanıp onaylanması
  * Test başlangıcında `dev.db` temizliği ile tam test izolasyonu
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Entegrasyon testlerinin bittiği yerde, uygulamanın tarayıcıda kullanıcıya nasıl göründüğünü doğrulamak için **Playwright** kullandık. Playwright arka planda gerçek bir tarayıcı açarak butona tıklama, form doldurma gibi adımları taklit ediyor. Ayrıca silme işlemi sırasındaki tarayıcı uyarı kutularını (confirm dialog) otomatik yakalayarak kabul ediyor ve resmin arayüzden silindiğini doğruluyor."*

---

## 🖥️ Slayt 9: k6 ile Yük ve Performans Testi
* **Slayt Başlığı:** Performans Mühendisliği: k6 Stress Testi
* **Görsel/Tasarım Önerisi:** k6 testinin terminal çıktısı (saniyedeki istek sayısı ve gecikme grafikleri).
* **Slayt Maddeleri:**
  * **k6 (Grafana Labs):** Go tabanlı, Javascript senaryolu yük testi aracı
  * 50 Sanal Kullanıcı (VUs) ile 30 saniye boyunca eşzamanlı istekler
  * Performans Barajları (Thresholds): p95 gecikme < 2000ms, hata oranı < %5
  * Sistem limitlerinin yük altında zorlanması ve metriklerin Prometheus'a yazılması
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Sistemimizin yük altındaki gücünü ölçmek için **k6** kullandık. Yazdığımız Javascript senaryosu ile sisteme aynı anda 50 sanal kullanıcı ile yüklendik ve saniyeler içinde 1500 resim boyutlandırma isteği gerçekleştirdik. k6 bize isteklerin %95'inin ne kadar sürede tamamlandığını ve hata oranlarını anlık raporladı. Bu sayede uygulamanın yoğun trafikteki performans sınırlarını doğrulamış olduk."*

---

## 🖥️ Slayt 10: Gözlemlenebilirlik (Observability): Prometheus & Grafana
* **Slayt Başlığı:** Canlı Sistem İzleme ve Dashboard Altyapısı
* **Görsel/Tasarım Önerisi:** Grafana dashboard ekran görüntüsü (mümkünse 13000 portundan aldığınız canlı arayüz).
* **Slayt Maddeleri:**
  * `/metrics` endpoint'i üzerinden Prometheus veri toplama akışı
  * Grafana ile otomatik yapılandırılmış veri kaynağı (Prometheus) ve dashboard
  * **Grafikler:** HTTP Request Rate, Response Latency (p95), S3 Resize Operations
  * Sorun anında (Darboğaz veya yüksek hata oranı) hızlı tespit ve alarm altyapısı
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Sistemimizin canlıdaki sağlık durumunu izlemek için Prometheus ve Grafana ikilisini kullandık. FastAPI uygulamamız özel metrikler üretiyor, Prometheus bunları düzenli olarak çekiyor, Grafana ise bu ham verileri görselleştiriyor. Docker Compose ayağa kalktığında bu paneller otomatik olarak yükleniyor. Böylece sistemde bir darboğaz veya hata artışı olduğunda bunu anında tespit edebiliyoruz."*

---

## 🖥️ Slayt 11: Bulut Güvenliği ve Güvenli Kodlama (Secure Coding) Önlemleri
* **Slayt Başlığı:** Güvenli Bulut Mimarisi Tasarımı
* **Görsel/Tasarım Önerisi:** Kilit simgesi, UUID dönüşüm şeması ve kod bloklarındaki güvenlik kontrolleri.
* **Slayt Maddeleri:**
  * **DDoS Koruması:** ASGI middleware katmanında 10MB boyut kontrolü
  * **Path Traversal Engelleyici:** Kullanıcı dosya adlarının rastgele UUID'lere dönüştürülmesi
  * **XSS Koruması:** Ön yüzde `innerHTML` yerine güvenli DOM metotları (`textContent`)
  * **Veri Gizliliği:** S3 kovasının dış dünyaya kapalı tutulması ve Presigned URL kullanımı
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Bulut uygulamalarında güvenlik öncelikli olmalıdır. DDoS saldırılarına karşı sunucu belleğini korumak adına 10MB sınırı koyduk. Dosya isimlerini rastgele UUID'ler haline getirerek path traversal (dizin aşımı) açıklarını engelledik. Ön yüzde ise Cross-Site Scripting yani XSS saldırılarını önlemek için asla innerHTML kullanmadık, sadece güvenli DOM elemanları kullandık. S3 kovamızı da dışarıya tamamen kapalı tutarak gizliliği koruduk."*

---

## 🖥️ Slayt 12: DevOps, Konteynerizasyon ve Kubernetes Altyapısı
* **Slayt Başlığı:** DevOps ve Kubernetes (K8s) ile Canlıya Geçiş
* **Görsel/Tasarım Önerisi:** Docker Compose ve Kubernetes logoları, podların dağıtım şeması.
* **Slayt Maddeleri:**
  * **Dockerfile:** İki aşamalı (multi-stage) güvenli ve hafif üretim imajı
  * **Docker Compose:** 5 servisli lokal geliştirme ve izleme ortamı
  * **Kubernetes (Minikube):** Deployment, Service ve ConfigMap tanımları
  * CPU/RAM kaynak sınırlandırmaları (Resource Limits) ve Health Probe kontrolleri
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Son olarak projenin DevOps altyapısını kurduk. İki aşamalı Dockerfile ile gereksiz bağımlılıklardan arındırılmış, hafif ve güvenli bir imaj oluşturduk. Lokal geliştirme için Docker Compose kullandık. Canlı ortama geçiş için ise Kubernetes manifestlerimizi hazırladık. Kubernetes deployment dosyasında podlarımızın CPU ve bellek limitlerini belirledik ve `/health` endpoint'i üzerinden liveness/readiness probe'larını kurguladık."*

---

## 🖥️ Slayt 13: Özet, Sonuç ve Soru-Cevap
* **Slayt Başlığı:** Teşekkürler & Soru-Cevap
* **Görsel/Tasarım Önerisi:** Soru işareti simgesi ve iletişim bilgileriniz.
* **Slayt Maddeleri:**
  * Bulut standartlarında test edilebilir ve güvenli mikroservis
  * %80.55 başarılı kod kapsama oranı
  * Canlı trafik, izleme ve performans analizleri hazır altyapı
  * Sorularınız için hazırım.
* **🗣️ Konuşma Notu (Presenter Notes):**
  > *"Hocam, özetlemek gerekirse; bu projede sadece çalışan bir resim boyutlandırma servisi yazmadık. Yazılımın bulut ortamındaki güvenilirliğini, test otomasyon standartlarını, yük altındaki performansını ve izlenebilirliğini test mühendisliği metotlarıyla garanti altına aldık. Dinlediğiniz için çok teşekkür ederim, sorularınız varsa yanıtlamaktan memnuniyet duyarım."*
