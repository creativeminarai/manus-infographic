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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Noto Sans JP', sans-serif; background-color: #f1f5f9; color: #1e293b; }}
        .gradient-bg {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }}
        .card {{ background: white; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; }}
        .section-title {{ border-left: 4px solid #3b82f6; padding-left: 1rem; margin-bottom: 1.5rem; font-weight: 700; color: #1e3a8a; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; }}
        .badge-blue {{ background-color: #dbeafe; color: #1e40af; }}
        .badge-green {{ background-color: #dcfce7; color: #166534; }}
        .badge-orange {{ background-color: #ffedd5; color: #9a3412; }}
        .prose li {{ margin-bottom: 0.5rem; }}
    </style>
</head>
<body class="py-8 px-4 md:px-0">
    <div class="max-w-5xl mx-auto">
        <!-- Header -->
        <header class="gradient-bg rounded-2xl p-8 mb-8 text-white shadow-lg relative overflow-hidden">
            <div class="relative z-10">
                <div class="flex items-center gap-3 mb-4">
                    <span class="badge badge-blue bg-white/20 text-white border border-white/30">資料要約</span>
                    <span class="text-white/80 text-sm">Update: 2026.01.30</span>
                </div>
                <h1 class="text-3xl md:text-4xl font-bold leading-tight mb-4">{title}</h1>
                <p class="text-blue-100 text-lg max-w-3xl">{summary_short}</p>
            </div>
            <i class="fas fa-file-pdf absolute -right-8 -bottom-8 text-9xl text-white/10 rotate-12"></i>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Left Column: Main Info -->
            <div class="lg:col-span-2 space-y-8">
                <!-- Overview Section -->
                <section class="card p-8">
                    <h2 class="section-title text-2xl">資料の概要</h2>
                    <div class="prose max-w-none text-slate-600 leading-relaxed">
                        {summary_long}
                    </div>
                </section>

                <!-- Key Points Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <section class="card p-6 border-t-4 border-t-green-500">
                        <h3 class="font-bold text-xl mb-4 flex items-center gap-2">
                            <i class="fas fa-check-circle text-green-500"></i> 重要ポイント
                        </h3>
                        <ul class="space-y-3 text-slate-600">
                            {points}
                        </ul>
                    </section>
                    <section class="card p-6 border-t-4 border-t-blue-500">
                        <h3 class="font-bold text-xl mb-4 flex items-center gap-2">
                            <i class="fas fa-bullseye text-blue-500"></i> 対象・要件
                        </h3>
                        <ul class="space-y-3 text-slate-600">
                            {eligibility}
                        </ul>
                    </section>
                </div>

                <!-- Detailed Content -->
                <section class="card p-8">
                    <h2 class="section-title text-2xl">詳細内容・解説</h2>
                    <div class="space-y-6">
                        {detailed_sections}
                    </div>
                </section>
            </div>

            <!-- Right Column: Sidebar -->
            <div class="space-y-8">
                <!-- Status/Timeline -->
                <section class="card p-6 bg-slate-50">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2 text-slate-800">
                        <i class="fas fa-calendar-alt text-orange-500"></i> 期限・スケジュール
                    </h3>
                    <div class="space-y-4">
                        {timeline}
                    </div>
                </section>

                <!-- Warnings -->
                <section class="card p-6 border-l-4 border-l-orange-500 bg-orange-50">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2 text-orange-800">
                        <i class="fas fa-exclamation-triangle"></i> 注意事項
                    </h3>
                    <ul class="space-y-3 text-orange-900/80 text-sm">
                        {warnings}
                    </ul>
                </section>

                <!-- Next Actions -->
                <section class="card p-6 bg-blue-50 border border-blue-100">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2 text-blue-800">
                        <i class="fas fa-rocket text-blue-600"></i> 次のアクション
                    </h3>
                    <div class="space-y-3">
                        {actions}
                    </div>
                </section>

                <!-- Metadata -->
                <div class="text-center p-4">
                    <a href="{original_url}" target="_blank" class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium transition-colors">
                        <i class="fas fa-external-link-alt"></i> 元資料を確認する
                    </a>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="mt-12 py-8 border-t border-slate-200 text-center text-slate-500 text-sm">
            <p>Generated by Manus Infographic System &copy; 2026</p>
            <p class="mt-1">この要約はAIによって生成されており、正確な情報は必ず元資料をご確認ください。</p>
        </footer>
    </div>
</body>
</html>
"""

def extract_text_from_pdf(pdf_path):
    try:
        result = subprocess.run(['pdftotext', '-l', '10', pdf_path, '-'], capture_output=True, text=True)
        return result.stdout[:8000]
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def generate_infographic_content(title, pdf_text):
    prompt = f"""
    以下の資料タイトルとPDFから抽出されたテキストに基づき、ビジネス向けの高度に構造化されたインフォグラフィックHTML用のコンテンツを生成してください。
    
    タイトル: {title}
    PDFテキスト抽出（一部）:
    {pdf_text}
    
    出力はJSON形式で以下のキーを厳守してください:
    - summary_short: 資料を一言で表すキャッチコピー的な要約（50文字以内）
    - summary_long: 資料の全体像を説明する詳細な概要（HTMLの<p>タグを使用）
    - points: 最も重要な3〜5つのポイント（HTMLの<li>タグ形式、各項目にFontAwesomeアイコンクラスは含めない）
    - eligibility: 補助対象者や申請要件（HTMLの<li>タグ形式）
    - detailed_sections: 資料の主要な章や項目ごとの詳細解説（HTML形式、<h3>と<p>を組み合わせて3つ以上作成）
    - timeline: 締切やスケジュール（HTML形式、<div>で各イベントを囲む）
    - warnings: 申請時の注意点や不備になりやすいポイント（HTMLの<li>タグ形式）
    - actions: 読者が次に取るべき具体的なステップ（HTML形式、チェックボックス付きのリストなど）
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": "あなたはプロフェッショナルなビジネスアナリストです。複雑な資料を分かりやすく構造化して要約するエキスパートです。必ず指定されたJSON形式で回答してください。"},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def main():
    if not os.path.exists(PROCESSED_FILE):
        return

    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed = json.load(f)

    for url, data in processed.items():
        print(f"Generating enhanced infographic for {data['text']}...")
        
        pdf_text = extract_text_from_pdf(data['local_path'])
        content = generate_infographic_content(data['text'], pdf_text)
        
        pdf_filename = os.path.basename(data['local_path'])
        html_filename = pdf_filename.replace('.pdf', '.html')
        html_path = os.path.join(INFOGRAPHIC_DIR, html_filename)
        
        html_content = HTML_TEMPLATE.format(
            title=data['text'],
            summary_short=content['summary_short'],
            summary_long=content['summary_long'],
            points=content['points'],
            eligibility=content['eligibility'],
            detailed_sections=content['detailed_sections'],
            timeline=content['timeline'],
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
