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
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f8fafc; color: #1e293b; }}
        .gradient-bg {{ background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%); }}
        .card {{ background: white; border-radius: 1.25rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #f1f5f9; }}
        .section-title {{ border-left: 5px solid #3b82f6; padding-left: 1.25rem; margin-bottom: 1.5rem; font-weight: 700; color: #0f172a; font-size: 1.5rem; }}
        
        /* Markdown Content Styling */
        .content-area h3 {{ font-size: 1.25rem; font-weight: 700; color: #1e40af; margin-top: 2rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }}
        .content-area h3::before {{ content: '●'; font-size: 0.8rem; color: #3b82f6; }}
        .content-area p {{ margin-bottom: 1.25rem; line-height: 1.8; color: #334155; }}
        .content-area ul {{ list-style: none; padding-left: 0.5rem; margin-bottom: 1.5rem; }}
        .content-area li {{ position: relative; padding-left: 1.75rem; margin-bottom: 0.75rem; line-height: 1.6; }}
        .content-area li::before {{ content: '\\f058'; font-family: 'Font Awesome 6 Free'; font-weight: 900; position: absolute; left: 0; color: #10b981; }}
        
        /* Sidebar Specific Styling */
        .sidebar-area ul {{ list-style: none; padding: 0; }}
        .sidebar-area li {{ position: relative; padding-left: 1.5rem; margin-bottom: 0.75rem; font-size: 0.875rem; }}
        .sidebar-area li::before {{ content: '→'; position: absolute; left: 0; color: #3b82f6; font-weight: bold; }}
        
        .timeline-item {{ border-left: 2px dashed #cbd5e1; padding-left: 1.5rem; position: relative; margin-bottom: 1.5rem; }}
        .timeline-item::after {{ content: ''; width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; position: absolute; left: -7px; top: 5px; }}
    </style>
</head>
<body class="py-12 px-4 md:px-6">
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <header class="gradient-bg rounded-3xl p-10 mb-10 text-white shadow-2xl relative overflow-hidden">
            <div class="relative z-10">
                <div class="flex flex-wrap items-center gap-3 mb-6">
                    <span class="bg-blue-500/30 backdrop-blur-md text-white px-4 py-1 rounded-full text-xs font-bold border border-white/20 tracking-wider">
                        <i class="fas fa-robot mr-2"></i>AGENT ANALYZED
                    </span>
                    <span class="text-blue-200 text-xs font-medium">DOCUMENT INSIGHT v2.0</span>
                </div>
                <h1 class="text-3xl md:text-5xl font-extrabold leading-tight mb-6 tracking-tight">{title}</h1>
                <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 inline-block">
                    <p class="text-blue-50 text-lg font-medium">「{summary_short}」</p>
                </div>
            </div>
            <i class="fas fa-shield-halved absolute -right-12 -top-12 text-[15rem] text-white/5 -rotate-12"></i>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
            <!-- Main Content (8 cols) -->
            <div class="lg:col-span-8 space-y-10">
                <!-- Overview Section -->
                <section class="card p-10">
                    <h2 class="section-title">資料の要旨</h2>
                    <div class="content-area">
                        {summary_long}
                    </div>
                </section>

                <!-- Key Info Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <section class="card p-8 border-t-8 border-t-emerald-500">
                        <h3 class="font-bold text-xl mb-6 flex items-center gap-3 text-emerald-800">
                            <i class="fas fa-star"></i> 注目すべき重要点
                        </h3>
                        <div class="content-area text-sm">
                            {points}
                        </div>
                    </section>
                    <section class="card p-8 border-t-8 border-t-indigo-500">
                        <h3 class="font-bold text-xl mb-6 flex items-center gap-3 text-indigo-800">
                            <i class="fas fa-clipboard-check"></i> 申請対象・主な要件
                        </h3>
                        <div class="content-area text-sm">
                            {eligibility}
                        </div>
                    </section>
                </div>

                <!-- Detailed Analysis -->
                <section class="card p-10 bg-gradient-to-br from-white to-blue-50/30">
                    <h2 class="section-title">詳細分析・重要項目解説</h2>
                    <div class="content-area">
                        {detailed_sections}
                    </div>
                </section>
            </div>

            <!-- Sidebar (4 cols) -->
            <div class="lg:col-span-4 space-y-8">
                <!-- Schedule -->
                <section class="card p-8 bg-slate-900 text-white">
                    <h3 class="font-bold text-xl mb-6 flex items-center gap-3 text-blue-400">
                        <i class="fas fa-calendar-days"></i> 重要スケジュール
                    </h3>
                    <div class="sidebar-area">
                        {timeline}
                    </div>
                </section>

                <!-- Warnings -->
                <section class="card p-8 border-2 border-amber-200 bg-amber-50">
                    <h3 class="font-bold text-xl mb-6 flex items-center gap-3 text-amber-800">
                        <i class="fas fa-triangle-exclamation"></i> 見落とし厳禁の注意点
                    </h3>
                    <div class="sidebar-area text-amber-900/90">
                        {warnings}
                    </div>
                </section>

                <!-- Action Plan -->
                <section class="card p-8 border-2 border-blue-600">
                    <h3 class="font-bold text-xl mb-6 flex items-center gap-3 text-blue-800">
                        <i class="fas fa-route"></i> 今すぐ取り組むべき行動
                    </h3>
                    <div class="sidebar-area text-blue-900">
                        {actions}
                    </div>
                </section>

                <!-- External Link -->
                <div class="p-6 text-center">
                    <a href="{original_url}" target="_blank" class="group inline-flex items-center gap-3 bg-white border border-slate-200 px-6 py-3 rounded-full shadow-sm hover:shadow-md hover:bg-slate-50 transition-all duration-300">
                        <span class="text-slate-600 font-bold tracking-wide">ORIGINAL DOCUMENT</span>
                        <i class="fas fa-arrow-up-right-from-square text-blue-500 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform"></i>
                    </a>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="mt-20 py-10 border-t border-slate-200 text-center">
            <p class="text-slate-400 text-sm font-medium tracking-widest uppercase">Manus Intelligence Service</p>
            <p class="text-slate-300 text-xs mt-4 max-w-2xl mx-auto leading-relaxed">
                本資料はAIエージェントによる自動解析によって生成されました。記載内容の正確性については万全を期しておりますが、最終的な判断は必ず公式の元資料をご確認ください。
            </p>
        </footer>
    </div>
</body>
</html>
"""

def extract_text_from_pdf(pdf_path):
    try:
        result = subprocess.run(['pdftotext', '-l', '20', pdf_path, '-'], capture_output=True, text=True)
        return result.stdout[:15000]
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def generate_markdown_draft(title, pdf_text):
    prompt = f"""
    あなたは超一流のビジネスコンサルタント兼テクニカルライターです。
    以下の資料を徹底的に分析し、経営者が一目で内容を把握できる「インフォグラフィック用原稿」を作成してください。
    
    タイトル: {title}
    資料テキスト（抜粋）:
    {pdf_text}
    
    以下の項目を、構造化された純粋なMarkdown形式で作成してください。
    
    【出力形式】
    JSON形式で以下のキーを含めてください:
    - summary_short: 資料の核心を突くキャッチコピー（1文）
    - summary_long: 全体像の論理的な解説（Markdownの段落）
    - points: 経営上重要な3〜5つのポイント（Markdownの箇条書き `- `）
    - eligibility: 申請対象者、金額、主要な要件（Markdownの箇条書き `- `）
    - detailed_sections: 補助対象経費、審査のポイント、事業計画書の書き方など、実務的な詳細解説（`### 見出し` と本文の組み合わせ）
    - timeline: 締切日、事業実施期間などの重要日程（Markdown形式）
    - warnings: 不採択になりやすいポイントや返還リスクなどの警告（Markdownの箇条書き `- `）
    - actions: 準備すべき書類や相談先などのネクストステップ（Markdownの箇条書き `- `）
    
    ※注意: 各値の中身は純粋なMarkdownにしてください。HTMLタグは混ぜないでください。
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": "You are a world-class business analyst. Output ONLY valid JSON containing high-quality Markdown content."},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def md_to_html(text):
    """MarkdownをHTMLに変換し、安全な処理を行う"""
    if not text:
        return ""
    # 拡張機能を使用してテーブルやリストを適切に処理
    return markdown.markdown(text, extensions=['extra', 'nl2br', 'sane_lists'])

def main():
    if not os.path.exists(PROCESSED_FILE):
        return

    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed = json.load(f)

    for url, data in processed.items():
        print(f"Agent is deeply analyzing {data['text']}...")
        
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
            points=md_to_html(draft['points']),
            eligibility=md_to_html(draft['eligibility']),
            detailed_sections=md_to_html(draft['detailed_sections']),
            timeline=md_to_html(draft['timeline']),
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
