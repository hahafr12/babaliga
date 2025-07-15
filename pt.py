from flask import Flask, request, render_template_string
import requests
import re

app = Flask(__name__)

def get_subdomains(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        subdomains = set()
        for item in data:
            name = item['name_value']
            for sub in name.split('\n'):
                if sub.endswith(domain):
                    subdomains.add(sub.strip())
        return sorted(subdomains)
    except Exception:
        return []

def check_leak(subdomain):
    leaks = {
        "admin": "2023 admin panel sızıntısı",
        "test": "2022 test subdomain leak"
    }
    for key in leaks:
        if key in subdomain:
            return leaks[key]
    return "Bulunamadı"

def extract_domain_from_github(repo_url):
    """github repo url'den domain tahmini yapar (ör: TerMax > termax.com)"""
    match = re.match(r"https?://github\.com/([\w-]+)/([\w-]+)", repo_url)
    if match:
        repo_name = match.group(2)
        # Daha gelişmiş bir domain tahmini gerekiyorsa burada düzenle
        return repo_name.lower() + ".com"
    return None

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Subdomain & Leak Checker</title>
</head>
<body>
    <h1>Subdomain ve Leak Kontrol Aracı</h1>
    <form method="post">
        <input type="text" name="domain" placeholder="site.com veya GitHub repo URL" required value="{{ domain }}">
        <button type="submit">Sorgula</button>
    </form>
    {% if github_url %}
        <p><b>GitHub URL:</b> {{ github_url }}</p>
        <p><b>Tahmini Domain:</b> {{ estimated_domain }}</p>
    {% endif %}
    {% if subdomains %}
        <h2>Sonuçlar:</h2>
        <table border="1">
            <tr>
                <th>Subdomain</th>
                <th>Leak Durumu</th>
            </tr>
            {% for sub in subdomains %}
            <tr>
                <td>{{sub}}</td>
                <td>{{leaks[sub]}}</td>
            </tr>
            {% endfor %}
        </table>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    subdomains = []
    leaks = {}
    domain = ""
    github_url = ""
    estimated_domain = ""
    if request.method == "POST":
        input_val = request.form.get("domain")
        if input_val.startswith("http"):
            github_url = input_val
            estimated_domain = extract_domain_from_github(github_url)
            domain = estimated_domain if estimated_domain else ""
        else:
            domain = input_val
        if domain:
            subdomains = get_subdomains(domain)
            for subdomain in subdomains:
                leaks[subdomain] = check_leak(subdomain)
    return render_template_string(HTML, domain=domain, subdomains=subdomains, leaks=leaks, github_url=github_url, estimated_domain=estimated_domain)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)