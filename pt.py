from flask import Flask, request
from user_agents import parse
from datetime import datetime
import json
import requests

app = Flask(__name__)

def get_location(ip):
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/")
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country_name"),
                "city": data.get("city"),
                "org": data.get("org"),
                "region": data.get("region")
            }
    except:
        return {}
    return {}

def log_request(info):
    try:
        with open("logs.json", "a") as file:
            file.write(json.dumps(info, ensure_ascii=False) + "\n")
    except Exception as e:
        print("Loglama hatası:", e)

@app.route("/")
def index():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent_str = request.headers.get('User-Agent')
    user_agent = parse(user_agent_str)

    device_type = "Mobil" if user_agent.is_mobile else "Tablet" if user_agent.is_tablet else "PC"

    location = get_location(ip_address)

    log_data = {
        "timestamp": str(datetime.now()),
        "ip": ip_address,
        "device": device_type,
        "browser": user_agent.browser.family,
        "os": user_agent.os.family,
        "location": location,
        "user_agent": user_agent_str
    }

    log_request(log_data)

    return f"""
    <h2>Cihaz Bilgilerin</h2>
    <ul>
        <li><strong>IP:</strong> {ip_address}</li>
        <li><strong>Tarayıcı:</strong> {user_agent.browser.family}</li>
        <li><strong>İşletim Sistemi:</strong> {user_agent.os.family}</li>
        <li><strong>Cihaz Türü:</strong> {device_type}</li>
        <li><strong>Şehir:</strong> {location.get('city', 'Bilinmiyor')}</li>
        <li><strong>Ülke:</strong> {location.get('country', 'Bilinmiyor')}</li>
        <li><strong>İnternet Sağlayıcı:</strong> {location.get('org', 'Bilinmiyor')}</li>
    </ul>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
