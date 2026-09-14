import json
import os
from dotenv import load_dotenv
load_dotenv()
import time
import threading
import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

SITES_FILE = "sites.json"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def load_sites():
    if os.path.exists(SITES_FILE):
        try:
            with open(SITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_sites(sites):
    with open(SITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(sites, f, indent=4, ensure_ascii=False)

def check_single_site(site):
    url = site.get('url')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        # 1. Price extraction
        match = re.search(r'(?:\"price\"|\bprice\b)\s*[:=]\s*(?:\"|\')?(\d+(?:[.,]\d+)?)', response.text)
        price_num = None
        if match:
            clean_price = match.group(1).replace(',', '')
            try: price_num = float(clean_price)
            except: pass
            
        soup = BeautifulSoup(response.text, 'html.parser')
        price_str = ""
        price_elem = soup.select_one('.price, .price2, span[itemprop="price"], meta[itemprop="price"], .box-price-present, .product-price')
        if price_elem:
            if price_elem.name == 'meta':
                price_str = price_elem.get('content', '')
            else:
                price_str = price_elem.get_text(strip=True)
                
        # 2. Stock checking (Rakuten specific initially)
        in_stock = True
        if "ご注文できない商品" in response.text or "売り切れ" in response.text or "品切れ" in response.text:
            in_stock = False
            
        return {
            "status": "success",
            "price_number": price_num,
            "price_text": price_str,
            "in_stock": in_stock,
            "last_checked": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "last_checked": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def background_monitor_loop():
    while True:
        sites = load_sites()
        updated = False
        for site in sites:
            # Nếu đang được bật theo dõi
            if site.get('active', False):
                result = check_single_site(site)
                
                # Logic thông báo
                prev_in_stock = site.get('last_result', {}).get('in_stock', None)
                curr_in_stock = result.get('in_stock', False)
                
                # Luôn luôn gửi thông báo liên tục (theo yêu cầu)
                if DISCORD_WEBHOOK_URL and "URL_WEBHOOK" not in DISCORD_WEBHOOK_URL:
                    if curr_in_stock:
                        msg = f"🎉 **CÓ HÀNG RỒI: {site['name']}**"
                    else:
                        msg = f"📉 **ĐÃ HẾT HÀNG: {site['name']}**"
                        
                    payload = {
                        "content": f"{msg}\n- Giá: {result.get('price_text', 'Không rõ')}\n- Link: {site['url']}"
                    }
                    try: requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
                    except: pass
                
                site['last_result'] = result
                updated = True
        
        if updated:
            save_sites(sites)
            
        # Nghỉ 1 giây mỗi vòng (Siêu nhanh - Dễ spam)
        time.sleep(1)

# Khởi chạy luồng chạy ngầm
monitor_thread = threading.Thread(target=background_monitor_loop, daemon=True)
monitor_thread.start()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sites', methods=['GET'])
def get_sites():
    return jsonify(load_sites())

@app.route('/api/sites', methods=['POST'])
def add_site():
    data = request.json
    if not data or 'name' not in data or 'url' not in data:
        return jsonify({"error": "Thiếu thông tin"}), 400
        
    sites = load_sites()
    new_id = str(int(time.time()))
    new_site = {
        "id": new_id,
        "name": data['name'],
        "url": data['url'],
        "active": False,
        "last_result": None
    }
    sites.append(new_site)
    save_sites(sites)
    return jsonify({"message": "Đã thêm thành công", "site": new_site})

@app.route('/api/sites/<site_id>/toggle', methods=['POST'])
def toggle_site(site_id):
    sites = load_sites()
    found = False
    for site in sites:
        if site['id'] == site_id:
            site['active'] = not site.get('active', False)
            found = True
            break
    if found:
        save_sites(sites)
        return jsonify({"message": "Đã chuyển đổi trạng thái"})
    return jsonify({"error": "Không tìm thấy"}), 404

@app.route('/api/sites/<site_id>', methods=['DELETE'])
def delete_site(site_id):
    sites = load_sites()
    sites = [s for s in sites if s['id'] != site_id]
    save_sites(sites)
    return jsonify({"message": "Đã xóa"})

@app.route('/api/sites/<site_id>/check', methods=['POST'])
def force_check(site_id):
    sites = load_sites()
    for site in sites:
        if site['id'] == site_id:
            result = check_single_site(site)
            site['last_result'] = result
            save_sites(sites)
            return jsonify(result)
    return jsonify({"error": "Không tìm thấy"}), 404

if __name__ == '__main__':
    print("Dashboard is running at http://127.0.0.1:8080")
    app.run(host='127.0.0.1', port=8080)
