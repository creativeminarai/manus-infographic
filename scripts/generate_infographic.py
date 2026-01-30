import os
import json
import subprocess
import markdown
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
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f1f5f9; color: #0f172a; }}
        .hero-gradient {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }}
        .card {{ background: white; border-radius: 1.5rem; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; }}
        .accent-title {{ position: relative; display: inline-block; padding-bottom: 0.5rem; }}
        .accent-title::after {{ content: ''; position: absolute; left: 0; bottom: 0; width: 40%; height: 4px; background: #3b82f6; border-radius: 2px; }}
        
        /* Markdown Custom Styling */
        .content-area h3 {{ font-size: 1.125rem; font-weight: 700; color: #1e40af; margin-top: 1.5rem; margin-bottom: 0.75rem; }}
        .content-area p {{ margin-bottom: 1rem; line-height: 1.7; color: #334155; }}
        .content-area ul {{ list-style: none; padding-left: 0; margin-bottom: 1.25rem; }}
        .content-area li {{ position: relative; padding-left: 1.5rem; margin-bottom: 0.5rem; }}
        .content-area li::before {{ content: '•'; position: absolute; left: 0; color: #3b82f6; font-weight: bold; }}
        
        /* Specific Layout Components */
        .date-box {{ background: #eff6ff; border-left: 6px solid #2563eb; padding: 1.5rem; border-radius: 0.75rem; }}
        .expense-item {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 1rem; border-radius: 0.75rem; transition: all 0.2s; }}
        .expense-item:hover {{ border-color: #3b82f6; background: #f0f9ff; }}
        
        .highlight-card {{ background: linear-gradient(to right, #ffffff, #f0f9ff); border-left: 8px solid #3b82f6; }}
    </style>
</head>
<body class="py-12 px-4 md:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <header class="hero-gradient rounded-[2rem] p-8 md:p-12 mb-10 text-white shadow-2xl relative overflow-hidden">
            <div class="relative z-10">
                <div class="flex items-center gap-3 mb-6">
                    <span class="bg-white/20 backdrop-blur-md px-4 py-1 rounded-full text-xs font-bold tracking-widest border border-white/30 uppercase">Analysis Report</span>
                    <span class="text-blue-100 text-xs">Update: 2026.01.30</span>
                </div>
                <h1 class="text-3xl md:text-5xl font-black mb-6 leading-tight tracking-tight">{title}</h1>
                <div class="flex flex-wrap gap-4">
                    <div class="bg-white/10 backdrop-blur-sm border border-white/20 px-6 py-3 rounded-2xl">
                        <p class="text-blue-50 text-lg font-bold">「{summary_short}」</p>
                    </div>
                </div>
            </div>
            <i class="fas fa-file-invoice-dollar absolute -right-16 -bottom-16 text-[20rem] text-white/5 rotate-12"></i>
        </header>

        <!-- Top Highlights: Summary & Dates -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
            <!-- Short Summary Card -->
            <section class="card p-8 lg:col-span-2 highlight-card">
                <h2 class="text-2xl font-black text-slate-800 mb-6 flex items-center gap-3">
                    <i class="fas fa-quote-left text-blue-500"></i> 資料の要点（30秒で把握）
                </h2>
                <div class="content-area text-lg text-slate-700 leading-relaxed">
                    {summary_long}
                </div>
            </section>

            <!-- Important Dates Card -->
            <section class="card p-8 bg-slate-900 text-white border-none shadow-blue-900/20">
                <h2 class="text-xl font-bold mb-6 flex items-center gap-3 text-blue-400">
                    <i class="fas fa-calendar-check"></i> 重要日程
                </h2>
                <div class="space-y-4">
                    {timeline}
                </div>
            </section>
        </div>

        <!-- Period & Eligibility Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
            <!-- Period Box -->
            <div class="date-box">
                <h3 class="text-blue-800 font-black text-xl mb-4 flex items-center gap-2">
                    <i class="fas fa-hourglass-half"></i> 実施・対象期間
                </h3>
                <div class="content-area text-blue-900 font-medium">
                    {period}
                </div>
            </div>
            <!-- Eligibility Box -->
            <div class="bg-emerald-50 border-l-6 border-emerald-500 p-6 rounded-xl">
                <h3 class="text-emerald-800 font-black text-xl mb-4 flex items-center gap-2">
                    <i class="fas fa-user-tag"></i> 申請対象・要件
                </h3>
                <div class="content-area text-emerald-900 text-sm">
                    {eligibility}
                </div>
            </div>
        </div>

        <!-- Detailed Content Area -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
            <!-- Expenses Analysis (Main) -->
            <div class="lg:col-span-8 space-y-10">
                <section class="card p-8 md:p-10">
                    <h2 class="accent-title text-2xl font-black mb-8 text-slate-800">補助対象経費の詳細</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {expenses}
                    </div>
                </section>

                <section class="card p-8 md:p-10">
                    <h2 class="accent-title text-2xl font-black mb-8 text-slate-800">重要項目の詳細解説</h2>
                    <div class="content-area">
                        {detailed_sections}
                    </div>
                </section>
            </div>

            <!-- Sidebar Info -->
            <div class="lg:col-span-4 space-y-8">
                <!-- Warnings -->
                <section class="card p-8 border-2 border-red-100 bg-red-50/50">
                    <h3 class="font-bold text-xl mb-6 flex items-center gap-3 text-red-700">
                        <i class="fas fa-exclamation-triangle"></i> 注意事項・不備対策
                    </h3>
                    <div class="content-area text-sm text-red-900/80">
                        {warnings}
                    </div>
                </section>

                <!-- Action Plan -->
                <section class="card p-8 border-2 border-blue-600 bg-blue-50/30">
                    <h3 class="font-bold text-xl mb-6 flex items-center gap-3 text-blue-800">
                        <i class="fas fa-rocket"></i> 次のアクション
                    </h3>
                    <div class="content-area text-sm text-blue-900 font-bold">
                        {actions}
                    </div>
                </section>

                <!-- Metadata -->
                <div class="text-center">
                    <a href="{original_url}" target="_blank" class="inline-flex items-center gap-3 px-8 py-4 bg-slate-800 text-white rounded-full font-bold hover:bg-slate-700 transition-all shadow-lg">
                        <i class="fas fa-external-link-alt"></i> 元資料を確認
                    </a>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="mt-20 py-10 border-t border-slate-200 text-center">
            <p class="text-slate-400 text-xs font-bold tracking-widest uppercase mb-4">Generated by Advanced Agent-Python Flow</p>
            <p class="text-slate-400 text-xs max-w-xl mx-auto">
                本資料はAIエージェントによる自動解析によって生成されました。記載内容の正確性については万全を期しておりますが、最終的な判断は必ず公式の元資料をご確認ください。
            </p>
        </footer>
    </div>
</body>
</html>
"""

def extract_text_from_pdf(pdf_path):
    try:
        result = subprocess.run(['pdftotext', '-l', '25', pdf_path, '-'], capture_output=True, text=True)
        return result.stdout[:18000]
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def generate_markdown_draft(title, pdf_text):
    prompt = f"""
    あなたは超一流のビジネスアナリストです。以下の資料を読み解き、経営者が一目で内容を把握できる「視覚的構造化」された原稿を作成してください。
    
    タイトル: {title}
    資料テキスト（抜粋）:
    {pdf_text}
    
    【厳守事項】
    1. 文章を極力短くし、構造化（箇条書き、短い段落）すること。
    2. 要旨（summary_long）は元の3分の1程度、200文字以内で簡潔にまとめること。
    3. 補助対象経費（expenses）は、項目ごとに分けて詳細に記述すること。
    
    【出力形式】
    JSON形式で以下のキーを含めてください:
    - summary_short: 資料の核心を突くキャッチコピー（1文）
    - summary_long: 全体像の要約（200文字以内、簡潔なMarkdown）
    - timeline: 締切日などの重要日程（Markdown形式、各行を独立させる）
    - period: 事業実施期間や対象期間（Markdown形式）
    - eligibility: 申請対象者、金額、主要な要件（Markdownの箇条書き）
    - expenses: 補助対象経費の詳細（HTMLの`<div class="expense-item"><strong>項目名</strong><br>詳細</div>`を複数並べた文字列）
    - detailed_sections: 重要項目の詳細解説（`### 見出し` と短い本文の組み合わせ）
    - warnings: 注意点（Markdownの箇条書き）
    - actions: ネクストステップ（Markdownの箇条書き）
    
    ※注意: 各値の中身はMarkdownまたは指定されたHTML形式にしてください。
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": "You are a visual communication expert. Output high-quality structured content in JSON format."},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def md_to_html(text):
    if not text:
        return ""
    return markdown.markdown(text, extensions=['extra', 'nl2br', 'sane_lists'])

def main():
    if not os.path.exists(PROCESSED_FILE):
        return

    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed = json.load(f)

    for url, data in processed.items():
        print(f"Agent is visually structuring {data['text']}...")
        
        pdf_text = extract_text_from_pdf(data['local_path'])
        draft = generate_markdown_draft(data['text'], pdf_text)
        
        # 原稿を保存
        pdf_filename = os.path.basename(data['local_path'])
        draft_path = os.path.join(DRAFT_DIR, pdf_filename.replace('.pdf', '.json'))
        with open(draft_path, 'w', encoding='utf-8') as f:
            json.dump(draft, f, ensure_ascii=False, indent=2)
            
        # HTMLに変換して流し込み
        html_filename = pdf_filename.replace('.pdf', '.html')
        html_path = os.path.join(INFOGRAPHIC_DIR, html_filename)
        
        html_content = HTML_TEMPLATE.format(
            title=data['text'],
            summary_short=draft['summary_short'],
            summary_long=md_to_html(draft['summary_long']),
            timeline=md_to_html(draft['timeline']),
            period=md_to_html(draft['period']),
            eligibility=md_to_html(draft['eligibility']),
            expenses=draft['expenses'], # これは既にHTML形式で出力させる
            detailed_sections=md_to_html(draft['detailed_sections']),
            warnings=md_to_html(draft['warnings']),
            actions=md_to_html(draft['actions']),
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
