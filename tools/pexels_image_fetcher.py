#!/usr/bin/env python3
"""
Pexels APIを使用して台本内容に応じた画像を自動取得するツール
Usage: python pexels_image_fetcher.py "search_query" [output_dir]
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

# Pexels API設定
PEXELS_API_KEY = "NLaozjJD7A3J84VIp60DTMCAJ0VZIa2v9L4UdKZKqHdILTnMWYT09kyn"
PEXELS_API_URL = "https://api.pexels.com/v1/search"

# デフォルト出力ディレクトリ
DEFAULT_OUTPUT_DIR = "output/images/pexels"

class PexelsImageFetcher:
    def __init__(self, api_key=PEXELS_API_KEY):
        self.api_key = api_key.encode('ascii', 'ignore').decode('ascii')
        self.translator = Translator()
        self.tokenizer = Tokenizer()
        
    def split_japanese_query(self, query):
        """日本語クエリを意味のあるキーワードに分割"""
        tokens = self.tokenizer.tokenize(query)
        keywords = [token.surface for token in tokens 
                   if token.part_of_speech.split(',')[0] in ['名詞', '動詞', '形容詞']]
        return ' '.join(keywords)
    
    def translate_to_english(self, text):
        """日本語を英語に翻訳"""
        try:
            return self.translator.translate(text, dest='en').text
        except Exception as e:
            print(f"翻訳エラー: {e}")
            return text
    
    def search_images(self, query, per_page=15):
        """Pexels APIで画像を検索"""
        headers = {"Authorization": self.api_key}
        encoded_query = quote(query)
        full_url = f"{PEXELS_API_URL}?query={encoded_query}&per_page={per_page}"
        
        response = requests.get(full_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API エラー: {response.status_code}")
            return None
    
    def get_best_image(self, search_results):
        """検索結果から最適な画像を選択"""
        if search_results and search_results['photos']:
            # 最初の画像を選択（Pexelsは関連性順でソート済み）
            return search_results['photos'][0]
        return None
    
    def sanitize_filename(self, filename):
        """ファイル名に使用できない文字を置換"""
        return re.sub(r'[\\/*?:"<>|]', "_", filename)
    
    def generate_filename(self, query, image_id):
        """一意のファイル名を生成"""
        sanitized_query = self.sanitize_filename(query)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{sanitized_query}_{image_id}_{timestamp}.jpg"
    
    def download_image(self, image_data, query, output_dir=DEFAULT_OUTPUT_DIR):
        """画像をダウンロード"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 中解像度の画像URLを取得
        image_url = image_data['src']['medium']
        image_id = image_data['id']
        
        # ファイル名生成
        filename = self.generate_filename(query, image_id)
        file_path = os.path.join(output_dir, filename)
        
        # 画像ダウンロード
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ 画像ダウンロード完了: {file_path}")
            return file_path
        else:
            print(f"❌ 画像ダウンロード失敗: {filename}")
            return None
    
    def fetch_image_for_text(self, text, output_dir=DEFAULT_OUTPUT_DIR):
        """テキスト内容に応じた画像を取得"""
        print(f"🔍 検索対象テキスト: {text[:50]}...")
        
        # 日本語クエリを処理
        split_query = self.split_japanese_query(text)
        english_query = self.translate_to_english(split_query)
        print(f"🌐 英語クエリ: {english_query}")
        
        # 画像検索
        search_results = self.search_images(english_query)
        if not search_results:
            return None
        
        # 最適な画像を選択
        best_image = self.get_best_image(search_results)
        if not best_image:
            print("⚠️  適切な画像が見つかりませんでした")
            return None
        
        # 画像ダウンロード
        return self.download_image(best_image, english_query, output_dir)

def main():
    """メイン関数"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python pexels_image_fetcher.py \"検索クエリ\" [出力ディレクトリ]")
        sys.exit(1)
    
    query = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_DIR
    
    fetcher = PexelsImageFetcher()
    image_path = fetcher.fetch_image_for_text(query, output_dir)
    
    if image_path:
        print(f"🎉 成功: {image_path}")
    else:
        print("❌ 画像取得に失敗しました")

if __name__ == "__main__":
    main() 