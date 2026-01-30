import os
import json
import subprocess
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

URLS_FILE = '/home/ubuntu/manus-infographic/data/urls.txt'
PROCESSED_FILE = '/home/ubuntu/manus-infographic/data/processed_files.json'
DOWNLOAD_DIR = '/home/ubuntu/manus-infographic/data/downloads'

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def load_processed():
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                return json.loads(content) if content else {}
        except Exception:
            return {}
    return {}

def save_processed(data):
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_valid_pdf(path):
    if not os.path.exists(path):
        return False
    try:
        result = subprocess.run(['file', path], capture_output=True, text=True)
        return 'PDF document' in result.stdout
    except Exception:
        return False

def get_pdf_links(url):
    try:
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=15)
        response.raise_for_status()
        
        # エンコーディングを明示的に設定（chardetが失敗する場合に備え）
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding
            
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            clean_href = href.split('?')[0]
            if clean_href.lower().endswith('.pdf'):
                full_url = urljoin(url, href)
                text = a.get_text(strip=True) or os.path.basename(urlparse(full_url).path)
                
                # IT導入補助金の場合は公募要領のみに絞る
                if 'it-shien.smrj.go.jp' in full_url:
                    if 'koubo' not in full_url:
                        continue
                
                links.append({'url': full_url, 'text': text})
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def download_pdf_with_curl(url, filename, referer):
    path = os.path.join(DOWNLOAD_DIR, filename)
    try:
        cmd = [
            'curl', '-L', '-A', USER_AGENT,
            '-H', f'Referer: {referer}',
            url, '-o', path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        if is_valid_pdf(path):
            return path
        else:
            print(f"Downloaded file is not a valid PDF: {url}")
            if os.path.exists(path):
                os.remove(path)
            return None
    except Exception as e:
        print(f"Error downloading with curl {url}: {e}")
        return None

def main():
    with open(URLS_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    processed = load_processed()
    new_pdfs = []

    for url in urls:
        print(f"Checking {url}...")
        links = get_pdf_links(url)
        for link in links:
            pdf_url = link['url']
            
            if pdf_url in processed:
                data = processed[pdf_url]
                if data.get('local_path') and is_valid_pdf(data['local_path']):
                    continue
                else:
                    print(f"Redownloading invalid or missing PDF: {pdf_url}")
            
            print(f"Attempting to download: {pdf_url}")
            url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:10]
            filename = f"doc_{url_hash}.pdf"
            
            local_path = download_pdf_with_curl(pdf_url, filename, url)
            if local_path:
                print(f"Successfully downloaded PDF: {filename}")
                entry = {
                    'url': pdf_url,
                    'text': link['text'],
                    'local_path': local_path,
                    'processed': False
                }
                processed[pdf_url] = entry
                new_pdfs.append(entry)

    save_processed(processed)
    return new_pdfs

if __name__ == "__main__":
    main()
