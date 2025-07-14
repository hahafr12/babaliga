import requests
import threading
import time

# Hedef: kendi test sunucun olabilir (örnek: http://localhost:5000)
url = "https://www.instagram.com/efe_____mfjr/"

# Gönderilecek istek sayısı (simülasyon)
request_count = 100
thread_count = 10

def send_requests():
    for _ in range(request_count // thread_count):
        try:
            response = requests.get(url)
            print(f"Status Code: {response.status_code}")
        except Exception as e:
            print(f"Hata: {e}")

# Thread'leri başlat
threads = []

start_time = time.time()

for i in range(thread_count):
    t = threading.Thread(target=send_requests)
    threads.append(t)
    t.start()

# Tüm thread'lerin bitmesini bekle
for t in threads:
    t.join()

end_time = time.time()
print(f"Toplam süre: {end_time - start_time:.2f} saniye")
