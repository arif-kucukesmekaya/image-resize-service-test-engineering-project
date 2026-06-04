
### ⏱️ 1. Dakika: Yeni Dal (Branch) Açma ve Değişiklik Yapma
Hocanın gözü önünde yeni bir özellik dalı açıp ufak bir kod değişikliği yapacağız:
1. Terminalde yeni bir branch açın:
   ```bash
   git checkout -b feat/image-comment
   ```
2. `app/main.py` dosyasını açıp en üst satırlara zararsız bir yorum satırı ekleyin (Örn: `# Arif Kucukesmekaya - 2026`).
3. Değişikliği commitleyip GitHub'a push edin:
   ```bash
   git add app/main.py
   git commit -m "docs: add developer comment to main.py"
   git push -u origin feat/image-comment
   ```

---

### ⏱️ 2. Dakika: Pull Request (PR) Açma ve CI Tetikleme
1. GitHub tarayıcı sayfanızı açın. Ekranda sarı kutuda **"Compare & pull request"** butonu çıkacaktır. Ona tıklayın.
2. **"Create pull request"** butonuna basarak PR'ı açın.
3. **Burada hocaya gösterin:** PR açıldığı an sayfanın altında GitHub Actions'ın (CI) **otomatik olarak tetiklendiğini** göreceksiniz. 
4. *"Hocam, yazdığımız `.github/workflows/ci.yml` dosyası sayesinde açılan her PR'da kod kalitesi kontrolleri ve Pytest testlerimiz bulutta otomatik koşmaya başlıyor."* deyin.

---

### ⏱️ 3. Dakika: Lokal Dağıtım (Deploy) Gösterimi
CI arkada çalışmaya devam ederken yerel dağıtımı göstereceğiz:
1. Terminalde Docker Compose durumunu gösterin:
   ```bash
   docker compose ps
   ```
2. Servislerin (FastAPI, Postgres, LocalStack, Prometheus, Grafana) ayakta ve çalışır olduğunu gösterin.
3. Tarayıcıda `http://localhost:8000` adresine girip çalışan arayüzü hocaya gösterin. Bir adet test resmi yükleyip boyutlandırın.

---

### ⏱️ 4. Dakika: Yük Testi (k6) ile Trafik Oluşturma
Metrik panellerinde canlı yükselişi göstermek için arkada yük testini başlatacağız:
1. Terminalde k6 stres testini başlatın:
   ```bash
   docker run --rm -v $(pwd):/app -w /app --network=host grafana/k6 run performance/k6_script.js
   ```
2. Test arkada 30 saniye boyunca saniyede onlarca istek göndererek sistemi zorlamaya başlasın.

---

### ⏱️ 5. Dakika: Canlı Metrik İzleme (Prometheus & Grafana)
1. k6 testi çalışırken hemen tarayıcıda Grafana ekranını açın: **`http://localhost:13000`** (Giriş: `admin` / `admin`).
2. **Image Resize Service Dashboard**'unu gösterin. 
3. **Burada hocaya gösterin:** **Request Rate** ve **P95 Latency** grafiklerinin aniden nasıl tavan yaptığını (dalgalandığını) canlı olarak izletin.
4. Prometheus ekranına (`http://localhost:9090`) gidip **Status -> Targets** menüsünden API sunucumuzun yeşil renkli **`UP`** durumunda olduğunu gösterin.

---

### ⏱️ 6. Dakika: Uçtan Uca (E2E) Test Çalıştırma
Arayüz fonksiyonlarımızın kararlılığını kanıtlamak için Playwright testlerini koşturacağız:
1. Terminale geçin ve şu komutla E2E testlerini başlatın:
   ```bash
   PYTHONPATH=. venv/bin/pytest tests/e2e/test_playwright.py --no-cov
   ```
2. Testlerin başarıyla geçtiğini (`3 passed`) hocaya gösterin.

---

### ⏱️ 7. Dakika: PR Onaylama ve Kapanış
1. GitHub sayfasına geri dönün. Bu sırada CI testlerinizin de başarıyla tamamlandığını (yeşil tik aldığını) göreceksiniz.
2. **"Merge pull request"** butonuna basarak PR'ı onaylayın ve değişiklikleri `main` branch'ine başarıyla deploy etmiş olun.
3. Sunumu tamamlayıp soruları bekleyin.
