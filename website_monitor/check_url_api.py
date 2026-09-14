from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

app = Flask(__name__)

@app.route('/api/check')
def check_url():
    # Lấy URL từ tham số hoặc dùng URL mặc định bạn yêu cầu
    url = request.args.get('url', "https://item.rakuten.co.jp/sendaihawks/167961015/")
    
    # Bộ ngụy trang chống Bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        # Kiểm tra nếu trả về mã 200 (Truy cập thành công)
        if response.status_code == 200:
            is_accessible = True
            
            # Tự động gửi thông báo lên Discord
            if DISCORD_WEBHOOK_URL and DISCORD_WEBHOOK_URL != "URL_WEBHOOK_CỦA_BẠN":
                payload = {
                    "content": f"🚨 **TRANG WEB ĐÃ TRUY CẬP ĐƯỢC (CÓ HÀNG)!** 🚨\n- Link đặt mua: {url}"
                }
                try:
                    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
                except Exception as e:
                    pass
        else:
            is_accessible = False
            
        return jsonify({
            "status": "success",
            "url": url,
            "accessible": is_accessible,
            "status_code": response.status_code
        })
        
    except Exception as e:
        # Nếu bị lỗi (Timeout, rớt mạng, bị chặn...)
        return jsonify({
            "status": "error",
            "url": url,
            "accessible": False,
            "message": str(e)
        })

if __name__ == '__main__':
    print("API kiểm tra kết nối đang chạy tại http://127.0.0.1:5001/api/check")
    # Sử dụng port 5001 để không bị đụng chạm với file price_api.py (đang chạy port 5000)
    app.run(host='127.0.0.1', port=5001)
