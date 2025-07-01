#!/usr/bin/env python3
"""
台本テキストをmulmocastスクリプト形式に自動変換するツール（スマートPexels統合版）
使用方法: python text_to_mulmo_with_smart_pexels.py "台本テキスト" [output_file.json] [time_period] [--use-smart-pexels]
"""

import json
import sys
import re
import os
from datetime import datetime
from smart_pexels_fetcher import SmartPexelsImageFetcher

# 定数定義
DEFAULT_BEAT_DURATION = 17.0
MIN_BEATS = 7
MAX_BEATS = 11
TARGET_BEATS_RANGE = (7, 11)
MIN_SENTENCE_LENGTH = 3

# 挨拶文定数（テック系用に更新）
TECH_MORNING_GREETING = "おはようございます。今日の重要なテクノロジーニュースを1〜2分でお届けします。最新の技術動向をチェックして、デジタル時代を生き抜く知識を身につけていきましょう。ぜひチャンネル登録・高評価、よろしくお願いします。"
TECH_EVENING_GREETING = "お疲れ様です。今日のテック業界の重要ニュースを振り返り、明日のトレンドを先取りしていきましょう。忙しい一日の終わりに、サクッとテック情報をチェックしてください。ぜひチャンネル登録・高評価、よろしくお願いします。"
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

# テック系画像プロンプト生成用キーワード辞書
TECH_IMAGE_PROMPT_KEYWORDS = {
    'apple': {
        'patterns': ['Apple', 'iPhone', 'iPad', 'Mac', 'iOS', 'アップル', 'Siri'],
        'prompt': "Apple headquarters building, iPhone devices, modern technology, sleek design"
    },
    'meta': {
        'patterns': ['Meta', 'Facebook', 'Instagram', 'WhatsApp', 'メタ'],
        'prompt': "Meta headquarters, social media platforms, virtual reality, modern office"
    },
    'openai': {
        'patterns': ['OpenAI', 'ChatGPT', 'GPT', 'オープンAI'],
        'prompt': "OpenAI office, artificial intelligence, ChatGPT interface, modern AI technology"
    },
    'anthropic': {
        'patterns': ['Anthropic', 'Claude', 'アンソロピック'],
        'prompt': "Anthropic AI company, Claude AI assistant, artificial intelligence research"
    },
    'cloudflare': {
        'patterns': ['Cloudflare', 'クラウドフレア'],
        'prompt': "Cloudflare data center, web security, internet infrastructure, cloud computing"
    },
    'ai_technology': {
        'patterns': ['AI', '人工知能', '機械学習', '大規模言語モデル', 'LLM'],
        'prompt': "artificial intelligence, neural networks, machine learning, futuristic technology"
    },
    'voice_assistant': {
        'patterns': ['音声アシスタント', 'Siri', '音声認識'],
        'prompt': "voice assistant technology, smart speaker, speech recognition, AI voice interface"
    },
    'web_security': {
        'patterns': ['ウェブサイト', 'セキュリティ', 'スクレイピング', 'ボット'],
        'prompt': "web security, cybersecurity shield, website protection, data security"
    },
    'gpu_computing': {
        'patterns': ['GPU', 'クラスタ', 'コンピューティング'],
        'prompt': "GPU cluster, high performance computing, data center servers, AI computing"
    },
    'ecosystem': {
        'patterns': ['エコシステム', '収益モデル', 'プラットフォーム'],
        'prompt': "business ecosystem, platform economy, digital transformation, interconnected systems"
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
        return TECH_EVENING_GREETING
    else:
        return TECH_MORNING_GREETING

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

def create_pexels_image_config(image_path):
    """Pexels画像の設定オブジェクトを作成"""
    return {
        "type": "image",
        "source": {
            "kind": "path",
            "path": image_path
        }
    }

def get_default_image_prompts():
    """デフォルト画像プロンプトを取得"""
    return {
        "opening": "professional tech news studio background with digital screens and technology graphics, modern design",
        "closing": "YouTube channel subscribe button and like button with tech news channel branding, call-to-action graphics"
    }

def prepare_main_content(text, opening_greeting, closing_greeting):
    """台本から挨拶文を除去して本文のみを抽出"""
    main_content = text.strip()
    main_content = main_content.replace(opening_greeting, "").strip()
    main_content = main_content.replace(closing_greeting, "").strip()
    return main_content

def split_text_into_sentences(text):
    """テキストを文単位で分割（より細かく分割）"""
    # より詳細な文分割（複数の区切り文字に対応）
    sentences = re.split(r'[。！？]', text)
    sentences = [s.strip() + '。' for s in sentences if s.strip() and len(s.strip()) > MIN_SENTENCE_LENGTH]
    
    # さらに細かく分割するための追加処理
    refined_sentences = []
    for sentence in sentences:
        # 長い文（100文字以上）をさらに分割
        if len(sentence) > 100:
            # 複数の区切り文字で分割
            parts = re.split(r'[、,また次に最後にさらに例えば]', sentence)
            if len(parts) > 1:
                for i, part in enumerate(parts):
                    if part.strip():
                        if i == len(parts) - 1:
                            refined_sentences.append(part.strip())
                        else:
                            refined_sentences.append(part.strip() + '。')
            else:
                refined_sentences.append(sentence)
        else:
            refined_sentences.append(sentence)
    
    # 最後の文の重複した。を修正
    if refined_sentences:
        refined_sentences[-1] = refined_sentences[-1].replace('。。', '。')
    
    return [s for s in refined_sentences if len(s.strip()) > MIN_SENTENCE_LENGTH]

def combine_sentences(sentences, target_beats):
    """文が多すぎる場合に文を結合"""
    if len(sentences) <= target_beats:
        return sentences
    
    combined_sentences = []
    chunk_size = max(1, len(sentences) // target_beats)
    
    for i in range(0, len(sentences), chunk_size):
        chunk = sentences[i:i+chunk_size]
        combined_text = "".join(chunk).replace('。。', '。')
        combined_sentences.append(combined_text)
    
    return combined_sentences[:target_beats]

def split_long_sentences(sentences):
    """長い文を分割（より積極的に分割）"""
    new_sentences = []
    for sentence in sentences:
        if len(sentence) > 80:  # より短い基準で分割
            # 複数の区切り文字で分割
            parts = re.split(r'[、,また次に最後にさらに例えばそして]', sentence)
            if len(parts) > 1:
                mid = len(parts) // 2
                part1 = "、".join(parts[:mid]) + "。"
                part2 = "、".join(parts[mid:])
                if len(part2.strip()) > MIN_SENTENCE_LENGTH:
                    new_sentences.extend([part1, part2])
                else:
                    new_sentences.append(sentence)
            else:
                new_sentences.append(sentence)
        else:
            new_sentences.append(sentence)
    return new_sentences

def adjust_beats_count(sentences):
    """beats数を目標範囲（7-11）に調整"""
    print(f"📝 初期文数: {len(sentences)}")
    
    # まず長い文を分割
    sentences = split_long_sentences(sentences)
    print(f"📝 分割後文数: {len(sentences)}")
    
    # 目標範囲内に調整
    if len(sentences) > MAX_BEATS:
        # 文が多すぎる場合は結合
        sentences = combine_sentences(sentences, MAX_BEATS)
        print(f"📝 結合後文数: {len(sentences)}")
    elif len(sentences) < MIN_BEATS:
        # 文が少なすぎる場合はさらに分割
        additional_sentences = []
        for sentence in sentences:
            if len(sentence) > 60:  # さらに短い基準で分割
                parts = re.split(r'[、,]', sentence)
                if len(parts) >= 2:
                    mid = len(parts) // 2
                    part1 = "、".join(parts[:mid]) + "。"
                    part2 = "、".join(parts[mid:])
                    additional_sentences.extend([part1, part2])
                else:
                    additional_sentences.append(sentence)
            else:
                additional_sentences.append(sentence)
        sentences = additional_sentences
        print(f"📝 追加分割後文数: {len(sentences)}")
    
    # 最終的に目標範囲内に収める（厳密に）
    if len(sentences) > MAX_BEATS:
        # 強制的にMAX_BEATSに制限
        sentences = sentences[:MAX_BEATS]
        print(f"📝 上限調整後文数: {len(sentences)}")
    elif len(sentences) < MIN_BEATS:
        # 不足分を最後の文から分割して補完
        while len(sentences) < MIN_BEATS and sentences:
            last_sentence = sentences[-1]
            if len(last_sentence) > 30:
                # 最後の文を2つに分割
                mid = len(last_sentence) // 2
                # 句読点で分割位置を調整
                for i in range(mid-10, mid+10):
                    if i > 0 and i < len(last_sentence) and last_sentence[i] in '、,':
                        mid = i + 1
                        break
                
                part1 = last_sentence[:mid].strip() + "。"
                part2 = last_sentence[mid:].strip()
                if len(part2) > MIN_SENTENCE_LENGTH:
                    sentences[-1] = part1
                    sentences.append(part2)
                    print(f"📝 最終分割: {len(sentences)}文に調整")
                else:
                    break
            else:
                # 分割できない場合は、前の文を分割
                if len(sentences) >= 2:
                    prev_sentence = sentences[-2]
                    if len(prev_sentence) > 40:
                        mid = len(prev_sentence) // 2
                        for i in range(mid-5, mid+5):
                            if i > 0 and i < len(prev_sentence) and prev_sentence[i] in '、,':
                                mid = i + 1
                                break
                        
                        part1 = prev_sentence[:mid].strip() + "。"
                        part2 = prev_sentence[mid:].strip() + "。"
                        sentences[-2] = part1
                        sentences.insert(-1, part2)
                        print(f"📝 前文分割: {len(sentences)}文に調整")
                    else:
                        break
                else:
                    break
    
    # 最終確認
    final_count = len(sentences)
    if final_count < MIN_BEATS or final_count > MAX_BEATS:
        print(f"⚠️  警告: beats数調整が目標範囲外です ({final_count})")
    else:
        print(f"✅ beats数が目標範囲内に調整されました ({final_count})")
    
    return sentences

def generate_image_prompt(text):
    """文章の内容に基づいて画像プロンプトを生成"""
    for category, config in TECH_IMAGE_PROMPT_KEYWORDS.items():
        if any(word in text for word in config['patterns']):
            return config['prompt']
    
    return "professional technology news graphics, modern digital design"

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

def create_mulmocast_script_structure(title="テクノロジーニュース - AI最新トピック"):
    """mulmocastスクリプトの基本構造を作成"""
    return {
        "$mulmocast": {
            "version": "1.0"
        },
        "title": title,
        "description": "最新のAI・テクノロジーニュースを1〜2分でお届け",
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
            "style": "professional technology news graphics"
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

def add_main_content_beats(script, sentences, use_smart_pexels=False, smart_fetcher=None):
    """本文のbeatsを追加"""
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            if use_smart_pexels and smart_fetcher:
                # スマートPexels画像を使用
                print(f"🧠 スマート画像選定中 ({i+1}/{len(sentences)}): {sentence[:40]}...")
                image_path = smart_fetcher.fetch_smart_image(sentence)
                
                if image_path:
                    image_config = create_pexels_image_config(image_path)
                    beat = create_beat_config("Presenter", sentence, image_config=image_config)
                    print(f"✅ スマート画像を使用: {os.path.basename(image_path)}")
                else:
                    # スマートPexels取得失敗時はプロンプトにフォールバック
                    image_prompt = generate_image_prompt(sentence)
                    beat = create_beat_config("Presenter", sentence, image_prompt=image_prompt)
                    print(f"⚠️  スマートPexels取得失敗、プロンプト使用: {image_prompt[:50]}...")
            else:
                # 従来のプロンプト方式
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

def print_generation_summary(output_file, total_beats, fixed_images, use_smart_pexels=False):
    """生成結果のサマリーを出力"""
    print(f"✅ mulmocastスクリプトを生成しました: {output_file}")
    print(f"📊 総beats数: {total_beats} (目標範囲: {TARGET_BEATS_RANGE[0]}-{TARGET_BEATS_RANGE[1]})")
    print(f"🎬 構成: オープニング(1) + 本文({total_beats-2}) + クロージング(1)")
    
    if use_smart_pexels:
        print(f"🧠 画像取得: スマートPexels API使用")
    elif fixed_images:
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

def text_to_mulmo_script(text, output_file=None, time_period="morning", use_smart_pexels=False):
    """台本テキストをmulmocastスクリプト形式に変換"""
    
    # 固定画像設定を読み込み
    fixed_images = load_fixed_images_config()
    
    # スマートPexels設定
    smart_fetcher = None
    if use_smart_pexels:
        print("🧠 スマートPexels統合モード: 高品質画像選定を使用します")
        api_key = "NLaozjJD7A3J84VIp60DTMCAJ0VZIa2v9L4UdKZKqHdILTnMWYT09kyn"
        smart_fetcher = SmartPexelsImageFetcher(api_key)
    elif fixed_images:
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
    print(f"📝 分割された文数: {len(sentences)}")
    
    # beats数調整
    sentences = adjust_beats_count(sentences)
    print(f"📝 調整後文数: {len(sentences)}")
    
    # mulmocastスクリプト構造を作成
    script = create_mulmocast_script_structure()
    
    # 1. オープニングbeat追加
    add_opening_beat(script, opening_greeting, fixed_images)
    
    # 2. 本文のbeats追加
    add_main_content_beats(script, sentences, use_smart_pexels, smart_fetcher)
    
    # 3. クロージングbeat追加
    add_closing_beat(script, closing_greeting, fixed_images)
    
    # ファイル出力
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "tech_smart" if use_smart_pexels else "tech"
        output_file = f"{prefix}_script_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    
    total_beats = len(script["beats"])
    print_generation_summary(output_file, total_beats, fixed_images, use_smart_pexels)
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("使用方法: python text_to_mulmo_with_smart_pexels.py '台本テキスト' [output_file.json] [time_period] [--use-smart-pexels]")
        print("time_period: 'morning'(朝用・デフォルト) または 'evening'(夜用)")
        print("--use-smart-pexels: スマートPexels APIで高品質画像を取得")
        sys.exit(1)
    
    text = sys.argv[1]
    output_file = None
    time_period = "morning"
    use_smart_pexels = False
    
    # 引数解析
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--use-smart-pexels":
            use_smart_pexels = True
        elif arg in ["morning", "evening"]:
            time_period = arg
        elif arg.endswith(".json"):
            output_file = arg
    
    # time_periodの値をチェック
    if time_period not in ["morning", "evening"]:
        print(f"⚠️  警告: 不正な時間帯指定 '{time_period}'。'morning'を使用します。")
        time_period = "morning"
    
    result_file = text_to_mulmo_script(text, output_file, time_period, use_smart_pexels)
    print(f"🎬 次のコマンドで動画を生成できます:")
    print(f"cd ~/mulmocast && export PATH='/opt/homebrew/bin:$PATH' && mulmo movie {result_file} -l ja -c ja")

if __name__ == "__main__":
    main() 