import os
import json
import subprocess
from openai import OpenAI

client = OpenAI()

PROCESSED_FILE = '/home/ubuntu/manus-infographic/data/processed_files.json'
INFOGRAPHIC_DIR = '/home/ubuntu/manus-infographic/docs/infographics'

os.makedirs(INFOGRAPHIC_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f8fafc; }}
        .card {{ background: white; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }}
        .accent-bar {{ height: 4px; background: linear-gradient(90deg, #3b82f6, #2563eb); border-radius: 1rem 1rem 0 0; }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8 text-center">
            <h1 class="text-3xl font-bold text-slate-800 mb-2">{title}</h1>
            <p class="text-slate-500">資料の要約と重要ポイントのまとめ</p>
        </header>

        <main class="space-y-6">
            <section class="card overflow-hidden">
                <div class="accent-bar"></div>
                <div class="p-6">
                    <h2 class="text-xl font-bold text-blue-700 mb-4">概要</h2>
                    <div class="prose text-slate-700 leading-relaxed">
                        {summary}
                    </div>
                </div>
            </section>

            <div class="grid md:grid-cols-2 gap-6">
                <section class="card overflow-hidden">
                    <div class="accent-bar bg-green-500"></div>
                    <div class="p-6">
                        <h2 class="text-xl font-bold text-green-700 mb-4">重要ポイント</h2>
                        <ul class="list-disc list-inside space-y-2 text-slate-700">
                            {points}
                        </ul>
                    </div>
                </section>

                <section class="card overflow-hidden">
                    <div class="accent-bar bg-orange-500"></div>
                    <div class="p-6">
                        <h2 class="text-xl font-bold text-orange-700 mb-4">注意点・締切</h2>
                        <ul class="list-disc list-inside space-y-2 text-slate-700">
                            {warnings}
                        </ul>
                    </div>
                </section>
            </div>

            <section class="card overflow-hidden">
                <div class="accent-bar bg-purple-500"></div>
                <div class="p-6">
                    <h2 class="text-xl font-bold text-purple-700 mb-4">次のアクション</h2>
                    <div class="prose text-slate-700">
                        {actions}
                    </div>
                </div>
            </section>
        </main>

        <footer class="mt-12 text-center text-slate-400 text-sm">
            <p>元資料: <a href="{original_url}" class="text-blue-500 hover:underline" target="_blank">こちらをクリック</a></p>
            <p class="mt-2">&copy; 2026 Manus Infographic Generator</p>
        </footer>
    </div>
</body>
</html>
"""

def extract_text_from_pdf(pdf_path):
    try:
        # pdftotextを使用してテキストを抽出
        result = subprocess.run(['pdftotext', '-l', '5', pdf_path, '-'], capture_output=True, text=True)
        return result.stdout[:4000] # 最初の4000文字程度を返す
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def generate_infographic_content(title, pdf_text):
    prompt = f"""
    以下の資料タイトルとPDFから抽出されたテキストに基づき、ビジネス向けのインフォグラフィックHTML用のコンテンツを生成してください。
    
    タイトル: {title}
    PDFテキスト抽出（一部）:
    {pdf_text}
    
    出力はJSON形式で以下のキーを含めてください:
    - summary: 資料の概要（200文字程度）
    - points: 重要ポイントのリスト（HTMLの<li>タグ形式）
    - warnings: 注意点や締切のリスト（HTMLの<li>タグ形式）
    - actions: 推奨される次のアクション（HTML形式）
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def main():
    if not os.path.exists(PROCESSED_FILE):
        return

    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed = json.load(f)

    for url, data in processed.items():
        if not data.get('processed'):
            print(f"Generating infographic for {data['text']}...")
            
            # PDFからテキストを抽出
            pdf_text = extract_text_from_pdf(data['local_path'])
            
            # コンテンツ生成
            content = generate_infographic_content(data['text'], pdf_text)
            
            # HTML作成
            pdf_filename = os.path.basename(data['local_path'])
            html_filename = pdf_filename.replace('.pdf', '.html')
            html_path = os.path.join(INFOGRAPHIC_DIR, html_filename)
            
            html_content = HTML_TEMPLATE.format(
                title=data['text'],
                summary=content['summary'],
                points=content['points'],
                warnings=content['warnings'],
                actions=content['actions'],
                original_url=url
            )
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            data['processed'] = True
            data['infographic_path'] = f"infographics/{html_filename}"

    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
