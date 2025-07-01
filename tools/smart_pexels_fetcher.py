#!/usr/bin/env python3
"""
スマートPexels画像取得ツール - 改良版画像選定機能付き
"""

import requests
import os
import re
import json
from urllib.parse import quote
from googletrans import Translator
from janome.tokenizer import Tokenizer
from datetime import datetime

class SmartPexelsImageFetcher:
    def __init__(self, api_key):
        self.api_key = api_key.encode('ascii', 'ignore').decode('ascii')
        self.translator = Translator()
        self.tokenizer = Tokenizer()
        
        # 画像品質基準
        self.min_width = 800
        self.min_height = 600
        self.preferred_aspect_ratio = 16/9  # 動画用
        
        # テック系キーワード重み付け
        self.tech_keywords_weights = {
            'apple': ['apple', 'iphone', 'ipad', 'macbook', 'ios'],
            'google': ['google', 'android', 'chrome', 'pixel'],
            'microsoft': ['microsoft', 'windows', 'azure', 'surface'],
            'ai': ['artificial intelligence', 'ai', 'robot', 'machine learning'],
            'startup': ['startup', 'office', 'meeting', 'business'],
            'technology': ['technology', 'computer', 'software', 'digital']
        }
    
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
                        weight = self.tech_keywords_weights[category][0] if isinstance(self.tech_keywords_weights[category], list) else 3.0
                        weighted_keywords.append(f"{keyword}({weight})")
            
            # 一般的なキーワードも追加
            general_keywords = english_text.split()[:5]  # 最初の5つのキーワード
            for keyword in general_keywords:
                if len(keyword) > 2:  # 短すぎるキーワードは除外
                    weighted_keywords.append(f"{keyword}(1.0)")
            
            print(f"🔑 抽出キーワード: {weighted_keywords}")
            return weighted_keywords
            
        except Exception as e:
            print(f"❌ キーワード抽出エラー: {e}")
            # 完全フォールバック: 基本的なAIキーワードを返す
            return ["technology(3.0)", "ai(3.0)", "innovation(2.0)"]
    
    def calculate_keyword_weight(self, keyword):
        """キーワードの重要度を計算"""
        weight = 1.0  # 基本重み
        
        # テック系キーワードのボーナス
        for category, keywords in self.tech_keywords_weights.items():
            if keyword in keywords:
                weight += 2.0
                break
        
        # 企業名のボーナス
        company_names = ['apple', 'google', 'microsoft', 'meta', 'amazon', 'tesla']
        if keyword in company_names:
            weight += 1.5
        
        # 技術用語のボーナス
        tech_terms = ['ai', 'vr', 'ar', 'blockchain', 'cloud', 'security']
        if keyword in tech_terms:
            weight += 1.0
        
        return weight
    
    def search_images_smart(self, text, per_page=20):
        """スマート画像検索"""
        # キーワード抽出
        weighted_keywords = self.extract_keywords(text)
        
        # 複数の検索クエリを生成
        search_queries = self.generate_search_queries(weighted_keywords)
        
        all_results = []
        for query in search_queries[:3]:  # 上位3つのクエリで検索
            print(f"🔍 検索クエリ: {query}")
            results = self.search_pexels_api(query, per_page//3)
            if results and results['photos']:
                all_results.extend(results['photos'])
        
        return {'photos': all_results}
    
    def generate_search_queries(self, weighted_keywords):
        """重み付きキーワードから複数の検索クエリを生成"""
        try:
            if not weighted_keywords:
                return ["technology", "innovation", "business"]
            
            # 重み付きキーワードから実際のキーワードを抽出
            keywords = []
            for item in weighted_keywords:
                if isinstance(item, str) and '(' in item:
                    # "keyword(weight)" 形式から keyword を抽出
                    keyword = item.split('(')[0]
                    keywords.append(keyword)
                elif isinstance(item, tuple):
                    # (keyword, weight) 形式から keyword を抽出
                    keywords.append(item[0])
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
            
            if len(keywords) >= 3:
                queries.append(f"{keywords[0]} {keywords[1]} {keywords[2]}")
            
            print(f"🔍 検索クエリ: {queries}")
            return queries
            
        except Exception as e:
            print(f"⚠️  クエリ生成エラー: {e}")
            return ["technology", "innovation", "business"]
    
    def search_pexels_api(self, query, per_page=15):
        """Pexels API検索"""
        headers = {"Authorization": self.api_key}
        encoded_query = quote(query)
        url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page={per_page}"
        
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None
    
    def score_image(self, image, keywords):
        """画像を採点（100点満点）"""
        score = 0
        
        # 解像度スコア（25点満点）
        width = image.get('width', 0)
        height = image.get('height', 0)
        if width >= 1920 and height >= 1080:
            score += 25
        elif width >= 800 and height >= 600:
            score += 20
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
        alt_text = image.get('alt', '').lower()
        photographer = image.get('photographer', '').lower()
        
        keyword_matches = 0
        for keyword_item in keywords:
            if isinstance(keyword_item, str) and '(' in keyword_item:
                keyword = keyword_item.split('(')[0].lower()
            else:
                keyword = str(keyword_item).lower()
            
            if keyword in alt_text or keyword in photographer:
                keyword_matches += 1
        
        score += min(keyword_matches * 5, 25)
        
        # 色彩スコア（15点満点）
        avg_color = image.get('avg_color', '#000000')
        if avg_color and avg_color != '#000000':
            score += 15
        else:
            score += 5
        
        # 写真家評価スコア（15点満点）
        if photographer:
            score += 15
        else:
            score += 5
        
        return min(score, 100)  # 最大100点
    
    def select_best_image(self, search_results, keywords):
        """最適な画像を選択"""
        if not search_results or not search_results['photos']:
            return None
        
        # 各画像を採点
        scored_images = []
        for image in search_results['photos']:
            score = self.score_image(image, keywords)
            scored_images.append((image, score))
            print(f"📊 画像ID {image['id']}: {score:.1f}点 ({image['width']}x{image['height']})")
        
        # スコア順にソート
        scored_images.sort(key=lambda x: x[1], reverse=True)
        
        # 最高スコアの画像を選択
        best_image = scored_images[0][0]
        best_score = scored_images[0][1]
        
        print(f"🏆 選択された画像: ID {best_image['id']} (スコア: {best_score:.1f}点)")
        return best_image
    
    def fetch_smart_image(self, text, output_dir="output/images/pexels"):
        """スマート画像選定でPexels画像を取得"""
        try:
            print(f"🧠 スマート画像選定開始: {text[:80]}...")
            
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
                print(f"🔍 検索クエリ: {query}")
                images = self.search_pexels_api(query)
                if images:
                    all_images.extend(images)
            
            if not all_images:
                print("❌ 画像が見つかりませんでした")
                return None
            
            print(f"📸 検索結果: {len(all_images)}枚")
            
            # 画像を採点
            scored_images = []
            for image in all_images:
                score = self.score_image(image, keywords)
                scored_images.append((image, score))
                print(f"📊 画像ID {image['id']}: {score:.1f}点 ({image['width']}x{image['height']})")
            
            # 最高スコアの画像を選択
            best_image, best_score = max(scored_images, key=lambda x: x[1])
            print(f"🏆 選択された画像: ID {best_image['id']} (スコア: {best_score:.1f}点)")
            
            # 画像をダウンロード
            filename = self.generate_smart_filename(text, best_image['id'])
            downloaded_path = self.download_image(best_image['src']['large'], filename, output_dir)
            
            if downloaded_path:
                print(f"✅ スマート画像ダウンロード完了: {downloaded_path}")
                return downloaded_path
            else:
                print("❌ 画像ダウンロードに失敗しました")
                return None
                
        except Exception as e:
            print(f"❌ スマート画像選定エラー: {e}")
            return None
    
    def download_image(self, image_url, filename, output_dir):
        """画像ダウンロード"""
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名生成
        sanitized_filename = re.sub(r'[\\/*?:"<>|]', "_", filename[:30])
        file_path = os.path.join(output_dir, sanitized_filename)
        
        # ダウンロード
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ スマート画像ダウンロード完了: {file_path}")
            return file_path
        else:
            print(f"❌ ダウンロード失敗: {filename}")
            return None

    def split_japanese_query(self, query):
        """日本語クエリを意味のあるキーワードに分割"""
        try:
            tokens = self.tokenizer.tokenize(query)
            keywords = [token.surface for token in tokens 
                       if token.part_of_speech.split(',')[0] in ['名詞', '動詞', '形容詞'] 
                       and len(token.surface) > 1]  # 1文字のキーワードは除外
            
            # 重複を除去し、最初の10個まで
            unique_keywords = list(dict.fromkeys(keywords))[:10]
            return unique_keywords
            
        except Exception as e:
            print(f"⚠️  日本語解析エラー: {e}")
            # フォールバック: 基本的な分割
            import re
            # カタカナ、ひらがな、漢字、英数字の単語を抽出
            words = re.findall(r'[ァ-ヶー]+|[ひ-ゖ]+|[一-龯]+|[a-zA-Z0-9]+', query)
            return [word for word in words if len(word) > 1][:10]

    def generate_smart_filename(self, text, image_id):
        """スマートファイル名を生成"""
        sanitized_text = re.sub(r'[\\/*?:"<>|]', "_", text[:40])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"smart_{sanitized_text}_{image_id}_{timestamp}.jpg"

# 使用例
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python smart_pexels_fetcher.py \"検索テキスト\"")
        sys.exit(1)
    
    api_key = "NLaozjJD7A3J84VIp60DTMCAJ0VZIa2v9L4UdKZKqHdILTnMWYT09kyn"
    fetcher = SmartPexelsImageFetcher(api_key)
    
    text = sys.argv[1]
    result = fetcher.fetch_smart_image(text)
    
    if result:
        print(f"🎉 成功: {result}")
    else:
        print("❌ 失敗") 