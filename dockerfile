# Temel Python imajı
FROM python:3.11-slim

# Çalışma dizini oluştur
WORKDIR /app

# Gereksinim dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Tüm dosyaları konteynıra kopyala
COPY . .

# Uygulama portunu dışa aç
EXPOSE 5000

# Uygulamayı başlat
CMD ["python", "app.py"]