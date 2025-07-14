from flask import Flask, request, redirect, url_for, session
from pyngrok import ngrok
import socket

app = Flask(__name__)
app.secret_key = 'gizli-key'  # oturum yönetimi için gerekli

# 🔐 Ngrok Token – sadece ilk kez çalıştırırken ekle
ngrok.set_auth_token("2zseOKy2PBk4LrWL6Drwhp9bEqH_5i17LHpUirnoDZ9qh1ZrS")  # örn: 2JxkExxx...

# 🌐 Flask'ı dışa açan ngrok tünelini başlat
public_url = ngrok.connect(5000)
print(f"🔗 Uygulama bağlantısı (herkese açık): {public_url}")

# 🌐 Banner Grabbing Fonksiyonu
def banner_grab_by_site(domain, port):
    try:
        ip = socket.gethostbyname(domain)
        s = socket.socket()
        s.settimeout(2)
        s.connect((ip, port))
        s.send(b"HEAD / HTTP/1.1\r\nHost: " + domain.encode() + b"\r\n\r\n")
        banner = s.recv(1024).decode(errors="ignore").strip()
        s.close()
        return f"IP: {ip}\n\n" + (banner if banner else "Banner alınamadı.")
    except socket.timeout:
        return "Zaman aşımı!"
    except Exception as e:
        return f"Hata: {e}"

# 🔑 Giriş Sayfası
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        key = request.form.get('key')
        if key == 'adminpro':
            session['authenticated'] = True
            return redirect(url_for('banner_page'))
        else:
            return "<h3>❌ Hatalı anahtar!</h3><a href='/'>"
