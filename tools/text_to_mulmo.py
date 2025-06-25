#!/usr/bin/env python3
"""
台本テキストをmulmocastスクリプト形式に自動変換するツール
使用方法: python text_to_mulmo.py "台本テキスト" output_file.json [time_period]
"""

import json
import sys
import re
import os
from datetime import datetime

# 定数定義
DEFAULT_BEAT_DURATION = 17.0
MIN_BEATS = 5
MAX_BEATS = 9
TARGET_BEATS_RANGE = (7, 11)
MIN_SENTENCE_LENGTH = 5

# 挨拶文定数
MORNING_GREETING = "おはようございます。この動画では、忙しい朝にサクッと聞ける重要な投資・経済ニュースを1～2分でお届けします。毎日の習慣で投資知識と判断力を高めていきましょう。ぜひチャンネル登録・高評価、よろしくお願いします。"
EVENING_GREETING = "お疲れ様です。今日一日の重要な投資・経済ニュースを振り返り、明日の投資判断に役立つポイントを1～2分でお届けします。忙しい一日の終わりに、サクッと投資情報をチェックしていきましょう。ぜひチャンネル登録・高評価、よろしくお願いします。"
CLOSING_GREETING = "このチャンネルでは毎日重要ニュースをピックアップしてお届けしています。よろしければチャンネル登録と高評価をお願いいたします。"

# 固定画像設定候補パス
FIXED_IMAGE_CONFIG_PATHS = [
    "config/fixed_images_config.json",
    "../config/fixed_images_config.json",
    "fixed_images_config.json",
    "~/mulmocast/config/fixed_images_config.json",
    os.path.expanduser("~/mulmocast/config/fixed_images_config.json"),
    os.path.join(os.getcwd(), "config/fixed_images_config.json")
]

# 画像プロンプト生成用キーワード辞書
IMAGE_PROMPT_KEYWORDS = {
    'bank_japan': {
        'patterns': ['日銀', '金利', '利上げ', '物価', 'パーセント'],
        'prompt': "Bank of Japan building with economic charts showing interest rates and inflation data, professional financial graphics"
    },
    'currency': {
        'patterns': ['円高', '円安', 'ドル円', '為替'],
        'prompt': "Japanese yen currency symbols with upward arrow, interest rate charts, financial market data visualization"
    },
    'geopolitical': {
        'patterns': ['中東', 'イスラエル', 'イラン', '原油'],
        'prompt': "Middle East map with oil price charts showing upward trend, stock market graphs with red and green indicators"
    },
    'risk_management': {
        'patterns': ['エネルギー', '地政学', 'リスク', '分散'],
        'prompt': "portfolio diversification chart showing stocks and bonds correlation during geopolitical risk, warning indicators"
    },
    'economic_indicators': {
        'patterns': ['CPI', 'インフレ', '総務省'],
        'prompt': "USD/JPY currency exchange rate chart showing 145.23 level, Japanese yen strengthening against US dollar"
    },
    'investment_strategy': {
        'patterns': ['リバランス', 'NISA', '利益確定'],
        'prompt': "portfolio rebalancing illustration with Japanese assets and NISA investment account graphics, profit-taking strategies"
    },
    'summary': {
        'patterns': ['ポイント', '整理', '①', '②', '③', 'まとめ'],
        'prompt': "summary infographic with three key points, checklist format, portfolio risk management visualization"
    },
    'stock_market': {
        'patterns': ['株', '株式', '日経', 'ダウ', 'NASDAQ'],
        'prompt': "stock market graphs with red and green indicators, trading screens, financial data visualization"
    }
}

def load_fixed_images_config():
    """固定画像設定を読み込み"""
    for config_file in FIXED_IMAGE_CONFIG_PATHS:
        expanded_path = os.path.expanduser(config_file)
        if os.path.exists(expanded_path):
            try:
                with open(expanded_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✅ 固定画像設定を読み込みました: {expanded_path}")
                    return config
            except Exception as e:
                print(f"⚠️  設定ファイル読み込みエラー: {e}")
                continue
    return None

def get_greeting_text(time_period):
    """時間帯に応じた挨拶文を取得"""
    if time_period == "evening":
        return EVENING_GREETING
    else:
        return MORNING_GREETING

def create_fixed_image_config(fixed_images, image_type):
    """固定画像の設定オブジェクトを作成"""
    image_key = f"{image_type}_image"
    return {
        "type": "image",
        "source": {
            "kind": "path",
            "path": fixed_images.get(image_key)
        }
    }

def get_default_image_prompts():
    """デフォルト画像プロンプトを取得"""
    return {
        "opening": "professional news studio background with financial charts and graphs, morning news setting, clean and modern design",
        "closing": "YouTube channel subscribe button and like button with financial news channel branding, call-to-action graphics"
    }

def prepare_main_content(text, opening_greeting, closing_greeting):
    """台本から挨拶文を除去して本文のみを抽出"""
    main_content = text.strip()
    main_content = main_content.replace(opening_greeting, "").strip()
    main_content = main_content.replace(closing_greeting, "").strip()
    return main_content

def split_text_into_sentences(text):
    """テキストを文単位で分割"""
    sentences = re.split(r'(?<![0-9])。', text)
    sentences = [s.strip() + '。' for s in sentences if s.strip() and len(s.strip()) > MIN_SENTENCE_LENGTH]
    
    # 最後の文の重複した。を修正
    if sentences:
        sentences[-1] = sentences[-1].replace('。。', '。')
    
    return sentences

def combine_sentences(sentences, target_beats):
    """文が多すぎる場合に文を結合"""
    combined_sentences = []
    chunk_size = len(sentences) // target_beats + 1
    
    for i in range(0, len(sentences), chunk_size):
        chunk = sentences[i:i+chunk_size]
        combined_text = "".join(chunk).replace('。。', '。')
        combined_sentences.append(combined_text)
    
    return combined_sentences[:target_beats]

def split_long_sentences(sentences):
    """長い文を分割"""
    new_sentences = []
    for sentence in sentences:
        if len(sentence) > 100:
            parts = re.split(r'[、,]', sentence)
            if len(parts) > 1:
                mid = len(parts) // 2
                part1 = "、".join(parts[:mid]) + "。"
                part2 = "、".join(parts[mid:])
                new_sentences.extend([part1, part2])
            else:
                new_sentences.append(sentence)
        else:
            new_sentences.append(sentence)
    return new_sentences[:MAX_BEATS]

def adjust_beats_count(sentences):
    """beats数を目標範囲（7-11）に調整"""
    target_main_beats = min(max(len(sentences), MIN_BEATS), MAX_BEATS)
    
    if len(sentences) > target_main_beats:
        # 文が多すぎる場合は結合
        return combine_sentences(sentences, target_main_beats)
    elif len(sentences) < MIN_BEATS:
        # 文が少なすぎる場合は分割
        return split_long_sentences(sentences)
    
    return sentences

def generate_image_prompt(text):
    """文章の内容に基づいて画像プロンプトを生成"""
    for category, config in IMAGE_PROMPT_KEYWORDS.items():
        if any(word in text for word in config['patterns']):
            return config['prompt']
    
    return "professional financial news graphics, clean modern design"

def create_beat_config(speaker, text, image_config=None, image_prompt=None):
    """beat設定オブジェクトを作成"""
    beat = {
        "speaker": speaker,
        "text": text.strip()
    }
    
    if image_config:
        beat["image"] = image_config
    elif image_prompt:
        beat["imagePrompt"] = image_prompt
    
    return beat

def create_mulmocast_script_structure(title="投資・経済ニュース - 朝の重要ポイント"):
    """mulmocastスクリプトの基本構造を作成"""
    return {
        "$mulmocast": {
            "version": "1.0"
        },
        "title": title,
        "description": "忙しい朝にサクッと聞ける重要な投資・経済ニュースを1～2分でお届け",
        "lang": "ja",
        "speechParams": {
            "speakers": {
                "Presenter": {
                    "voiceId": "shimmer",
                    "displayName": {
                        "ja": "プレゼンター"
                    }
                }
            }
        },
        "imageParams": {
            "style": "professional financial news graphics"
        },
        "beats": []
    }

def add_opening_beat(script, opening_greeting, fixed_images):
    """オープニングbeatを追加"""
    if fixed_images:
        image_config = create_fixed_image_config(fixed_images, "opening")
        beat = create_beat_config("Presenter", opening_greeting, image_config=image_config)
    else:
        default_prompts = get_default_image_prompts()
        beat = create_beat_config("Presenter", opening_greeting, image_prompt=default_prompts["opening"])
    
    script["beats"].append(beat)

def add_main_content_beats(script, sentences):
    """本文のbeatsを追加"""
    for sentence in sentences:
        if sentence.strip():
            image_prompt = generate_image_prompt(sentence)
            beat = create_beat_config("Presenter", sentence, image_prompt=image_prompt)
            script["beats"].append(beat)

def add_closing_beat(script, closing_greeting, fixed_images):
    """クロージングbeatを追加"""
    if fixed_images:
        image_config = create_fixed_image_config(fixed_images, "closing")
        beat = create_beat_config("Presenter", closing_greeting, image_config=image_config)
    else:
        default_prompts = get_default_image_prompts()
        beat = create_beat_config("Presenter", closing_greeting, image_prompt=default_prompts["closing"])
    
    script["beats"].append(beat)

def print_generation_summary(output_file, total_beats, fixed_images):
    """生成結果のサマリーを出力"""
    print(f"✅ mulmocastスクリプトを生成しました: {output_file}")
    print(f"📊 総beats数: {total_beats} (目標範囲: {TARGET_BEATS_RANGE[0]}-{TARGET_BEATS_RANGE[1]})")
    print(f"🎬 構成: オープニング(1) + 本文({total_beats-2}) + クロージング(1)")
    
    if fixed_images:
        print(f"💰 Token節約: 固定画像2枚を再利用（API呼び出しなし）")
    else:
        print(f"💡 Token節約を有効にするには setup_fixed_images.py を実行してください")
    
    # beats数の警告
    if total_beats < TARGET_BEATS_RANGE[0]:
        print(f"⚠️  警告: beats数が少なすぎます ({total_beats} < {TARGET_BEATS_RANGE[0]})")
    elif total_beats > TARGET_BEATS_RANGE[1]:
        print(f"⚠️  警告: beats数が多すぎます ({total_beats} > {TARGET_BEATS_RANGE[1]})")
    else:
        print(f"✅ beats数が適切な範囲内です")

def text_to_mulmo_script(text, output_file=None, time_period="morning"):
    """台本テキストをmulmocastスクリプト形式に変換"""
    
    # 固定画像設定を読み込み
    fixed_images = load_fixed_images_config()
    
    if fixed_images:
        print("💰 Token節約モード: 固定画像を再利用します")
    else:
        print("⚠️  固定画像設定が見つかりません。初回生成モードで動作します")
        print("💡 setup_fixed_images.py を実行してtoken節約を有効にしてください")
    
    # 挨拶文を取得
    opening_greeting = get_greeting_text(time_period)
    closing_greeting = CLOSING_GREETING
    
    # 台本から挨拶文を除去して本文のみを抽出
    main_content = prepare_main_content(text, opening_greeting, closing_greeting)
    
    # 台本を文単位で分割
    sentences = split_text_into_sentences(main_content)
    
    # beats数調整
    sentences = adjust_beats_count(sentences)
    
    # mulmocastスクリプト構造を作成
    script = create_mulmocast_script_structure()
    
    # 1. オープニングbeat追加
    add_opening_beat(script, opening_greeting, fixed_images)
    
    # 2. 本文のbeats追加
    add_main_content_beats(script, sentences)
    
    # 3. クロージングbeat追加
    add_closing_beat(script, closing_greeting, fixed_images)
    
    # ファイル出力
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"news_script_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    
    total_beats = len(script["beats"])
    print_generation_summary(output_file, total_beats, fixed_images)
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("使用方法: python text_to_mulmo.py '台本テキスト' [output_file.json] [time_period]")
        print("time_period: 'morning'(朝用・デフォルト) または 'evening'(夜用)")
        sys.exit(1)
    
    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    time_period = sys.argv[3] if len(sys.argv) > 3 else "morning"
    
    # time_periodの値をチェック
    if time_period not in ["morning", "evening"]:
        print(f"⚠️  警告: 不正な時間帯指定 '{time_period}'。'morning'を使用します。")
        time_period = "morning"
    
    result_file = text_to_mulmo_script(text, output_file, time_period)
    print(f"🎬 次のコマンドで動画を生成できます:")
    print(f"cd ~/mulmocast && export PATH='/opt/homebrew/bin:$PATH' && mulmo movie {result_file} -l ja -c ja")

if __name__ == "__main__":
    main() 