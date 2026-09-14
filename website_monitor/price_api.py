from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/api/price')
def get_price():
    # Ưu tiên lấy url từ query string, nếu không có thì lấy link Rakuten mặc định
    url = request.args.get('url', "https://books.rakuten.co.jp/rb/17407091/?bkts=1&l-id=search-c-item-text-01")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/',
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Phương pháp 1: Lấy từ JSON-LD hoặc biến DataLayer (Rakuten, TGDD, v.v.)
        match = re.search(r'(?:\"price\"|\bprice\b)\s*[:=]\s*(?:\"|\')?(\d+(?:[.,]\d+)?)', response.text)
        price_num = None
        if match:
            # Loại bỏ dấu phẩy nếu có (ví dụ 1,200)
            clean_price = match.group(1).replace(',', '')
            try:
                price_num = float(clean_price)
            except:
                pass
            
        # Phương pháp 2: Tìm trong DOM HTML bằng BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        price_str = ""
        
        # Các class phổ biến cho TGDD và Rakuten
        price_elem = soup.select_one('.price, .price2, span[itemprop="price"], meta[itemprop="price"], .box-price-present, .product-price')
        
        if price_elem:
            if price_elem.name == 'meta':
                price_str = price_elem.get('content', '')
            else:
                price_str = price_elem.get_text(strip=True)
            
        # Kiểm tra tình trạng còn hàng (đặc biệt cho Rakuten)
        # "ご注文できない商品" = Không thể đặt hàng (hết hàng)
        in_stock = True
        if "ご注文できない商品" in response.text or "売り切れ" in response.text or "品切れ" in response.text:
            in_stock = False
            
        return jsonify({
            "status": "success",
            "data": {
                "url": url,
                "price_number": price_num,
                "price_text": price_str,
                "in_stock": in_stock
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    print("API Server đang chạy tại http://127.0.0.1:5000/api/price")
    app.run(host='127.0.0.1', port=5000)
