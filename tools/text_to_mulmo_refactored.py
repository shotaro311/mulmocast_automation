#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テキスト→mulmocast台本変換ツール（リファクタリング版）
"""

import sys
import json
import os
import argparse
from typing import List, Dict, Optional

# パス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_processing_utils import TextProcessor
from unsplash_image_fetcher_refactored import UnsplashImageFetcher

# 定数
GREETING_TEMPLATES = {
    'morning': "おはようございます。今日の重要なテクノロジーニュースを1〜2分でお届けします。最新の技術動向をチェックして、デジタル時代を生き抜く知識を身につけていきましょう。ぜひチャンネル登録・高評価、よろしくお願いします。",
    'evening': "こんばんは。今日一日お疲れ様でした。本日の重要なテクノロジーニュースを1〜2分でお届けします。明日に向けて最新の技術動向をチェックしていきましょう。ぜひチャンネル登録・高評価、よろしくお願いします。",
    'afternoon': "こんにちは。今日の重要なテクノロジーニュースを1〜2分でお届けします。最新の技術動向をチェックして、デジタル時代を生き抜く知識を身につけていきましょう。ぜひチャンネル登録・高評価、よろしくお願いします。"
}

CLOSING_TEMPLATE = "このチャンネルでは毎日重要ニュースをピックアップしてお届けしています。よろしければチャンネル登録と高評価をお願いいたします。"

class MulmoScriptGenerator:
    """mulmocast台本生成クラス"""
    
    def __init__(self, use_unsplash: bool = False):
        """初期化
        
        Args:
            use_unsplash: Unsplash画像を使用するかどうか
        """
        self.use_unsplash = use_unsplash
        self.unsplash_fetcher = None
        
        if use_unsplash:
            try:
                self.unsplash_fetcher = UnsplashImageFetcher()
                print("✅ Unsplash統合が有効になりました")
            except Exception as e:
                print(f"⚠️  Unsplash初期化エラー: {e}")
                print("🔄 AI生成プロンプトを使用します")
                self.use_unsplash = False
    
    def generate_script(self, text: str, time_of_day: str = 'morning') -> Dict:
        """台本を生成
        
        Args:
            text: 元テキスト
            time_of_day: 時間帯 ('morning', 'evening', 'afternoon')
            
        Returns:
            mulmocast台本辞書
        """
        # テキストを文に分割・調整
        sentences = TextProcessor.split_text_into_sentences(text, detailed_split=True)
        sentences = TextProcessor.adjust_beats_count(sentences)
        
        # 台本構造を構築
        script = self._build_script_structure(time_of_day)
        
        # 本文beatsを生成
        main_beats = self._generate_main_beats(sentences)
        
        # beats統合
        script['beats'].extend(main_beats)
        script['beats'].append(self._create_closing_beat())
        
        print(f"✅ 台本生成完了: {len(script['beats'])}beats")
        return script
    
    def _build_script_structure(self, time_of_day: str) -> Dict:
        """基本的な台本構造を構築"""
        greeting = GREETING_TEMPLATES.get(time_of_day, GREETING_TEMPLATES['morning'])
        
        return {
            "$mulmocast": {"version": "1.0"},
            "canvasSize": {"width": 1280, "height": 720},
            "speechParams": {
                "provider": "openai",
                "speakers": {
                    "Presenter": {
                        "displayName": {"ja": "プレゼンター"},
                        "voiceId": "shimmer"
                    }
                }
            },
            "imageParams": {
                "style": "professional technology news graphics",
                "provider": "openai"
            },
            "audioParams": {
                "padding": 0.3,
                "introPadding": 1,
                "closingPadding": 0.8,
                "outroPadding": 1
            },
            "title": "テクノロジーニュース - AI最新トピック",
            "description": "最新のAI・テクノロジーニュースを1〜2分でお届け",
            "lang": "ja",
            "beats": [self._create_opening_beat(greeting)]
        }
    
    def _create_opening_beat(self, greeting: str) -> Dict:
        """オープニングbeatを作成"""
        return {
            "speaker": "Presenter",
            "text": greeting,
            "image": {
                "type": "image",
                "source": {
                    "kind": "path",
                    "path": "output/images/fixed_images_setup/0p.png"
                }
            }
        }
    
    def _create_closing_beat(self) -> Dict:
        """クロージングbeatを作成"""
        return {
            "speaker": "Presenter",
            "text": CLOSING_TEMPLATE,
            "image": {
                "type": "image",
                "source": {
                    "kind": "path",
                    "path": "output/images/fixed_images_setup/1p.png"
                }
            }
        }
    
    def _generate_main_beats(self, sentences: List[str]) -> List[Dict]:
        """メインコンテンツのbeatsを生成"""
        beats = []
        
        for sentence in sentences:
            beat = {
                "speaker": "Presenter",
                "text": sentence
            }
            
            # 画像設定
            if self.use_unsplash and self.unsplash_fetcher:
                image_path = self._get_unsplash_image(sentence)
                if image_path:
                    beat["image"] = {
                        "type": "image",
                        "source": {
                            "kind": "path",
                            "path": image_path
                        }
                    }
                else:
                    # フォールバック: AI生成プロンプト
                    beat["imagePrompt"] = self._generate_image_prompt(sentence)
            else:
                # AI生成プロンプト
                beat["imagePrompt"] = self._generate_image_prompt(sentence)
            
            beats.append(beat)
        
        return beats
    
    def _get_unsplash_image(self, text: str) -> Optional[str]:
        """Unsplash画像を取得"""
        try:
            output_dir = "output/images/unsplash"
            return self.unsplash_fetcher.fetch_smart_image(text, output_dir)
        except Exception as e:
            print(f"⚠️  Unsplash画像取得エラー: {e}")
            return None
    
    def _generate_image_prompt(self, text: str) -> str:
        """AI生成用画像プロンプトを生成"""
        # 基本プロンプト
        base_prompt = "professional technology news graphics"
        
        # テキストからキーワードを抽出してプロンプトに追加
        tech_keywords = self._extract_tech_keywords(text)
        if tech_keywords:
            specific_prompt = f"{base_prompt}, {', '.join(tech_keywords)}"
            return specific_prompt
        
        return f"{base_prompt}, modern digital design"
    
    def _extract_tech_keywords(self, text: str) -> List[str]:
        """テキストからテック系キーワードを抽出"""
        tech_terms = [
            'AI', 'Apple', 'Siri', 'ChatGPT', 'Claude', 'Meta', 'OpenAI',
            'Instagram', 'WhatsApp', 'Cloudflare', 'iPhone', 'Android',
            'Google', 'Microsoft', 'Tesla', 'Amazon', 'Facebook',
            'technology', 'innovation', 'digital', 'software', 'hardware',
            'algorithm', 'machine learning', 'automation', 'cloud', 'security'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for term in tech_terms:
            if term.lower() in text_lower:
                found_keywords.append(term.lower())
        
        return found_keywords[:3]  # 最大3つまで

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='テキストをmulmocast台本に変換')
    parser.add_argument('text', help='変換するテキスト')
    parser.add_argument('output_file', help='出力ファイル名')
    parser.add_argument('time_of_day', choices=['morning', 'evening', 'afternoon'], 
                       help='時間帯')
    parser.add_argument('--use-unsplash', action='store_true', 
                       help='Unsplash画像を使用')
    
    args = parser.parse_args()
    
    try:
        # 台本生成
        generator = MulmoScriptGenerator(use_unsplash=args.use_unsplash)
        script = generator.generate_script(args.text, args.time_of_day)
        
        # ファイル出力
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 台本を保存しました: {args.output_file}")
        
        # 統計情報
        beats_count = len(script['beats'])
        print(f"📊 生成統計:")
        print(f"   - 総beats数: {beats_count}")
        print(f"   - メインコンテンツ: {beats_count - 2}beats")
        print(f"   - 画像取得方法: {'Unsplash API' if args.use_unsplash else 'AI生成プロンプト'}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 