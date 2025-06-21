#!/usr/bin/env python3
"""
mulmocast動画からYouTube用目次（チャプター）を自動生成するツール（改善版）
使用方法: python youtube_chapters.py studio_file.json [output_dir] [base_name]
"""

import json
import sys
import os
from datetime import datetime

def seconds_to_timestamp(seconds):
    """秒をYouTube用タイムスタンプ（MM:SS）に変換"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def generate_youtube_chapters(studio_file):
    """studio.jsonからYouTube用チャプターを生成"""
    
    if not os.path.exists(studio_file):
        print(f"❌ ファイルが見つかりません: {studio_file}")
        return None
    
    try:
        with open(studio_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return None
    
    chapters = []
    current_time = 0.0
    used_chapter_names = set()  # 重複チェック用
    
    # studio.jsonから実際のbeat時間データを取得
    # 実際のbeat時間情報は'beats'キーに格納されている
    if 'beats' in data:
        beats_data = data['beats']
        # script情報も取得
        if 'script' in data and 'beats' in data['script']:
            script_beats = data['script']['beats']
        else:
            print("❌ script beats情報が見つかりません")
            return None
    else:
        print("❌ beats時間情報が見つかりません")
        return None
    
    # beat数の一致確認
    if len(beats_data) != len(script_beats):
        print(f"⚠️  警告: beat数が一致しません (時間データ: {len(beats_data)}, テキストデータ: {len(script_beats)})")
        return None
    
    for i, (beat_time, beat_text) in enumerate(zip(beats_data, script_beats)):
        # 実際の音声時間を取得（デフォルト17秒）
        duration = beat_time.get('duration', 17.0)
        
        # OP（最初）・ED（最後）のチャプターをスキップ
        if i == 0 or i == len(script_beats) - 1:
            current_time += duration
            continue
        
        # チャプター名を決定
        text = beat_text.get('text', '')
        chapter_name = generate_smart_chapter_name(text, i)
        
        # 重複チャプター名をチェック・統合
        if chapter_name in used_chapter_names:
            # 重複の場合は時間を加算してスキップ（統合）
            current_time += duration
            continue
        
        used_chapter_names.add(chapter_name)
        
        # タイムスタンプとチャプター追加
        timestamp = seconds_to_timestamp(current_time)
        chapters.append(f"{timestamp} {chapter_name}")
        
        # 実際の音声時間を加算
        current_time += duration
    
    # 総動画時間（全beatの時間を含む）
    total_duration = sum(beat.get('duration', 17.0) for beat in beats_data)
    
    # デバッグ情報を出力
    print(f"🕐 チャプター時間計算:")
    current_debug_time = 0.0
    chapter_index = 0
    
    for i, (beat_time, beat_text) in enumerate(zip(beats_data, script_beats)):
        duration = beat_time.get('duration', 17.0)
        
        if i == 0:
            print(f"  Beat {i+1}: {duration:.2f}秒 - [OP] スキップ")
        elif i == len(script_beats) - 1:
            print(f"  Beat {i+1}: {duration:.2f}秒 - [ED] スキップ")
        else:
            text = beat_text.get('text', '')
            chapter_name = generate_smart_chapter_name(text, i)
            
            if chapter_name not in [ch.split(' ', 1)[1] for ch in chapters[:chapter_index]]:
                if chapter_index < len(chapters):
                    print(f"  Beat {i+1}: {duration:.2f}秒 - {chapters[chapter_index]}")
                    chapter_index += 1
                else:
                    print(f"  Beat {i+1}: {duration:.2f}秒 - {seconds_to_timestamp(current_debug_time)} {chapter_name}")
            else:
                print(f"  Beat {i+1}: {duration:.2f}秒 - [重複] {chapter_name} 統合")
        
        current_debug_time += duration
    
    return chapters, total_duration

def generate_smart_chapter_name(text, index):
    """実際のテキスト内容からより具体的なチャプター名を生成"""
    
    # 新NISA関連
    if any(word in text for word in ['新NISA', 'つみたて枠', '成長投資枠', '非課税', '制度2年目']):
        if '88％' in text or '56％' in text:
            return "💼 新NISA利用状況（88％が活用）"
        elif '平均積立額' in text or '73万' in text or '160万' in text:
            return "📊 新NISA積立額の増加トレンド"
        elif '自動積立' in text or 'ボーナス月' in text:
            return "⚡ 非課税枠完全活用の戦略"
        else:
            return "💼 新NISA制度の活用状況"
    
    # 日銀・金利関連
    elif any(word in text for word in ['日銀', '議事要旨', '政策委員', '基調インフレ', '段階的利上げ']):
        if '基調インフレ' in text and '2％' in text:
            return "💹 日銀議事要旨（段階的利上げ方針）"
        elif '年内利上げ' in text or '7割織り込' in text:
            return "📈 市場の利上げ織り込み状況"
        else:
            return "💹 日銀政策・金利動向"
    
    # 住宅ローン・REIT関連
    elif any(word in text for word in ['住宅ローン', 'REIT', '固定化', '生活防衛費', '返済負担増']):
        return "🏠 住宅ローン対策（固定化検討）"
    
    # 為替関連
    elif any(word in text for word in ['為替', '円高', '円安', '輸出株', 'ボラティリティ']):
        return "💱 為替動向（円高進行の影響）"
    
    # GAFAM・AI関連
    elif any(word in text for word in ['GAFAM', 'マイクロソフト', 'Azure AI', 'Copilot+PC']):
        return "🤖 Microsoft AI戦略（営業利益率最高）"
    elif any(word in text for word in ['Google', 'Gemini', '広告検索']):
        return "🔍 Google Gemini戦略"
    elif any(word in text for word in ['Apple', 'トランプ関税', 'インド生産', '9億ドル']):
        return "🍎 Apple関税対策（インド生産転換）"
    elif any(word in text for word in ['AI競争力', '関税リスク', 'セクター分散']):
        return "💼 米国株投資戦略（AI vs 関税リスク）"
    
    # その他のキーワード
    elif any(word in text for word in ['中東', 'イスラエル', 'イラン', '原油']):
        return "🛢️ 地政学リスクと原油"
    elif any(word in text for word in ['エネルギー', '地政学', 'リスク', '分散']):
        return "⚖️ リスク管理のポイント"
    elif any(word in text for word in ['CPI', 'インフレ', '総務省']):
        return "📊 経済指標の解説"
    elif any(word in text for word in ['リバランス', '利益確定', 'インデックス']):
        return "💼 投資戦略のアドバイス"
    elif any(word in text for word in ['ポイント', '整理', '①', '②', '③', 'まとめ']):
        return "📝 重要ポイントまとめ"
    elif any(word in text for word in ['株', '株式', '日経', 'ダウ', 'NASDAQ']):
        return "📈 株式市場の動向"
    else:
        # テキストの最初の重要単語を抽出
        keywords = extract_keywords(text)
        if keywords:
            return f"📰 {keywords[0]}について"
        else:
            return f"📰 ニュース解説 {index}"

def extract_keywords(text):
    """テキストから重要なキーワードを抽出"""
    # 重要な単語を優先順位順に並べる
    important_words = [
        '新NISA', 'つみたて', '成長投資枠', '日銀', '利上げ', '金利', 
        'マイクロソフト', 'Google', 'Apple', 'AI', '為替', '円高', '円安',
        '住宅ローン', 'REIT', '関税', 'トランプ', 'インド生産',
        'セクター分散', 'インデックス', 'リバランス'
    ]
    
    found_keywords = []
    for word in important_words:
        if word in text:
            found_keywords.append(word)
    
    return found_keywords[:2]  # 最大2つまで

def create_youtube_description(chapters, video_title, total_duration):
    """YouTube用の説明文を生成"""
    
    description = f"""📺 {video_title}

🕐 総動画時間: {seconds_to_timestamp(total_duration)}

📋 目次（チャプター）:
"""
    
    for chapter in chapters:
        description += f"{chapter}\n"
    
    description += """
━━━━━━━━━━━━━━━━━━━━━━━━

💡 このチャンネルについて
忙しい朝にサクッと聞ける重要な投資・経済ニュースを毎日お届けしています。
投資知識と判断力を日々の習慣で高めていきましょう！

🔔 チャンネル登録・高評価をお願いします！
📌 ベルマークで通知もオンにしてください

#投資ニュース #経済ニュース #朝活 #投資初心者 #資産運用 #NISA #株式投資 #為替 #GAFAM #AI #日銀
"""
    
    return description

def main():
    if len(sys.argv) < 2:
        print("使用方法: python youtube_chapters.py studio_file.json [output_dir] [base_name]")
        sys.exit(1)
    
    studio_file = sys.argv[1]
    
    # 出力ディレクトリとベース名を引数から取得
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        output_dir = "output/movie"
    
    if len(sys.argv) >= 4:
        base_name = sys.argv[3]
    else:
        # studio.jsonファイル名からベース名を推測
        base_name = os.path.splitext(os.path.basename(studio_file))[0].replace('_studio', '')
    
    # studio.jsonファイルが見つからない場合、最新のものを自動検索
    if not os.path.exists(studio_file):
        # output/ディレクトリから最新のstudio.jsonを検索
        if os.path.exists("output"):
            studio_files = [f for f in os.listdir("output") if f.endswith('_studio.json')]
            if studio_files:
                # 最新のファイルを選択
                studio_files.sort(reverse=True)
                studio_file = os.path.join("output", studio_files[0])
                print(f"📁 最新のstudio.jsonを使用: {studio_file}")
            else:
                print("❌ studio.jsonファイルが見つかりません")
                sys.exit(1)
        else:
            print("❌ outputディレクトリが見つかりません")
            sys.exit(1)
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎬 YouTube目次生成中...")
    print(f"📁 入力ファイル: {studio_file}")
    print(f"📁 出力ディレクトリ: {output_dir}")
    print(f"📄 ベースファイル名: {base_name}")
    
    result = generate_youtube_chapters(studio_file)
    if result is None:
        sys.exit(1)
    
    chapters, total_duration = result
    
    # 動画タイトルを生成（studio.jsonから取得）
    try:
        with open(studio_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'script' in data:
            video_title = data['script'].get('title', '投資・経済ニュース - 朝の重要ポイント')
        else:
            video_title = data.get('title', '投資・経済ニュース - 朝の重要ポイント')
    except:
        video_title = '投資・経済ニュース - 朝の重要ポイント'
    
    # 出力ファイル名を生成（新しい命名規則）
    chapters_file = os.path.join(output_dir, f"{base_name}_youtube_chapters.txt")
    description_file = os.path.join(output_dir, f"{base_name}_youtube_description.txt")
    
    # チャプター一覧を出力
    with open(chapters_file, 'w', encoding='utf-8') as f:
        for chapter in chapters:
            f.write(chapter + '\n')
    
    # YouTube説明文を出力
    description = create_youtube_description(chapters, video_title, total_duration)
    with open(description_file, 'w', encoding='utf-8') as f:
        f.write(description)
    
    print(f"✅ YouTube目次を生成しました!")
    print(f"📋 チャプター一覧: {chapters_file}")
    print(f"📝 YouTube説明文: {description_file}")
    print(f"🕐 総動画時間: {seconds_to_timestamp(total_duration)}")
    print(f"📊 チャプター数: {len(chapters)}")
    
    print(f"\n📋 生成されたチャプター:")
    for chapter in chapters:
        print(f"  {chapter}")
    
    print(f"\n💡 使い方:")
    print(f"1. YouTubeの動画説明欄に {description_file} の内容をコピー")
    print(f"2. または手動で以下のチャプターを説明欄に追加:")
    for chapter in chapters:
        print(f"   {chapter}")

if __name__ == "__main__":
    main()
