import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def check_and_notify():
    url = "https://item.rakuten.co.jp/sendaihawks/167961015/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Nếu truy cập thành công (Mã 200 OK)
        if response.status_code == 200:
            print("TRANG WEB ĐÃ TRUY CẬP ĐƯỢC! Báo cáo lên Discord...")
            
            # Gửi thông báo Discord
            if DISCORD_WEBHOOK_URL != "https://discord.com/api/webhooks/1549049688626561134/bngjNpIqPwXblmczH4163zi9QTuC1f4KE7RwnGCx96WnAtFimZEirELHJx1PyCUOZr9u":
                discord_payload = {
                    "content": f"🚨 **CẢNH BÁO TỐC ĐỘ CAO** 🚨\nTrang web hiện đã MỞ LẠI và CÓ THỂ TRUY CẬP!\nVào mua ngay: {url}"
                }
                requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
                print("Đã gửi Discord thành công!")
            else:
                print("Bạn chưa điền link Discord Webhook vào code, nên chưa thể gửi tin nhắn!")
                
            return True # Trả về True để dừng vòng lặp
        else:
            print(f"Trang web vẫn đóng (Mã {response.status_code}). Nghỉ 1 giây...")
            return False
            
    except Exception as e:
        print(f"Lỗi mạng hoặc bị chặn. Nghỉ 1 giây...")
        return False

def main():
    print("Bắt đầu khởi chạy chiến dịch quét liên tục (1 giây/lần)...")
    print("Lưu ý: Bấm phím Ctrl + C để tắt nếu bạn muốn dừng lại.")
    
    count = 0
    while True:
        count += 1
        print(f"[Lần quét {count}] ", end="")
        
        is_accessible = check_and_notify()
        
        if is_accessible:
            # Ngừng quét khi đã báo Discord thành công để tránh bị ban Discord do Spam tin nhắn liên tục
            print("Nhiệm vụ hoàn tất! Đã dừng script.")
            break
            
        time.sleep(1) # Nghỉ 1 giây rồi quét tiếp

if __name__ == "__main__":
    main()
