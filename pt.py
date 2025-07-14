from flask import Flask, request, redirect, url_for, session

import socket

app = Flask(__name__)
app.secret_key = 'guclu-bir-secret'  # oturum için gerekli

# Banner grabbing fonksiyonu
def banner_grab(ip, port):
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((ip, port))
        s.send(b"HEAD / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
        banner = s.recv(1024).decode(errors="ignore").strip()
        s.close()
        return banner if banner else "Banner alınamadı."
    except socket.timeout:
        return "Zaman aşımı!"
    except Exception as e:
        return f"Hata: {e}"

# Giriş ekranı
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        key = request.form.get('key')
        if key == 'adminpro':
            session['authenticated'] = True
            return redirect(url_for('banner_page'))
        else:
            return """
            <h3>Hatalı anahtar!</h3>
            <a href='/'>Tekrar dene</a>
            """

    return '''
        <h2>Giriş Anahtarı</h2>
        <form method="post">
            <input type="password" name="key" placeholder="Anahtar" required>
            <button type="submit">Giriş</button>
        </form>
    '''

# Asıl banner grabbing sayfası
@app.route('/banner', methods=['GET', 'POST'])
def banner_page():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    html = """
    <h2>Banner Grabbing Tool</h2>
    <form method="post">
        <input type="text" name="ip" placeholder="IP adresi" required>
        <input type="number" name="port" placeholder="Port" required>
        <button type="submit">Tarama Başlat</button>
    </form>
    """

    if request.method == 'POST':
        ip = request.form.get('ip')
        port = int(request.form.get('port'))
        result = banner_grab(ip, port)
        html += f"<h3>Sonuç ({ip}:{port})</h3><pre>{result}</pre>"

    html += '<br><a href="/logout">Çıkış Yap</a>'
    return html

# Çıkış işlemi
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
