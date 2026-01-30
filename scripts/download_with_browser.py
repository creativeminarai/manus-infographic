import os
import time
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

DOWNLOAD_DIR = '/home/ubuntu/manus-infographic/data/downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_pdf_with_selenium(url, filename):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # PDFを直接ダウンロードするための設定
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # ダウンロード完了を待つ（簡易的な実装）
        time.sleep(10)
        
        # ダウンロードされた最新のファイルを探す
        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            return None
        
        # 最も新しいファイルを取得
        latest_file = max([os.path.join(DOWNLOAD_DIR, f) for f in files], key=os.path.getctime)
        
        # 指定の名前にリネーム
        new_path = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(new_path):
            os.remove(new_path)
        os.rename(latest_file, new_path)
        
        return new_path
    except Exception as e:
        print(f"Selenium error: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    # テスト用
    test_url = "https://www.jizokukanb.com/jizokuka_r6h/doc/kobo/r6_19/19_一般型_公募要領_第5版.pdf?28"
    download_pdf_with_selenium(test_url, "test.pdf")
