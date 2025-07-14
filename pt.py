from flask import Flask, request, redirect, url_for, session
from pyngrok import ngrok
import socket

app = Flask(__name__)
app.secret_key = 'gizli-key'  # oturum yönetimi için gerekli

# 🔐 Ngrok Token – sadece ilk kez çalıştırırken ekle
ngrok.set_auth_token("BURAYA_NGROK_TOKENINI_YAZ")  # örn: 2JxkExxx...

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
            return "<h3>❌ Hatalı anahtar!</h3><a href='/'>Tekrar dene</a>"

    return '''
        <h2>🔐 Giriş Anahtarı</h2>
        <form method="post">
            <input type="password" name="key" placeholder="Anahtar (örn: adminpro)" required>
            <button type="submit">Giriş</button>
        </form>
    '''

# 📡 Banner Grabbing Sayfası
@app.route('/banner', methods=['GET', 'POST'])
def banner_page():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    html = """
    <h2>🌍 Web Site Banner Grabbing Tool</h2>
    <form method="post">
        <input type="text" name="domain" placeholder="Site (örn: example.com)" required>
        <input type="number" name="port" placeholder="Port (örn: 80)" required>
        <button type="submit">Başlat</button>
    </form>
    """

    if request.method == 'POST':
        domain = request.form.get('domain')
        port = int(request.form.get('port'))
        result = banner_grab_by_site(domain, port)
        html += f"<h3>Sonuç ({domain}:{port})</h3><pre>{result}</pre>"

    html += '<br><a href="/logout">Çıkış Yap</a>'
    return html

# 🚪 Oturumdan çık
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

# ▶️ Flask başlat
if __name__ == '__main__':
    app.run(port=5000)
