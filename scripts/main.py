import subprocess
import os

SCRIPTS_DIR = '/home/ubuntu/manus-infographic/scripts'
REPO_DIR = '/home/ubuntu/manus-infographic'

def run_script(name):
    print(f"--- Running {name} ---")
    script_path = os.path.join(SCRIPTS_DIR, name)
    result = subprocess.run(['python3', script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error in {name}: {result.stderr}")

def main():
    # 1. PDFチェックとダウンロード
    run_script('check_pdfs.py')
    
    # 2. インフォグラフィック生成
    run_script('generate_infographic.py')
    
    # 3. インデックスページ更新
    run_script('generate_index.py')
    
    # 4. GitHubにプッシュ
    print("--- Pushing to GitHub ---")
    try:
        os.chdir(REPO_DIR)
        subprocess.run(['git', 'add', '.'], check=True)
        # 変更があるか確認
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if status.stdout:
            subprocess.run(['git', 'commit', '-m', 'Update infographics and index'], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print("Successfully pushed to GitHub.")
        else:
            print("No changes to commit.")
    except Exception as e:
        print(f"GitHub push failed: {e}")

if __name__ == "__main__":
    main()
