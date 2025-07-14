from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

def log_request(ip, user_agent):
    log_line = f"{datetime.now()} - IP: {ip}, User-Agent: {user_agent}\n"
    with open("log.txt", "a") as file:
        file.write(log_line)

@app.route("/")
def index():
    # IP adresini al
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    # User-Agent (cihaz bilgileri)
    user_agent = request.headers.get('User-Agent')

    # Logla
    log_request(ip_address, user_agent)

    return f"IP adresin: {ip_address}<br>Cihaz bilgilerin: {user_agent}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
