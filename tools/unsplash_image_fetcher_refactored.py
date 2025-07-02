#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unsplash画像取得ツール（リファクタリング版）
"""

import os
import sys
import requests
from typing import List, Dict, Optional

# パス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from image_fetcher_base import BaseImageFetcher, ImageScoringMixin

class UnsplashImageFetcher(BaseImageFetcher, ImageScoringMixin):
    """Unsplash画像取得クラス"""
    
    def __init__(self):
        """初期化"""
        super().__init__()
        self.access_key, self.secret_key = self._load_api_keys()
        
        if not self.access_key or not self.secret_key:
            raise ValueError("Unsplash APIキーが設定されていません。.envファイルを確認してください。")
    
    def _load_api_keys(self) -> tuple:
        """環境変数からAPIキーを読み込み"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            access_key = os.getenv('UNSPLASH_ACCESS_KEY')
            secret_key = os.getenv('UNSPLASH_SECRET_KEY')
            
            if not access_key or not secret_key:
                print("❌ Unsplash APIキーが設定されていません")
                print("💡 .envファイルに以下を設定してください:")
                print("   UNSPLASH_ACCESS_KEY=your_access_key")
                print("   UNSPLASH_SECRET_KEY=your_secret_key")
                return None, None
            
            return access_key, secret_key
            
        except ImportError:
            print("❌ python-dotenvがインストールされていません")
            print("💡 pip3 install python-dotenv を実行してください")
            return None, None
        except Exception as e:
            print(f"❌ 環境変数読み込みエラー: {e}")
            return None, None
    
    def search_api(self, query: str, per_page: int = 10) -> List[Dict]:
        """Unsplash APIで画像を検索"""
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {self.access_key}"}
        params = {
            "query": query,
            "per_page": min(per_page, 30),
            "orientation": "landscape"  # 16:9に近い画像を優先
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"🔍 API レスポンス: {len(results)}件の画像を取得")
                return results
            else:
                print(f"⚠️  Unsplash API エラー: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ API検索エラー: {e}")
            return []
    
    def score_image(self, image: Dict, keywords: List[str]) -> float:
        """画像を採点（100点満点）"""
        try:
            score = 0
            
            # 解像度スコア（25点満点）
            width = image.get('width', 0)
            height = image.get('height', 0)
            score += self.calculate_resolution_score(width, height)
            
            # アスペクト比スコア（20点満点）
            score += self.calculate_aspect_ratio_score(width, height)
            
            # キーワード関連性スコア（25点満点）
            description = image.get('description', '') or image.get('alt_description', '') or ''
            tags = image.get('tags', [])
            
            # tagsがNoneの場合のハンドリング
            tag_titles = []
            if tags and isinstance(tags, list):
                tag_titles = [tag.get('title', '') if isinstance(tag, dict) else str(tag) for tag in tags]
            
            all_text = (description + ' ' + ' '.join(tag_titles)).lower()
            score += self.calculate_keyword_relevance_score(all_text, keywords)
            
            # 色彩スコア（15点満点）
            color = image.get('color', '#000000')
            if color and color != '#000000':  # 黒以外の色がある
                score += 15
            else:
                score += 5
            
            # いいね数スコア（15点満点）
            likes = image.get('likes', 0)
            if likes >= 1000:
                score += 15
            elif likes >= 500:
                score += 12
            elif likes >= 100:
                score += 10
            elif likes >= 50:
                score += 8
            else:
                score += 5
            
            return min(score, 100)
            
        except Exception as e:
            print(f"⚠️  画像採点エラー: {e}")
            return 0
    
    def download_image(self, image: Dict, output_dir: str, filename: str) -> Optional[str]:
        """画像をダウンロード"""
        try:
            # 高解像度URLを取得
            urls = image.get('urls', {})
            download_url = urls.get('regular') or urls.get('small') or urls.get('thumb')
            
            if not download_url:
                print("❌ ダウンロードURLが見つかりません")
                return None
            
            # ファイルパス
            filepath = os.path.join(output_dir, filename)
            
            # ダウンロード実行
            if self._download_file(download_url, filepath):
                # Unsplash利用統計を送信
                self._track_download(image.get('id'))
                return filepath
            else:
                return None
                
        except Exception as e:
            print(f"❌ ダウンロードエラー: {e}")
            return None
    
    def _track_download(self, image_id: str):
        """Unsplash利用統計を送信（利用規約準拠）"""
        if not image_id:
            return
        
        try:
            track_url = f"https://api.unsplash.com/photos/{image_id}/download"
            headers = {"Authorization": f"Client-ID {self.access_key}"}
            
            response = self.session.get(track_url, headers=headers, timeout=5)
            if response.status_code == 200:
                print("📊 Unsplash利用統計送信完了")
            else:
                print(f"⚠️  統計送信エラー: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  統計送信エラー: {e}")
    
    def _validate_image_data(self, image: Dict) -> bool:
        """Unsplash画像データの妥当性をチェック"""
        required_fields = ['id', 'width', 'height', 'urls']
        return all(key in image for key in required_fields)
    
    def _generate_filename(self, text: str, image: Dict) -> str:
        """Unsplash用ファイル名を生成"""
        from datetime import datetime
        
        image_id = image.get('id', 'unknown')
        sanitized_text = text[:40].replace('/', '_').replace('\\', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"unsplash_{sanitized_text}_{image_id}_{timestamp}.jpg"

def main():
    """メイン関数（テスト用）"""
    if len(sys.argv) != 2:
        print("使用法: python3 unsplash_image_fetcher_refactored.py <検索テキスト>")
        sys.exit(1)
    
    search_text = sys.argv[1]
    output_dir = "output/images/unsplash"
    
    try:
        fetcher = UnsplashImageFetcher()
        result = fetcher.fetch_smart_image(search_text, output_dir)
        
        if result:
            print(f"✅ 成功: {result}")
        else:
            print("❌ 画像取得に失敗しました")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 