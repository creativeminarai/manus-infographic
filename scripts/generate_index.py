import os
import json

PROCESSED_FILE = '/home/ubuntu/manus-infographic/data/processed_files.json'
INDEX_PATH = '/home/ubuntu/manus-infographic/docs/index.html'

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>資料インフォグラフィック一覧</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f1f5f9; }}
    </style>
</head>
<body class="p-4 md:p-12">
    <div class="max-w-5xl mx-auto">
        <header class="mb-12">
            <h1 class="text-4xl font-bold text-slate-900 mb-4">資料インフォグラフィック一覧</h1>
            <p class="text-slate-600 text-lg">追加されたPDF資料の要約をインフォグラフィック形式で閲覧できます。</p>
        </header>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items}
        </div>

        <footer class="mt-20 text-center text-slate-400">
            <p>&copy; 2026 Manus Infographic Automation System</p>
        </footer>
    </div>
</body>
</html>
"""

ITEM_TEMPLATE = """
<div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
    <div class="p-6">
        <h2 class="text-xl font-bold text-slate-800 mb-3 line-clamp-2">{title}</h2>
        <div class="flex items-center space-x-4 mt-6">
            <a href="{infographic_url}" class="flex-1 bg-blue-600 text-white text-center py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                インフォグラフィックを見る
            </a>
        </div>
        <div class="mt-3 text-center">
            <a href="{original_url}" target="_blank" class="text-sm text-slate-400 hover:text-slate-600 underline">
                元資料(PDF)を開く
            </a>
        </div>
    </div>
</div>
"""

def main():
    if not os.path.exists(PROCESSED_FILE):
        return

    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed = json.load(f)

    items_html = []
    # 逆順（新しい順）に表示
    for url, data in reversed(list(processed.items())):
        if data.get('infographic_path'):
            items_html.append(ITEM_TEMPLATE.format(
                title=data['text'],
                infographic_url=data['infographic_path'],
                original_url=url
            ))

    full_html = INDEX_TEMPLATE.format(items="".join(items_html))

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Index page generated at {INDEX_PATH}")

if __name__ == "__main__":
    main()
