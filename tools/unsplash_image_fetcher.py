#!/usr/bin/env python3
"""
Unsplash APIを使用して台本内容に応じた画像を自動取得するツール
Usage: python unsplash_image_fetcher.py "search_query" [output_dir]
"""

import requests
import os
import re
import json
from urllib.parse import quote
from googletrans import Translator
from janome.tokenizer import Tokenizer
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# Unsplash API設定
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
UNSPLASH_SECRET_KEY = os.getenv('UNSPLASH_SECRET_KEY')
UNSPLASH_API_URL = "https://api.unsplash.com"

# デフォルト出力ディレクトリ
DEFAULT_OUTPUT_DIR = "output/images/unsplash"

class UnsplashImageFetcher:
    def __init__(self, access_key=None, secret_key=None):
        self.access_key = access_key or UNSPLASH_ACCESS_KEY
        self.secret_key = secret_key or UNSPLASH_SECRET_KEY
        
        # API認証情報の確認
        if not self.access_key:
            raise ValueError("Unsplash Access Keyが設定されていません。.envファイルでUNSPLASH_ACCESS_KEYを設定してください。")
        
        self.translator = Translator()
        self.tokenizer = Tokenizer()
        
        # 画像品質基準
        self.min_width = 800
        self.min_height = 600
        self.preferred_aspect_ratio = 16/9  # 動画用
        
        # テック系キーワード重み付け
        self.tech_keywords_weights = {
            'apple': ['apple', 'iphone', 'ipad', 'macbook', 'ios', 'siri'],
            'google': ['google', 'android', 'chrome', 'pixel'],
            'microsoft': ['microsoft', 'windows', 'azure', 'office'],
            'meta': ['meta', 'facebook', 'instagram', 'whatsapp', 'oculus'],
            'openai': ['openai', 'chatgpt', 'gpt', 'artificial intelligence'],
            'anthropic': ['anthropic', 'claude', 'ai assistant'],
            'cloudflare': ['cloudflare', 'cdn', 'web security'],
            'ai_technology': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning'],
            'voice_assistant': ['voice assistant', 'smart speaker', 'speech recognition'],
            'web_security': ['cybersecurity', 'data protection', 'web security'],
            'gpu_computing': ['gpu', 'computing', 'data center', 'cloud computing'],
            'social_media': ['social media', 'social network', 'communication'],
            'mobile_tech': ['smartphone', 'mobile', 'tablet', 'wearable'],
            'startup': ['startup', 'innovation', 'technology', 'business']
        }
        
    def split_japanese_query(self, query):
        """日本語クエリを意味のあるキーワードに分割"""
        try:
            tokens = self.tokenizer.tokenize(query)
            keywords = [token.surface for token in tokens 
                       if token.part_of_speech.split(',')[0] in ['名詞', '動詞', '形容詞'] 
                       and len(token.surface) > 1]
            
            # 重複を除去し、最初の10個まで
            unique_keywords = list(dict.fromkeys(keywords))[:10]
            return unique_keywords
            
        except Exception as e:
            print(f"⚠️  日本語解析エラー: {e}")
            # フォールバック: 基本的な分割
            import re
            words = re.findall(r'[ァ-ヶー]+|[ひ-ゖ]+|[一-龯]+|[a-zA-Z0-9]+', query)
            return [word for word in words if len(word) > 1][:10]
    
    def extract_keywords(self, text):
        """日本語テキストからキーワードを抽出し、重み付きで英語に翻訳"""
        try:
            # 日本語キーワード抽出
            japanese_keywords = self.split_japanese_query(text)
            print(f"🔑 日本語キーワード: {japanese_keywords}")
            
            if not japanese_keywords:
                return []
            
            # 翻訳を試行（エラーハンドリング付き）
            try:
                english_text = self.translator.translate(' '.join(japanese_keywords), dest='en').text
                print(f"🌐 英語翻訳: {english_text}")
            except Exception as e:
                print(f"⚠️  翻訳エラー: {e}")
                # フォールバック: 日本語キーワードをそのまま使用
                english_text = ' '.join(japanese_keywords)
                print(f"🔄 フォールバック: {english_text}")
            
            # 重み付きキーワード生成
            weighted_keywords = []
            
            # テック系キーワードの重み付け
            for category, keywords in self.tech_keywords_weights.items():
                for keyword in keywords:
                    if keyword.lower() in english_text.lower() or keyword.lower() in text.lower():
                        weight = 4.0 if category in ['apple', 'meta', 'openai'] else 3.0
                        weighted_keywords.append(f"{keyword}({weight})")
            
            # 一般的なキーワードも追加
            general_keywords = english_text.split()[:5]
            for keyword in general_keywords:
                if len(keyword) > 2:
                    weighted_keywords.append(f"{keyword}(1.0)")
            
            print(f"🔑 抽出キーワード: {weighted_keywords}")
            return weighted_keywords
            
        except Exception as e:
            print(f"❌ キーワード抽出エラー: {e}")
            return ["technology(3.0)", "innovation(3.0)", "business(2.0)"]
    
    def generate_search_queries(self, weighted_keywords):
        """重み付きキーワードから複数の検索クエリを生成"""
        try:
            if not weighted_keywords:
                return ["technology", "innovation", "business"]
            
            # 重み付きキーワードから実際のキーワードを抽出
            keywords = []
            for item in weighted_keywords:
                if isinstance(item, str) and '(' in item:
                    keyword = item.split('(')[0]
                    keywords.append(keyword)
                else:
                    keywords.append(str(item))
            
            # 重複を除去
            keywords = list(dict.fromkeys(keywords))[:5]
            
            queries = []
            
            # 単一キーワードクエリ
            for keyword in keywords[:3]:
                queries.append(keyword)
            
            # 複合キーワードクエリ
            if len(keywords) >= 2:
                queries.append(f"{keywords[0]} {keywords[1]}")
            
            print(f"🔍 検索クエリ: {queries}")
            return queries
            
        except Exception as e:
            print(f"⚠️  クエリ生成エラー: {e}")
            return ["technology", "innovation", "business"]
    
    def search_unsplash_api(self, query, per_page=15):
        """Unsplash APIで画像を検索"""
        try:
            headers = {
                'Authorization': f'Client-ID {self.access_key}',
                'Accept-Version': 'v1'
            }
            
            params = {
                'query': query,
                'per_page': per_page,
                'orientation': 'landscape',  # 動画用に横向き優先
                'order_by': 'relevant'
            }
            
            response = requests.get(
                f"{UNSPLASH_API_URL}/search/photos",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"🔍 API レスポンス: {len(results)}件の画像を取得")
                # デバッグ用：最初の画像の構造を確認
                if results:
                    first_image = results[0]
                    print(f"🔍 画像構造確認: keys={list(first_image.keys())}")
                    if 'urls' in first_image:
                        print(f"🔍 URLs: {list(first_image['urls'].keys())}")
                return results
            else:
                print(f"⚠️  Unsplash API エラー: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Unsplash API 検索エラー: {e}")
            return []
    
    def score_image(self, image, keywords):
        """画像を採点（100点満点）"""
        try:
            score = 0
            
            # 解像度スコア（25点満点）
            width = image.get('width', 0)
            height = image.get('height', 0)
            if width >= 1920 and height >= 1080:
                score += 25
            elif width >= 1200 and height >= 800:
                score += 20
            elif width >= 800 and height >= 600:
                score += 15
            else:
                score += 10
            
            # アスペクト比スコア（20点満点）
            if width > 0 and height > 0:
                aspect_ratio = width / height
                target_ratio = 16/9
                ratio_diff = abs(aspect_ratio - target_ratio)
                if ratio_diff < 0.1:
                    score += 20
                elif ratio_diff < 0.3:
                    score += 15
                else:
                    score += 10
            
            # キーワード関連性スコア（25点満点）
            description = image.get('description', '') or image.get('alt_description', '') or ''
            tags = image.get('tags', [])
            
            # tagsがNoneの場合のハンドリング
            tag_titles = []
            if tags and isinstance(tags, list):
                tag_titles = [tag.get('title', '') if isinstance(tag, dict) else str(tag) for tag in tags]
            
            all_text = (description + ' ' + ' '.join(tag_titles)).lower()
            
            keyword_matches = 0
            for keyword_item in keywords:
                if isinstance(keyword_item, str) and '(' in keyword_item:
                    keyword = keyword_item.split('(')[0].lower()
                else:
                    keyword = str(keyword_item).lower()
                
                if keyword in all_text:
                    keyword_matches += 1
            
            score += min(keyword_matches * 3, 25)
            
            # 色彩スコア（15点満点）
            color = image.get('color', '#000000')
            if color and color != '#000000' and color != '#ffffff':
                score += 15
            else:
                score += 5
            
            # いいね数・品質スコア（15点満点）
            likes = image.get('likes', 0)
            if likes >= 100:
                score += 15
            elif likes >= 50:
                score += 12
            elif likes >= 10:
                score += 8
            else:
                score += 5
            return min(score, 100)
        except Exception as e:
            print(f"⚠️  画像採点エラー: {e}")
            return 0
    
    def generate_smart_filename(self, text, image_id):
        """スマートファイル名を生成"""
        sanitized_text = re.sub(r'[\\/*?:"<>|]', "_", text[:40])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"unsplash_{sanitized_text}_{image_id}_{timestamp}.jpg"
    
    def download_image(self, image_url, filename, output_dir):
        """画像をダウンロード"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # ファイル名をサニタイズ
            sanitized_filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
            file_path = os.path.join(output_dir, sanitized_filename)
            
            # 画像をダウンロード
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ 画像ダウンロード完了: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ 画像ダウンロードエラー: {e}")
            return None
    
    def fetch_smart_image(self, text, output_dir=DEFAULT_OUTPUT_DIR):
        """スマート画像選定でUnsplash画像を取得"""
        try:
            print(f"🎨 Unsplash スマート画像選定開始: {text[:80]}...")
            
            # キーワード抽出
            keywords = self.extract_keywords(text)
            if not keywords:
                print("⚠️  キーワードが抽出できませんでした")
                return None
            
            # 検索クエリ生成
            search_queries = self.generate_search_queries(keywords)
            
            # 全ての検索結果を収集
            all_images = []
            for query in search_queries:
                print(f"🔍 Unsplash検索: {query}")
                images = self.search_unsplash_api(query)
                if images:
                    all_images.extend(images)
            
            if not all_images:
                print("❌ Unsplash画像が見つかりませんでした")
                return None
            
            print(f"📸 Unsplash検索結果: {len(all_images)}枚")
            
            # 画像を採点
            scored_images = []
            for i, image in enumerate(all_images):
                print(f"🔍 画像 {i+1}/{len(all_images)} を処理中: ID={image.get('id', 'unknown')}")
                
                # 必要なフィールドの存在確認
                if not all(key in image for key in ['id', 'width', 'height', 'urls']):
                    print(f"⚠️  不完全な画像データをスキップ: {image.get('id', 'unknown')}")
                    continue
                    
                try:
                    score = self.score_image(image, keywords)
                    scored_images.append((image, score))
                    print(f"📊 画像ID {image['id']}: {score:.1f}点 ({image['width']}x{image['height']}) - {image.get('description', 'No description')[:50]}")
                except Exception as e:
                    print(f"❌ 画像採点エラー (ID: {image.get('id', 'unknown')}): {e}")
                    continue
            
            # 最高スコアの画像を選択
            if not scored_images:
                print("❌ 採点可能な画像がありませんでした")
                return None
                
            best_image, best_score = max(scored_images, key=lambda x: x[1])
            print(f"🏆 選択された画像: ID {best_image['id']} (スコア: {best_score:.1f}点)")
            
            # 画像URLの確認
            if 'urls' not in best_image or 'regular' not in best_image['urls']:
                print("❌ 画像URLが取得できませんでした")
                return None
            
            # 画像をダウンロード
            filename = self.generate_smart_filename(text, best_image['id'])
            image_url = best_image['urls']['regular']  # 1080px幅の高品質画像
            downloaded_path = self.download_image(image_url, filename, output_dir)
            
            # ダウンロード統計をUnsplashに送信（API利用規約に従って）
            if downloaded_path and 'links' in best_image and 'download_location' in best_image['links']:
                try:
                    headers = {'Authorization': f'Client-ID {self.access_key}'}
                    requests.get(best_image['links']['download_location'], headers=headers)
                    print("📊 Unsplashダウンロード統計送信完了")
                except:
                    pass  # 統計送信は必須ではないのでエラーは無視
            
            if downloaded_path:
                print(f"✅ Unsplash画像取得完了: {downloaded_path}")
                return downloaded_path
            else:
                print("❌ Unsplash画像ダウンロードに失敗しました")
                return None
                
        except Exception as e:
            print(f"❌ Unsplashスマート画像選定エラー: {e}")
            return None

# 使用例
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python unsplash_image_fetcher.py \"検索クエリ\" [出力ディレクトリ]")
        print("例: python unsplash_image_fetcher.py \"Apple iPhone technology\"")
        sys.exit(1)
    
    query = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_DIR
    
    fetcher = UnsplashImageFetcher()
    result = fetcher.fetch_smart_image(query, output_dir)
    
    if result:
        print(f"✅ 成功: {result}")
    else:
        print("❌ 失敗") 