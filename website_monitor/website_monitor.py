import os
import json
import time
import hashlib
import requests
import difflib
from datetime import datetime, timezone
from bs4 import BeautifulSoup

CONFIG_FILE = 'config.json'
STATE_FILE = 'state.json'

def load_json(filepath, default_val=None):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    return default_val if default_val is not None else {}

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

def get_page_content(url, selector):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        if selector:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator='\n', strip=True)
            else:
                return f"[Selector '{selector}' not found]"
        else:
            return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def compute_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def generate_diff(old_text, new_text):
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff = difflib.unified_diff(old_lines, new_lines, fromfile='old', tofile='new', lineterm='')
    return '\n'.join(list(diff)[:20]) # Chỉ lấy 20 dòng đầu của diff

def send_notification(config, site_name, url, diff):
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = {
        "event": "website_changed",
        "site_name": site_name,
        "url": url,
        "diff": diff,
        "timestamp": timestamp
    }
    
    n8n_url = os.environ.get('N8N_WEBHOOK_URL') or config.get('n8n_webhook_url')
    discord_url = os.environ.get('DISCORD_WEBHOOK_URL') or config.get('discord_webhook_url')
    
    if n8n_url:
        try:
            response = requests.post(n8n_url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"Sent notification to n8n for {site_name}")
        except Exception as e:
            print(f"Failed to send to n8n: {e}")
    elif discord_url:
        try:
            discord_payload = {
                "content": f"🔔 **Phát hiện thay đổi:** {site_name}\n{url}\n```diff\n{diff[:1500]}\n```"
            }
            response = requests.post(discord_url, json=discord_payload, timeout=10)
            response.raise_for_status()
            print(f"Sent notification to Discord for {site_name}")
        except Exception as e:
            print(f"Failed to send to Discord: {e}")
    else:
        print(f"No webhook configured. Detected change on {site_name}")

def monitor():
    config = load_json(CONFIG_FILE, {})
    if not config:
        print("Config file not found or empty.")
        return
        
    state = load_json(STATE_FILE, {})
    sites = config.get('sites', [])
    
    for site in sites:
        name = site.get('name')
        url = site.get('url')
        selector = site.get('selector')
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking {name} ({url})...")
        content = get_page_content(url, selector)
        
        if content is None:
            continue
            
        current_hash = compute_hash(content)
        site_state = state.get(url, {})
        previous_hash = site_state.get('hash')
        
        if previous_hash is None:
            print(f"First run for {name}. Saving initial state.")
            state[url] = {
                'hash': current_hash,
                'content': content
            }
            save_json(STATE_FILE, state)
        elif current_hash != previous_hash:
            print(f"Change detected for {name}!")
            previous_content = site_state.get('content', '')
            diff = generate_diff(previous_content, content)
            
            send_notification(config, name, url, diff)
            
            state[url] = {
                'hash': current_hash,
                'content': content
            }
            save_json(STATE_FILE, state)
        else:
            print(f"No changes for {name}.")
            
def main():
    config = load_json(CONFIG_FILE, {})
    run_once = config.get('run_once', False)
    interval = config.get('check_interval_seconds', 300)
    
    if run_once:
        monitor()
    else:
        while True:
            monitor()
            print(f"Sleeping for {interval} seconds...")
            time.sleep(interval)

if __name__ == "__main__":
    main()
