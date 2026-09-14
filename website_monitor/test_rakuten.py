import requests
from bs4 import BeautifulSoup
import re

url = "https://books.rakuten.co.jp/rb/17407091/?bkts=1&l-id=search-c-item-text-01"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://www.google.com/',
}

try:
    print("Fetching URL...")
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    in_stock = True
    if "ご注文できない商品" in response.text or "売り切れ" in response.text or "品切れ" in response.text:
        in_stock = False
        
    print(f"In Stock: {in_stock}")
    
    match = re.search(r'(?:\"price\"|\bprice\b)\s*[:=]\s*(?:\"|\')?(\d+(?:[.,]\d+)?)', response.text)
    if match:
        print(f"Price: {match.group(1)}")
    else:
        print("Price not found via regex")
        
except Exception as e:
    print(f"Error: {e}")
