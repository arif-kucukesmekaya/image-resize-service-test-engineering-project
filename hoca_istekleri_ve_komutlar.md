# 🎓 Sunum Sırasında Hocanın İsteyebileceği Gösterimler ve Komutları

Bu kılavuz, sunum esnasında hocanızın **"bana şunu göster"**, **"şu testi çalıştır"** veya **"metriği göster"** diyebileceği tüm olası durumlar için kullanacağınız hazır terminal komutlarını içerir.

---

## 🧪 1. "Testleri Çalıştır" İstekleri

### A. "Tüm testleri çalıştır ve test kapsamını (coverage) göster"
Tüm unit, integration ve E2E testleri çalıştırır ve kapsama oranının %80.97 olduğunu gösterir.
```bash
PYTHONPATH=. venv/bin/pytest
```

### B. "Sadece Playwright (E2E) testlerini çalıştır"
Arka planda (headless) tarayıcıyı açarak sadece arayüz testlerini koşturur.
*Not: Tek bir test dosyası çalıştırırken kapsama oranı (coverage) %70 barajının altında kalacağı için hata vermesini engellemek adına `--no-cov` bayrağını ekliyoruz.*
```bash
PYTHONPATH=. venv/bin/pytest tests/e2e/test_playwright.py --no-cov
```

### C. "Sadece Birim (Unit) testlerini çalıştır"
Hızlı çalışan Pillow ve veri doğrulama testlerini koşturur.
```bash
PYTHONPATH=. venv/bin/pytest tests/unit/ --no-cov
```

### D. "Sadece Entegrasyon (Integration) testlerini çalıştır"
Veritabanı ve S3 (Moto ile taklit edilen) entegrasyon testlerini koşturur.
```bash
PYTHONPATH=. venv/bin/pytest tests/integration/ --no-cov
```

### E. "Playwright testlerini tarayıcıyı açarak canlı göster"
*Not: Bu komutun çalışması için bilgisayarınızdaki WSL (WSLg) ekran yönlendirmesinin aktif olması gerekir. Adımları takip edebilmek için her tıklama arasına 1.5 saniye gecikme koyduk (`--slowmo 1500`).*
```bash
PYTHONPATH=. venv/bin/pytest tests/e2e/test_playwright.py --headed --slowmo 1500 --no-cov
```

---

## 📈 2. "Kod Kapsama (Coverage) Raporunu Ayrıntılı Göster"
Hoca *"Hangi satırlar test edilmiş, hangileri edilmemiş detaylı rapor görebilir miyiz?"* derse:
1. Terminalde şu komutla HTML raporu üretin:
   ```bash
   PYTHONPATH=. venv/bin/pytest --cov=app --cov-report=html
   ```
2. Proje klasörünüzde oluşan **`htmlcov/index.html`** dosyasını çift tıklayarak tarayıcınızda açın. Karşınıza satır satır test edilen kodları gösteren renkli, harika bir arayüz çıkacaktır.

---

## ☁️ 3. "AWS S3 / LocalStack Durumunu Göster"

### A. "S3 kovanında (bucket) biriken resimleri listele"
LocalStack üzerindeki yapay S3 sunucusuna bağlanıp yüklenen tüm boyutlandırılmış dosyaları listeler.
```bash
docker run --rm -e AWS_ACCESS_KEY_ID=test -e AWS_SECRET_ACCESS_KEY=test -e AWS_DEFAULT_REGION=us-east-1 --network=host amazon/aws-cli --endpoint-url=http://localhost:4566 s3 ls s3://image-resize-bucket/resized/
```

---

## ⚡ 4. "Yük Testi ve Performans Testini Çalıştır"

### A. "k6 ile sisteme yük bindir"
Aynı anda 50 sanal kullanıcı ile sisteme saniyeler içinde 1500 adet istek gönderir. (Bu test çalışırken Grafana ekranındaki grafiklerin yükselişini gösterin).
```bash
docker run --rm -v $(pwd):/app -w /app --network=host grafana/k6 run performance/k6_script.js
```

---

## 🐋 5. "Konteynerlerin ve Servislerin Durumunu Göster"

### A. "Docker'da hangi servisler ayakta?"
Postgres, LocalStack, App, Prometheus ve Grafana'nın çalışır durumda olduğunu doğrular.
```bash
docker compose ps
```
