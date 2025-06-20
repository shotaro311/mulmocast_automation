#!/usr/bin/env python3
"""
台本テキストをmulmocastスクリプト形式に自動変換するツール
使用方法: python text_to_mulmo.py "台本テキスト" output_file.json
"""

import json
import sys
import re
import os
from datetime import datetime

def load_fixed_images_config():
    """固定画像設定を読み込み"""
    # 複数の候補パスを試す
    candidates = [
        "config/fixed_images_config.json",
        "../config/fixed_images_config.json",
        "fixed_images_config.json",
        "~/mulmocast/config/fixed_images_config.json",
        os.path.expanduser("~/mulmocast/config/fixed_images_config.json"),
        os.path.join(os.getcwd(), "config/fixed_images_config.json")
    ]
    
    for config_file in candidates:
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

def text_to_mulmo_script(text, output_file=None):
    """台本テキストをmulmocastスクリプト形式に変換"""
    
    # 固定の挨拶文
    OPENING_GREETING = "おはようございます。この動画では、忙しい朝にサクッと聞ける重要な投資・経済ニュースを1～2分でお届けします。毎日の習慣で投資知識と判断力を高めていきましょう。ぜひチャンネル登録・高評価、よろしくお願いします。"
    CLOSING_GREETING = "このチャンネルでは毎日重要ニュースをピックアップしてお届けしています。よろしければチャンネル登録と高評価をお願いいたします。"
    
    # 固定画像設定を読み込み
    fixed_images = load_fixed_images_config()
    
    if fixed_images:
        print("💰 Token節約モード: 固定画像を再利用します")
        OPENING_IMAGE_CONFIG = {
            "type": "image",
            "source": {
                "kind": "path",
                "path": fixed_images.get("opening_image")
            }
        }
        CLOSING_IMAGE_CONFIG = {
            "type": "image", 
            "source": {
                "kind": "path",
                "path": fixed_images.get("closing_image")
            }
        }
    else:
        print("⚠️  固定画像設定が見つかりません。初回生成モードで動作します")
        print("💡 setup_fixed_images.py を実行してtoken節約を有効にしてください")
        OPENING_IMAGE_CONFIG = "professional news studio background with financial charts and graphs, morning news setting, clean and modern design"
        CLOSING_IMAGE_CONFIG = "YouTube channel subscribe button and like button with financial news channel branding, call-to-action graphics"
    
    # 固定の挨拶を台本から除去して、本文のみを抽出
    main_content = text.strip()
    main_content = main_content.replace(OPENING_GREETING, "").strip()
    main_content = main_content.replace(CLOSING_GREETING, "").strip()
    
    # 台本を文単位で分割（。で区切り、ただし数字の後の。は除外）
    sentences = re.split(r'(?<![0-9])。', main_content)
    sentences = [s.strip() + '。' for s in sentences if s.strip() and len(s.strip()) > 5]
    
    # 最後の文の重複した。を修正
    if sentences:
        sentences[-1] = sentences[-1].replace('。。', '。')
    
    # beats数調整（7-11cutの範囲）
    # 固定の挨拶2つ + 本文 = 7-11beats
    target_main_beats = min(max(len(sentences), 5), 9)  # 本文部分は5-9beats
    
    if len(sentences) > target_main_beats:
        # 文が多すぎる場合は結合
        combined_sentences = []
        chunk_size = len(sentences) // target_main_beats + 1
        
        for i in range(0, len(sentences), chunk_size):
            chunk = sentences[i:i+chunk_size]
            combined_text = "".join(chunk).replace('。。', '。')
            combined_sentences.append(combined_text)
        
        sentences = combined_sentences[:target_main_beats]
    elif len(sentences) < 5:
        # 文が少なすぎる場合は分割
        new_sentences = []
        for sentence in sentences:
            # 長い文を分割（100文字以上）
            if len(sentence) > 100:
                # 適当な区切りで分割
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
        sentences = new_sentences[:9]  # 最大9beats
    
    # 画像プロンプトを自動生成する関数
    def generate_image_prompt(text):
        """文章の内容に基づいて画像プロンプトを生成"""
        if any(word in text for word in ['日銀', '金利', '利上げ', '物価', 'パーセント']):
            return "Bank of Japan building with economic charts showing interest rates and inflation data, professional financial graphics"
        elif any(word in text for word in ['円高', '円安', 'ドル円', '為替']):
            return "Japanese yen currency symbols with upward arrow, interest rate charts, financial market data visualization"
        elif any(word in text for word in ['中東', 'イスラエル', 'イラン', '原油']):
            return "Middle East map with oil price charts showing upward trend, stock market graphs with red and green indicators"
        elif any(word in text for word in ['エネルギー', '地政学', 'リスク', '分散']):
            return "portfolio diversification chart showing stocks and bonds correlation during geopolitical risk, warning indicators"
        elif any(word in text for word in ['CPI', 'インフレ', '総務省']):
            return "USD/JPY currency exchange rate chart showing 145.23 level, Japanese yen strengthening against US dollar"
        elif any(word in text for word in ['リバランス', 'NISA', '利益確定']):
            return "portfolio rebalancing illustration with Japanese assets and NISA investment account graphics, profit-taking strategies"
        elif any(word in text for word in ['ポイント', '整理', '①', '②', '③', 'まとめ']):
            return "summary infographic with three key points, checklist format, portfolio risk management visualization"
        elif any(word in text for word in ['株', '株式', '日経', 'ダウ', 'NASDAQ']):
            return "stock market graphs with red and green indicators, trading screens, financial data visualization"
        else:
            return "professional financial news graphics, clean modern design"
    
    # mulmocastスクリプト構造を作成
    script = {
        "$mulmocast": {
            "version": "1.0"
        },
        "title": "投資・経済ニュース - 朝の重要ポイント",
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
    
    # 1. 固定のオープニング
    opening_beat = {
        "speaker": "Presenter",
        "text": OPENING_GREETING
    }
    
    if fixed_images:
        opening_beat["image"] = OPENING_IMAGE_CONFIG
    else:
        opening_beat["imagePrompt"] = OPENING_IMAGE_CONFIG
    
    script["beats"].append(opening_beat)
    
    # 2. 本文のbeats
    for sentence in sentences:
        if sentence.strip():
            beat = {
                "speaker": "Presenter",
                "text": sentence.strip(),
                "imagePrompt": generate_image_prompt(sentence)
            }
            script["beats"].append(beat)
    
    # 3. 固定のクロージング
    closing_beat = {
        "speaker": "Presenter",
        "text": CLOSING_GREETING
    }
    
    if fixed_images:
        closing_beat["image"] = CLOSING_IMAGE_CONFIG
    else:
        closing_beat["imagePrompt"] = CLOSING_IMAGE_CONFIG
    
    script["beats"].append(closing_beat)
    
    # ファイル出力
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"news_script_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    
    total_beats = len(script["beats"])
    print(f"✅ mulmocastスクリプトを生成しました: {output_file}")
    print(f"📊 総beats数: {total_beats} (目標範囲: 7-11)")
    print(f"🎬 構成: オープニング(1) + 本文({total_beats-2}) + クロージング(1)")
    
    if fixed_images:
        print(f"💰 Token節約: 固定画像2枚を再利用（API呼び出しなし）")
    else:
        print(f"💡 Token節約を有効にするには setup_fixed_images.py を実行してください")
    
    # beats数の警告
    if total_beats < 7:
        print(f"⚠️  警告: beats数が少なすぎます ({total_beats} < 7)")
    elif total_beats > 11:
        print(f"⚠️  警告: beats数が多すぎます ({total_beats} > 11)")
    else:
        print(f"✅ beats数が適切な範囲内です")
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("使用方法: python text_to_mulmo.py '台本テキスト' [output_file.json]")
        sys.exit(1)
    
    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result_file = text_to_mulmo_script(text, output_file)
    print(f"🎬 次のコマンドで動画を生成できます:")
    print(f"cd ~/mulmocast && export PATH='/opt/homebrew/bin:$PATH' && mulmo movie {result_file} -l ja -c ja")

if __name__ == "__main__":
    main() 