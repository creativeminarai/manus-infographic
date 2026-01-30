import os
import json
import subprocess
from openai import OpenAI

client = OpenAI()

PROCESSED_FILE = '/home/ubuntu/manus-infographic/data/processed_files.json'
INFOGRAPHIC_DIR = '/home/ubuntu/manus-infographic/docs/infographics'
DRAFT_DIR = '/home/ubuntu/manus-infographic/data/drafts'

os.makedirs(INFOGRAPHIC_DIR, exist_ok=True)
os.makedirs(DRAFT_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f1f5f9; color: #1e293b; }}
        .gradient-bg {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }}
        .card {{ background: white; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; }}
        .section-title {{ border-left: 4px solid #3b82f6; padding-left: 1rem; margin-bottom: 1.5rem; font-weight: 700; color: #1e3a8a; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; }}
        .badge-blue {{ background-color: #dbeafe; color: #1e40af; }}
        .prose h3 {{ font-size: 1.25rem; font-weight: 700; color: #1e3a8a; margin-top: 1.5rem; margin-bottom: 0.75rem; }}
        .prose p {{ margin-bottom: 1rem; line-height: 1.7; }}
        .prose ul {{ list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1rem; }}
        .prose li {{ margin-bottom: 0.5rem; }}
    </style>
</head>
<body class="py-8 px-4 md:px-0">
    <div class="max-w-5xl mx-auto">
        <!-- Header -->
        <header class="gradient-bg rounded-2xl p-8 mb-8 text-white shadow-lg relative overflow-hidden">
            <div class="relative z-10">
                <div class="flex items-center gap-3 mb-4">
                    <span class="badge badge-blue bg-white/20 text-white border border-white/30">AI要約・構造化資料</span>
                    <span class="text-white/80 text-sm">Update: 2026.01.30</span>
                </div>
                <h1 class="text-3xl md:text-4xl font-bold leading-tight mb-4">{title}</h1>
                <p class="text-blue-100 text-lg max-w-3xl">{summary_short}</p>
            </div>
            <i class="fas fa-magic absolute -right-8 -bottom-8 text-9xl text-white/10 rotate-12"></i>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Left Column: Main Info -->
            <div class="lg:col-span-2 space-y-8">
                <!-- Overview Section -->
                <section class="card p-8">
                    <h2 class="section-title text-2xl">資料の全体像</h2>
                    <div class="prose max-w-none text-slate-600">
                        {summary_long}
                    </div>
                </section>

                <!-- Key Points & Eligibility -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <section class="card p-6 border-t-4 border-t-green-500">
                        <h3 class="font-bold text-xl mb-4 flex items-center gap-2">
                            <i class="fas fa-lightbulb text-green-500"></i> 重要ポイント
                        </h3>
                        <div class="prose text-sm text-slate-600">
                            {points}
                        </div>
                    </section>
                    <section class="card p-6 border-t-4 border-t-blue-500">
                        <h3 class="font-bold text-xl mb-4 flex items-center gap-2">
                            <i class="fas fa-user-check text-blue-500"></i> 対象・要件
                        </h3>
                        <div class="prose text-sm text-slate-600">
                            {eligibility}
                        </div>
                    </section>
                </div>

                <!-- Detailed Content -->
                <section class="card p-8">
                    <h2 class="section-title text-2xl">詳細解説</h2>
                    <div class="prose max-w-none text-slate-600">
                        {detailed_sections}
                    </div>
                </section>
            </div>

            <!-- Right Column: Sidebar -->
            <div class="space-y-8">
                <!-- Timeline -->
                <section class="card p-6 bg-slate-50">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2 text-slate-800">
                        <i class="fas fa-clock text-orange-500"></i> 期限・スケジュール
                    </h3>
                    <div class="prose text-sm text-slate-600">
                        {timeline}
                    </div>
                </section>

                <!-- Warnings -->
                <section class="card p-6 border-l-4 border-l-red-500 bg-red-50">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2 text-red-800">
                        <i class="fas fa-exclamation-circle"></i> 注意事項・不備対策
                    </h3>
                    <div class="prose text-sm text-red-900/80">
                        {warnings}
                    </div>
                </section>

                <!-- Next Actions -->
                <section class="card p-6 bg-blue-50 border border-blue-100">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2 text-blue-800">
                        <i class="fas fa-tasks text-blue-600"></i> 推奨アクション
                    </h3>
                    <div class="prose text-sm text-blue-800/90">
                        {actions}
                    </div>
                </section>

                <div class="text-center p-4">
                    <a href="{original_url}" target="_blank" class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium transition-colors">
                        <i class="fas fa-external-link-alt"></i> 元資料を確認する
                    </a>
                </div>
            </div>
        </div>

        <footer class="mt-12 py-8 border-t border-slate-200 text-center text-slate-500 text-sm">
            <p>Generated by Agent-Python Hybrid System &copy; 2026</p>
            <p class="mt-1">この資料はエージェントによる思考と解析を経て自動生成されました。</p>
        </footer>
    </div>
</body>
</html>
"""

def extract_text_from_pdf(pdf_path):
    try:
        result = subprocess.run(['pdftotext', '-l', '15', pdf_path, '-'], capture_output=True, text=True)
        return result.stdout[:12000]
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def generate_markdown_draft(title, pdf_text):
    """エージェントにMarkdown形式の原稿を作成させる"""
    prompt = f"""
    あなたはプロフェッショナルなビジネスアナリストです。以下の資料を読み解き、インフォグラフィック用の「原稿」をMarkdown形式で作成してください。
    
    タイトル: {title}
    資料テキスト（抜粋）:
    {pdf_text}
    
    以下の項目を構造化して記述してください。各項目は後でHTMLに埋め込むため、指定されたJSONキーに対応する内容をMarkdown（HTMLタグも可）で出力してください。
    
    JSON形式で出力してください:
    - summary_short: 資料を一言で表すキャッチコピー（50文字以内）
    - summary_long: 全体像の解説（複数の段落に分ける）
    - points: 重要なポイント（箇条書き）
    - eligibility: 対象者・要件（箇条書き）
    - detailed_sections: 主要な章ごとの詳細解説（### 見出し と 本文の組み合わせ）
    - timeline: スケジュールや締切（時系列がわかるように）
    - warnings: 注意点（箇条書き）
    - actions: 次のステップ（チェックリスト形式など）
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": "You are an expert analyst. Provide deep insights and structured drafts in JSON format."},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def markdown_to_html_snippet(text):
    """簡易的なMarkdown to HTML変換（ここではLLMが既に適切な形式で出していることを期待しつつ、必要なら調整）"""
    # 今回はLLMにHTMLタグも含めたMarkdownを出力させるため、そのまま使用
    return text

def main():
    if not os.path.exists(PROCESSED_FILE):
        return

    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed = json.load(f)

    for url, data in processed.items():
        print(f"Agent is thinking about {data['text']}...")
        
        pdf_text = extract_text_from_pdf(data['local_path'])
        
        # 1. エージェントが原稿を作成
        draft = generate_markdown_draft(data['text'], pdf_text)
        
        # 原稿を保存（デバッグ・記録用）
        pdf_filename = os.path.basename(data['local_path'])
        draft_path = os.path.join(DRAFT_DIR, pdf_filename.replace('.pdf', '.json'))
        with open(draft_path, 'w', encoding='utf-8') as f:
            json.dump(draft, f, ensure_ascii=False, indent=2)
            
        # 2. PythonがHTMLに整形
        html_filename = pdf_filename.replace('.pdf', '.html')
        html_path = os.path.join(INFOGRAPHIC_DIR, html_filename)
        
        html_content = HTML_TEMPLATE.format(
            title=data['text'],
            summary_short=draft['summary_short'],
            summary_long=markdown_to_html_snippet(draft['summary_long']),
            points=markdown_to_html_snippet(draft['points']),
            eligibility=markdown_to_html_snippet(draft['eligibility']),
            detailed_sections=markdown_to_html_snippet(draft['detailed_sections']),
            timeline=markdown_to_html_snippet(draft['timeline']),
            warnings=markdown_to_html_snippet(draft['warnings']),
            actions=markdown_to_html_snippet(draft['actions']),
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
