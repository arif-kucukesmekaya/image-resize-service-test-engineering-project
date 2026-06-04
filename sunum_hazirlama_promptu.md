# 📋 Sunum Hazırlama Yapay Zeka Promptu (Copy-Paste)

Aşağıdaki metni (başlıktan son satıra kadar) kopyalayıp ChatGPT, Claude veya tercih ettiğiniz herhangi bir yapay zekaya yapıştırarak sunum slaytlarınızın içeriğini ve konuşma notlarınızı otomatik oluşturtabilirsiniz.

---

```text
Aşağıda teknik detayları ve kod yapısı verilen "Resim Boyutlandırma Mikroservisi (Image Resize Service)" projesi için üniversitede "Bulut Mimarilerinde Test Mühendisliği" dersi jürisinde sunulmak üzere detaylı bir slayt içeriği ve konuşma notu (presenter notes) planı hazırlar mısın?

Sunum süresi tam 20 dakikadır. Bu nedenle slaytlar teknik açıdan doyurucu, konuşma notları ise akademik ve akıcı olmalıdır.

Slayt şablonu her slayt için şu formatta olmalıdır:
- Slayt No ve Başlığı
- Slayt Görsel/Diyagram Tavsiyesi
- Slayt Üzerindeki Kısa Maddeler (Bullet Points)
- Sunucunun Söyleyeceği Konuşma Metni (Presenter Notes - Detaylı ve akıcı Türkçe)

---

### PROJE DETAYLARI:

1. PROJENİN AMACI:
- Kullanıcılardan gelen resimleri en-boy oranını (aspect ratio) koruyarak boyutlandırmak (Bounding Box prensibi).
- Resim dosyalarını bulutta (AWS S3) depolamak, metadata kayıtlarını veritabanında saklamak.
- Sistemin test edilebilirliğini, gözlemlenebilirliğini (observability) ve güvenliğini bulut standartlarında doğrulamak.

2. TEKNOLOJİK YIĞIN (TECH STACK):
- Backend: FastAPI, Uvicorn, Pillow (Resim işleme), Pydantic (Girdi doğrulama).
- Depolama & DB: AWS S3 (boto3 SDK), PostgreSQL, SQLite (in-memory testler için), SQLAlchemy ORM.
- Simülasyon: LocalStack (Yerel AWS S3 emülatörü), Moto (Pytest içi bellek içi AWS mocking).
- Test Otomasyonu: Pytest, Playwright (E2E browser testleri), k6 (Performans ve yük testi), pytest-cov (%80.55 kapsama oranı).
- DevOps: Docker (Multi-stage build), Docker Compose (5 servis: App, DB, LocalStack, Prometheus, Grafana), Kubernetes (Deployment, Service, ConfigMap manifestleri).
- İzleme: Prometheus ve hazır Grafana paneli (Request Rate, P95 Latency, Resize Rate).

3. UYGULANAN GÜVENLİK ÖNLEMLERİ (SECURE CODING):
- ASGI Middleware ile 10MB dosya boyutu sınırı (DDoS ve OOM koruması).
- Dosya isimlerinin rastgele UUID'lerle değiştirilmesi (S3 key injection ve Path Traversal koruması).
- Arayüzde innerHTML yerine textContent kullanımı (XSS koruması).

4. TEST STRATEJİSİ (TEST PIRAMIDI):
- Unit Testler: Pillow algoritmaları ve Pydantic veri sınırlarının testi.
- Integration Testler: Moto ile S3 mock'lama, SQLite :memory: veritabanı ile veritabanı işlemlerinin testi.
- E2E Testler: Playwright ile tarayıcıda resim yükleme, yenileme ve silme (dialog interception ile confirm kabulü) testi.
- Kapsama Oranı: %80.55 coverage. Miss (eksik) satırların çoğunluğunun exception handling (hata yakalama) blokları olmasının gerekçelendirilmesi.

---

Lütfen bu bilgiler ışığında 12 slaytlık eksiksiz bir sunum planı oluştur. Slaytlar sırasıyla şunlar olsun:
Slayt 1: Giriş ve Proje Başlığı
Slayt 2: Problemin Tanımı ve Resim Boyutlandırma İhtiyacı
Slayt 3: Sistem Mimarisi ve İş Akışı (Sequence Diagram anlatımı)
Slayt 4: Endüstri Standardı: Bounding Box (En-Boy Oranı Koruma) Mantığı
Slayt 5: Test Stratejisi ve Test Piramidi Yaklaşımı
Slayt 6: Birim (Unit) Testleri ve Girdi Doğrulama
Slayt 7: Entegrasyon Testleri (Moto ile AWS S3 Mocking)
Slayt 8: Playwright ile Uçtan Uca (E2E) Tarayıcı Testleri
Slayt 9: k6 ile Yük ve Performans Testi
Slayt 10: Gözlemlenebilirlik (Observability): Prometheus & Grafana
Slayt 11: Bulut Güvenliği ve Güvenli Kodlama (Secure Coding) Önlemleri
Slayt 12: DevOps, Konteynerizasyon ve Kubernetes Altyapısı
Slayt 13: Özet, Sonuç ve Soru-Cevap
```
