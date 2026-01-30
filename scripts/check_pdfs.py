import os
import json
import requests
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

URLS_FILE = '/home/ubuntu/manus-infographic/data/urls.txt'
PROCESSED_FILE = '/home/ubuntu/manus-infographic/data/processed_files.json'
DOWNLOAD_DIR = '/home/ubuntu/manus-infographic/data/downloads'

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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

def get_pdf_links(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.lower().split('?')[0].endswith('.pdf'):
                full_url = urljoin(url, href)
                text = a.get_text(strip=True) or os.path.basename(urlparse(full_url).path)
                links.append({'url': full_url, 'text': text})
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def download_pdf(url, filename):
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        path = os.path.join(DOWNLOAD_DIR, filename)
        with open(path, 'wb') as f:
            f.write(response.content)
        return path
    except Exception as e:
        print(f"Error downloading {url}: {e}")
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
            if pdf_url not in processed:
                print(f"New PDF found: {pdf_url}")
                
                # URLから一意のID（ハッシュ）を生成してファイル名にする
                url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:10]
                filename = f"doc_{url_hash}.pdf"
                
                local_path = download_pdf(pdf_url, filename)
                if local_path:
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
