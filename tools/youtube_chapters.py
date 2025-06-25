#!/usr/bin/env python3
"""
mulmocast動画からYouTube用目次（チャプター）を自動生成するツール（改善版）
使用方法: python youtube_chapters.py studio_file.json [output_dir] [base_name]
"""

import json
import sys
import os
from datetime import datetime

# 定数定義
DEFAULT_BEAT_DURATION = 17.0
MIN_SUMMARY_LENGTH = 100
MAX_SUMMARY_LENGTH = 120
FIXED_HASHTAGS = "#投資ニュース #経済ニュース #資産運用 #AI"
CHANNEL_URL = "https://www.youtube.com/@money_news_3min"

# チャプター名生成用キーワード辞書
CHAPTER_KEYWORDS = {
    '新NISA': {
        'patterns': ['新NISA', 'つみたて枠', '成長投資枠', '非課税', '制度2年目'],
        'specific': {
            ('88％', '56％'): "💼 新NISA利用状況（88％が活用）",
            ('平均積立額', '73万', '160万'): "📊 新NISA積立額の増加トレンド",
            ('自動積立', 'ボーナス月'): "⚡ 非課税枠完全活用の戦略"
        },
        'default': "💼 新NISA制度の活用状況"
    },
    '日銀': {
        'patterns': ['日銀', '議事要旨', '政策委員', '基調インフレ', '段階的利上げ'],
        'specific': {
            ('基調インフレ', '2％'): "💹 日銀議事要旨（段階的利上げ方針）",
            ('年内利上げ', '7割織り込'): "📈 市場の利上げ織り込み状況"
        },
        'default': "💹 日銀政策・金利動向"
    },
    '住宅ローン': {
        'patterns': ['住宅ローン', 'REIT', '固定化', '生活防衛費', '返済負担増'],
        'default': "🏠 住宅ローン対策（固定化検討）"
    },
    '為替': {
        'patterns': ['為替', '円高', '円安', '輸出株', 'ボラティリティ'],
        'default': "💱 為替動向（円高進行の影響）"
    },
    'Microsoft': {
        'patterns': ['GAFAM', 'マイクロソフト', 'Azure AI', 'Copilot+PC'],
        'default': "🤖 Microsoft AI戦略（営業利益率最高）"
    },
    'Google': {
        'patterns': ['Google', 'Gemini', '広告検索'],
        'default': "🔍 Google Gemini戦略"
    },
    'Apple': {
        'patterns': ['Apple', 'トランプ関税', 'インド生産', '9億ドル'],
        'default': "🍎 Apple関税対策（インド生産転換）"
    },
    'AI戦略': {
        'patterns': ['AI競争力', '関税リスク', 'セクター分散'],
        'default': "💼 米国株投資戦略（AI vs 関税リスク）"
    },
    '地政学': {
        'patterns': ['中東', 'イスラエル', 'イラン', '原油'],
        'default': "🛢️ 地政学リスクと原油"
    },
    'リスク管理': {
        'patterns': ['エネルギー', '地政学', 'リスク', '分散'],
        'default': "⚖️ リスク管理のポイント"
    },
    '経済指標': {
        'patterns': ['CPI', 'インフレ', '総務省'],
        'default': "📊 経済指標の解説"
    },
    '投資戦略': {
        'patterns': ['リバランス', '利益確定', 'インデックス'],
        'default': "💼 投資戦略のアドバイス"
    },
    'まとめ': {
        'patterns': ['ポイント', '整理', '①', '②', '③', 'まとめ'],
        'default': "📝 重要ポイントまとめ"
    },
    '株式市場': {
        'patterns': ['株', '株式', '日経', 'ダウ', 'NASDAQ'],
        'default': "📈 株式市場の動向"
    }
}

# ハッシュタグ生成用キーワード
HASHTAG_KEYWORDS = {
    '#新NISA': ['新NISA', 'つみたて枠', '成長投資枠'],
    '#日銀': ['日銀', '議事要旨', '利上げ', '金利政策'],
    '#米国株': ['マイクロソフト', 'Google', 'Apple', 'GAFAM'],
    '#為替': ['為替', '円高', '円安', 'ドル円'],
    '#住宅ローン': ['住宅ローン', 'REIT', '不動産'],
    '#地政学リスク': ['中東', 'イスラエル', 'イラン', '地政学'],
    '#金利': ['金利', '利上げ', '利下げ', '政策金利'],
    '#インデックス投資': ['インデックス', 'S&P500', 'オルカン', 'リバランス']
}

def seconds_to_timestamp(seconds):
    """秒をYouTube用タイムスタンプ（MM:SS）に変換"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def load_studio_data(studio_file):
    """studio.jsonファイルを読み込んでデータを検証"""
    if not os.path.exists(studio_file):
        print(f"❌ ファイルが見つかりません: {studio_file}")
        return None
    
    try:
        with open(studio_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return None
    
    # データ構造の検証
    if 'beats' not in data:
        print("❌ beats時間情報が見つかりません")
        return None
    
    if 'script' not in data or 'beats' not in data['script']:
        print("❌ script beats情報が見つかりません")
        return None
    
    beats_data = data['beats']
    script_beats = data['script']['beats']
    
    if len(beats_data) != len(script_beats):
        print(f"⚠️  警告: beat数が一致しません (時間データ: {len(beats_data)}, テキストデータ: {len(script_beats)})")
        return None
    
    return data

def find_matching_chapter_category(text):
    """テキストから最適なチャプターカテゴリを見つける"""
    for category, config in CHAPTER_KEYWORDS.items():
        if any(word in text for word in config['patterns']):
            # 特定パターンのチェック
            if 'specific' in config:
                for specific_patterns, chapter_name in config['specific'].items():
                    if any(pattern in text for pattern in specific_patterns):
                        return chapter_name
            return config['default']
    return None

def generate_smart_chapter_name(text, index):
    """実際のテキスト内容からより具体的なチャプター名を生成"""
    chapter_name = find_matching_chapter_category(text)
    
    if chapter_name:
        return chapter_name
    
    # どのカテゴリにも当てはまらない場合
    keywords = extract_keywords(text)
    if keywords:
        return f"📰 {keywords[0]}について"
    else:
        return f"📰 ニュース解説 {index}"

def extract_keywords(text):
    """テキストから重要なキーワードを抽出"""
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
    
    return found_keywords[:2]

def generate_chapters_from_beats(beats_data, script_beats):
    """beatsデータからチャプターリストを生成"""
    chapters = []
    current_time = 0.0
    used_chapter_names = set()
    
    for i, (beat_time, beat_text) in enumerate(zip(beats_data, script_beats)):
        duration = beat_time.get('duration', DEFAULT_BEAT_DURATION)
        
        # OP（最初）・ED（最後）のチャプターをスキップ
        if i == 0 or i == len(script_beats) - 1:
            current_time += duration
            continue
        
        # チャプター名を決定
        text = beat_text.get('text', '')
        chapter_name = generate_smart_chapter_name(text, i)
        
        # 重複チャプター名をチェック・統合
        if chapter_name in used_chapter_names:
            current_time += duration
            continue
        
        used_chapter_names.add(chapter_name)
        
        # タイムスタンプとチャプター追加
        timestamp = seconds_to_timestamp(current_time)
        chapters.append(f"{timestamp} {chapter_name}")
        
        current_time += duration
    
    return chapters

def print_chapter_debug_info(beats_data, script_beats, chapters):
    """チャプター時間計算のデバッグ情報を出力"""
    print(f"🕐 チャプター時間計算:")
    current_debug_time = 0.0
    chapter_index = 0
    
    for i, (beat_time, beat_text) in enumerate(zip(beats_data, script_beats)):
        duration = beat_time.get('duration', DEFAULT_BEAT_DURATION)
        
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

def generate_youtube_chapters(studio_file):
    """studio.jsonからYouTube用チャプターを生成"""
    data = load_studio_data(studio_file)
    if data is None:
        return None
    
    beats_data = data['beats']
    script_beats = data['script']['beats']
    
    # チャプター生成
    chapters = generate_chapters_from_beats(beats_data, script_beats)
    
    # 総動画時間計算
    total_duration = sum(beat.get('duration', DEFAULT_BEAT_DURATION) for beat in beats_data)
    
    # デバッグ情報出力
    print_chapter_debug_info(beats_data, script_beats, chapters)
    
    return chapters, total_duration

def extract_all_text_from_beats(studio_data):
    """スタジオデータから全テキストを抽出"""
    if 'script' in studio_data and 'beats' in studio_data['script']:
        beats = studio_data['script']['beats']
        return ' '.join([beat.get('text', '') for beat in beats])
    return ""

def generate_topic_list(all_text):
    """テキストから主要トピックリストを生成"""
    topics = []
    
    # 新NISA関連
    if any(word in all_text for word in ['新NISA', 'つみたて枠', '成長投資枠']):
        if '88％' in all_text or '利用状況' in all_text:
            topics.append('新NISA利用状況88％')
        elif '平均積立額' in all_text or '73万' in all_text:
            topics.append('新NISA積立額増加')
        else:
            topics.append('新NISA活用法')
    
    # 日銀・金利関連
    if any(word in all_text for word in ['日銀', '議事要旨', '利上げ', '金利']):
        topics.append('日銀段階的利上げ')
    
    # 米国株・AI関連
    if any(word in all_text for word in ['マイクロソフト', 'Azure', 'Copilot']):
        topics.append('Microsoft AI戦略')
    elif any(word in all_text for word in ['Google', 'Gemini']):
        topics.append('Google AI戦略')
    elif any(word in all_text for word in ['Apple', 'トランプ関税', 'インド生産']):
        topics.append('Apple関税対策')
    elif any(word in all_text for word in ['GAFAM', 'AI競争']):
        topics.append('米国株AI戦略')
    
    # その他のトピック
    if any(word in all_text for word in ['為替', '円高', '円安']):
        topics.append('為替動向')
    if any(word in all_text for word in ['住宅ローン', 'REIT', '固定化']):
        topics.append('住宅ローン対策')
    if any(word in all_text for word in ['中東', 'イスラエル', 'イラン', '地政学']):
        topics.append('地政学リスク')
    
    return topics

def generate_video_summary(studio_data):
    """スタジオデータから100-120文字の動画要約を生成"""
    try:
        all_text = extract_all_text_from_beats(studio_data)
        if not all_text:
            return "今日の重要な投資・経済ニュースを3分で解説。新NISA、日銀政策、米国株、為替動向など投資判断に必要な情報をお届けします。"
        
        topics = generate_topic_list(all_text)
        
        # 要約文を生成
        if topics:
            topic_str = '・'.join(topics[:3])  # 最大3つまで
            summary = f"今日の重要投資ニュース：{topic_str}など。投資判断に必要な最新情報を3分で解説します。"
        else:
            summary = "今日の重要な投資・経済ニュースを3分で解説。最新の市場動向と投資判断に必要な情報をお届けします。"
        
        # 文字数調整
        if len(summary) > MAX_SUMMARY_LENGTH:
            summary = summary[:117] + "..."
        elif len(summary) < MIN_SUMMARY_LENGTH:
            summary += "毎朝の投資情報収集にお役立てください。"
        
        return summary
        
    except Exception as e:
        return "今日の重要な投資・経済ニュースを3分で解説。新NISA、日銀政策、米国株、為替動向など投資判断に必要な情報をお届けします。"

def generate_dynamic_hashtags(studio_data):
    """ニュース内容から動的にハッシュタグを2つ生成"""
    try:
        all_text = extract_all_text_from_beats(studio_data)
        if not all_text:
            return " #新NISA #日銀"
        
        hashtags = []
        
        for hashtag, keywords in HASHTAG_KEYWORDS.items():
            if any(word in all_text for word in keywords):
                hashtags.append(hashtag)
        
        # 2つ選択（重複排除）
        unique_hashtags = list(dict.fromkeys(hashtags))
        selected_hashtags = unique_hashtags[:2]
        
        # 2つに満たない場合はデフォルトで補完
        if len(selected_hashtags) < 2:
            defaults = ['#新NISA', '#日銀', '#米国株', '#為替']
            for default in defaults:
                if default not in selected_hashtags:
                    selected_hashtags.append(default)
                    if len(selected_hashtags) >= 2:
                        break
        
        return ' ' + ' '.join(selected_hashtags)
        
    except Exception as e:
        return " #新NISA #日銀"

def create_youtube_description(chapters, video_title, studio_data):
    """YouTube用の説明文を生成"""
    summary = generate_video_summary(studio_data)
    dynamic_hashtags = generate_dynamic_hashtags(studio_data)
    
    description = f"""📺 {summary}

📋 目次（チャプター）:
"""
    
    for chapter in chapters:
        description += f"{chapter}\n"
    
    description += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

💡 このチャンネルについて
忙しい朝にサクッと聞ける重要な投資・経済ニュースを毎日お届けしています。
投資知識と判断力を日々の習慣で高めていきましょう！

🔔 チャンネル登録・高評価をお願いします！
📌 {CHANNEL_URL}

{FIXED_HASHTAGS}{dynamic_hashtags}
"""
    
    return description

def find_latest_studio_file():
    """最新のstudio.jsonファイルを自動検索"""
    if os.path.exists("output"):
        studio_files = [f for f in os.listdir("output") if f.endswith('_studio.json')]
        if studio_files:
            studio_files.sort(reverse=True)
            studio_file = os.path.join("output", studio_files[0])
            print(f"📁 最新のstudio.jsonを使用: {studio_file}")
            return studio_file
    return None

def main():
    if len(sys.argv) < 2:
        print("使用方法: python youtube_chapters.py studio_file.json [output_dir] [base_name]")
        sys.exit(1)
    
    studio_file = sys.argv[1]
    
    # 出力ディレクトリとベース名を引数から取得
    output_dir = sys.argv[2] if len(sys.argv) >= 3 else "output/movie"
    
    if len(sys.argv) >= 4:
        base_name = sys.argv[3]
    else:
        base_name = os.path.splitext(os.path.basename(studio_file))[0].replace('_studio', '')
    
    # studio.jsonファイルが見つからない場合、最新のものを自動検索
    if not os.path.exists(studio_file):
        found_file = find_latest_studio_file()
        if found_file:
            studio_file = found_file
        else:
            print("❌ studio.jsonファイルが見つかりません")
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
    
    # スタジオデータを取得
    try:
        with open(studio_file, 'r', encoding='utf-8') as f:
            studio_data = json.load(f)
        if 'script' in studio_data:
            video_title = studio_data['script'].get('title', '投資・経済ニュース - 朝の重要ポイント')
        else:
            video_title = studio_data.get('title', '投資・経済ニュース - 朝の重要ポイント')
    except:
        video_title = '投資・経済ニュース - 朝の重要ポイント'
        studio_data = {}
    
    # 出力ファイル名を生成
    chapters_file = os.path.join(output_dir, f"{base_name}_youtube_chapters.txt")
    description_file = os.path.join(output_dir, f"{base_name}_youtube_description.txt")
    
    # チャプター一覧を出力
    with open(chapters_file, 'w', encoding='utf-8') as f:
        for chapter in chapters:
            f.write(chapter + '\n')
    
    # YouTube説明文を出力
    description = create_youtube_description(chapters, video_title, studio_data)
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
