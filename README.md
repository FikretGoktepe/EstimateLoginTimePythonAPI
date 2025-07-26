🧠 Kullanıcı Oturum Tahmin Sistemi Python

Kullanıcıların geçmiş oturum (login) verilerini analiz ederek, bir sonraki muhtemel giriş zamanını tahmin eden Python tabanlı bir tahmin ve analiz sistemi.

🚀 Özellikler

- 📈 Giriş zamanlarına dayalı tahminleme (Prophet + Neural Prophet)
- 🗂️ JSON tabanlı veri saklama ve önbellekleme sistemi
- 🔁 15 dakikada bir otomatik veri güncelleme sistemi
- 🌐 Flask API üzerinden erişim desteği

📊 Kullanılan Algoritmalar ve Yöntemler

📌 Prophet Tabanlı Zaman Serisi Modeli
- Facebook Prophet kullanılarak zaman serisi modeli oluşturulur.
- Giriş zamanları gün bazında gruplanarak modellenir.
- Prophet, trend, mevsimsellik ve tatil etkilerini dikkate alarak bir sonraki günü tahmin eder.

🧠 Neural Prophet
- Giriş sayıları, kayan pencere (window) ile gruplanır ve model örnekleri oluşturulur.
- `MLPRegressor` (Multi-Layer Perceptron) kullanılarak sonraki gün tahmini yapılır.
- Küçük veri setleri için uygun değildir; en az 6 veri gerektirir.

🔁 Otomatik Cache Güncelleme
- Sistem, her 15 dakikada bir API'den kullanıcı verilerini çeker.
- Prophet ve Neural Prophet tahminlerini hesaplayarak `cache.json` dosyasına yazar.
- Yazım işlemi güvenli şekilde `.tmp` dosyasına yapılır ve ardından atomik olarak `cache.json` ile değiştirilir.
