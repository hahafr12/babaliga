from flask import Flask, request, render_template_string, redirect, url_for, session
import requests, socket, ssl, whois, os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.secret_key = "gizli-key"

HTML_LOGIN = '''
<h2>Giriş Yap</h2>
<form method="POST">
    Anahtar: <input type="password" name="key">
    <input type="submit" value="Giriş">
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
'''

HTML_FORM = '''
<h2>Website Bilgi Toplayıcı</h2>
<form method="POST">
    Site URL: <input type="text" name="url">
    <input type="submit" value="Bilgileri Getir">
</form>
<pre>{{ result }}</pre>
'''

COMMON_SUBDOMAINS = ['www', 'mail', 'ftp', 'api', 'blog', 'dev', 'test', 'admin']
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 8080, 3306, 8443]

def get_site_info(url):
    result = ""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc or parsed_url.path
        if not domain:
            return "Geçerli bir URL girin."

        ip_address = socket.gethostbyname(domain)
        result += f"🔹 IP Adresi: {ip_address}\n"

        response = requests.get(url, timeout=5)
        headers = response.headers
        result += "\n🔹 HTTP Başlıkları:\n"
        for k, v in headers.items():
            result += f"{k}: {v}\n"

        try:
            robots = requests.get(f"{parsed_url.scheme}://{domain}/robots.txt", timeout=5)
            result += f"\n🔹 robots.txt:\n{robots.text[:500]}\n"
        except:
            result += "\nrobots.txt alınamadı.\n"

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "Yok"
        description = soup.find("meta", attrs={"name": "description"})
        meta_desc = description["content"] if description else "Yok"
        result += f"\n🔹 Sayfa Başlığı: {title}\n"
        result += f"🔹 Meta Açıklama: {meta_desc}\n"

        scripts = soup.find_all("script", src=True)
        result += "\n🔹 JavaScript Dosyaları:\n"
        for script in scripts:
            result += f"{script['src']}\n"
        if not scripts:
            result += "Yok\n"

        result += "\n🔹 Subdomain Taraması:\n"
        for sub in COMMON_SUBDOMAINS:
            subdomain = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(subdomain)
                result += f"{subdomain} → {ip}\n"
            except:
                continue
        if "→" not in result:
            result += "Bulunamadı.\n"

        result += "\n🔹 Port Taraması:\n"
        open_ports = []
        def scan_port(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    result = s.connect_ex((ip_address, port))
                    if result == 0:
                        open_ports.append(port)
            except:
                pass
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(scan_port, COMMON_PORTS)
        result += "Açık Portlar: " + (", ".join(map(str, open_ports)) if open_ports else "Yok") + "\n"

        try:
            whois_info = whois.whois(domain)
            result += "\n🔹 WHOIS Bilgisi:\n"
            result += str(whois_info)
        except:
            result += "\nWHOIS bilgisi alınamadı.\n"

        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.settimeout(5)
                s.connect((domain, 443))
                cert = s.getpeercert()
                result += "\n🔹 SSL Sertifikası:\n"
                result += f"Subject: {cert.get('subject')}\n"
                result += f"Issuer: {cert.get('issuer')}\n"
        except:
            result += "\nSSL bilgisi alınamadı.\n"

        os.makedirs("logs", exist_ok=True)
        with open("logs/site_logs.txt", "a", encoding="utf-8") as log:
            log.write(f"\n--- {domain} ---\n{result}\n")

    except Exception as e:
        result += f"Hata oluştu: {str(e)}"
    return result

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if 'attempts' not in session:
        session['attempts'] = 0

    if session['attempts'] >= 16:
        return "<h3>Giriş hakkınız doldu. Lütfen daha sonra tekrar deneyin.</h3>"

    if request.method == 'POST':
        key = request.form['key']
        if key == "adminpro":
            session['auth'] = True
            session['attempts'] = 0
            return redirect(url_for('index'))
        else:
            session['attempts'] += 1
            kalan = 16 - session['attempts']
            error = f"Hatalı anahtar! Kalan deneme hakkı: {kalan}"

    return render_template_string(HTML_LOGIN, error=error)

@app.route('/analyzer', methods=['GET', 'POST'])
def index():
    if not session.get('auth'):
        return redirect(url_for('login'))

    result = ""
    if request.method == 'POST':
        url = request.form['url']
        if not url.startswith('http'):
            url = 'http://' + url
        result = get_site_info(url)
    return render_template_string(HTML_FORM, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500, debug=True)
