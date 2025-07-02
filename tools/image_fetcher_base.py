#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像取得の共通基底クラス
"""

import os
import sys
import requests
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple

# パス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_processing_utils import JapaneseAnalyzer, QueryGenerator, FilenameGenerator

class BaseImageFetcher(ABC):
    """画像取得の基底クラス"""
    
    def __init__(self):
        """初期化"""
        self.japanese_analyzer = JapaneseAnalyzer()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    @abstractmethod
    def search_api(self, query: str, per_page: int = 10) -> List[Dict]:
        """APIで画像を検索（各サービスで実装）
        
        Args:
            query: 検索クエリ
            per_page: 1ページあたりの取得数
            
        Returns:
            画像データのリスト
        """
        pass
    
    @abstractmethod
    def score_image(self, image: Dict, keywords: List[str]) -> float:
        """画像を採点（各サービスで実装）
        
        Args:
            image: 画像データ
            keywords: キーワードリスト
            
        Returns:
            画像のスコア（0-100）
        """
        pass
    
    @abstractmethod
    def download_image(self, image: Dict, output_dir: str, filename: str) -> str:
        """画像をダウンロード（各サービスで実装）
        
        Args:
            image: 画像データ
            output_dir: 出力ディレクトリ
            filename: ファイル名
            
        Returns:
            ダウンロードしたファイルのパス
        """
        pass
    
    def extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出
        
        Args:
            text: 抽出対象のテキスト
            
        Returns:
            重み付きキーワードのリスト
        """
        try:
            # 日本語解析
            japanese_keywords = self.japanese_analyzer.split_japanese_query(text)
            
            # 英語翻訳
            english_keywords = self._translate_keywords(japanese_keywords)
            
            # テック系キーワードの重み付け
            weighted_keywords = self._apply_tech_weights(english_keywords)
            
            return weighted_keywords
            
        except Exception as e:
            print(f"❌ キーワード抽出エラー: {e}")
            return ["technology(3.0)", "innovation(3.0)", "business(2.0)"]
    
    def _translate_keywords(self, keywords: List[str]) -> List[str]:
        """キーワードを英語に翻訳"""
        try:
            from googletrans import Translator
            translator = Translator()
            
            english_keywords = []
            for keyword in keywords:
                if self._is_japanese(keyword):
                    try:
                        translated = translator.translate(keyword, src='ja', dest='en')
                        english_keywords.append(translated.text.lower())
                    except:
                        english_keywords.append(keyword)
                else:
                    english_keywords.append(keyword.lower())
            
            return english_keywords
            
        except ImportError:
            print("⚠️  googletransがインストールされていません。日本語キーワードをそのまま使用します。")
            return keywords
        except Exception as e:
            print(f"⚠️  翻訳エラー: {e}")
            return keywords
    
    def _is_japanese(self, text: str) -> bool:
        """テキストが日本語かどうかを判定"""
        japanese_chars = re.compile(r'[ひらがなカタカナ漢字]+')
        return bool(japanese_chars.search(text))
    
    def _apply_tech_weights(self, keywords: List[str]) -> List[str]:
        """テック系キーワードに重み付けを適用"""
        tech_keywords = {
            'ai': 4.0, 'artificial intelligence': 4.0, 'machine learning': 4.0,
            'technology': 3.5, 'tech': 3.5, 'digital': 3.5, 'innovation': 3.5,
            'software': 3.0, 'hardware': 3.0, 'computer': 3.0, 'programming': 3.0,
            'data': 3.0, 'algorithm': 3.0, 'automation': 3.0, 'robot': 3.5,
            'cloud': 3.0, 'internet': 2.5, 'mobile': 2.5, 'app': 2.5,
            'startup': 2.5, 'business': 2.0, 'finance': 2.0, 'investment': 2.0,
            'apple': 3.5, 'google': 3.5, 'microsoft': 3.5, 'meta': 3.5,
            'openai': 4.0, 'chatgpt': 4.0, 'claude': 4.0, 'siri': 3.5,
            'iphone': 3.0, 'android': 3.0, 'instagram': 2.5, 'whatsapp': 2.5,
            'cloudflare': 3.0, 'security': 3.0, 'cybersecurity': 3.5
        }
        
        weighted_keywords = []
        for keyword in keywords:
            weight = tech_keywords.get(keyword.lower(), 2.0)
            weighted_keywords.append(f"{keyword}({weight})")
        
        # 重み順でソート
        weighted_keywords.sort(key=lambda x: float(x.split('(')[1].rstrip(')')), reverse=True)
        
        return weighted_keywords[:10]
    
    def generate_search_queries(self, weighted_keywords: List[str]) -> List[str]:
        """検索クエリを生成"""
        return QueryGenerator.generate_search_queries(weighted_keywords)
    
    def fetch_smart_image(self, text: str, output_dir: str) -> Optional[str]:
        """スマート画像取得のメインメソッド
        
        Args:
            text: 検索対象のテキスト
            output_dir: 出力ディレクトリ
            
        Returns:
            ダウンロードした画像のパス（失敗時はNone）
        """
        try:
            print(f"🔍 画像検索開始: {text[:50]}...")
            
            # 出力ディレクトリを作成
            os.makedirs(output_dir, exist_ok=True)
            
            # キーワード抽出
            keywords = self.extract_keywords(text)
            print(f"🏷️  抽出キーワード: {keywords[:5]}")
            
            # 検索クエリ生成
            queries = self.generate_search_queries(keywords)
            
            # 各クエリで画像を検索
            all_images = []
            for query in queries:
                try:
                    images = self.search_api(query)
                    all_images.extend(images)
                    print(f"🔍 クエリ '{query}': {len(images)}枚取得")
                except Exception as e:
                    print(f"⚠️  クエリ '{query}' でエラー: {e}")
                    continue
            
            if not all_images:
                print("❌ 画像が見つかりませんでした")
                return None
            
            print(f"📊 合計 {len(all_images)}枚の画像を取得")
            
            # 画像を採点
            scored_images = []
            for i, image in enumerate(all_images):
                print(f"🔍 画像 {i+1}/{len(all_images)} を処理中: ID={image.get('id', 'unknown')}")
                
                # 必要なフィールドの存在確認
                if not self._validate_image_data(image):
                    print(f"⚠️  不完全な画像データをスキップ: {image.get('id', 'unknown')}")
                    continue
                    
                try:
                    score = self.score_image(image, keywords)
                    scored_images.append((image, score))
                    print(f"📊 画像ID {image.get('id', 'unknown')}: {score:.1f}点")
                except Exception as e:
                    print(f"❌ 画像採点エラー (ID: {image.get('id', 'unknown')}): {e}")
                    continue
            
            if not scored_images:
                print("❌ 採点可能な画像がありませんでした")
                return None
            
            # 最高スコアの画像を選択
            best_image, best_score = max(scored_images, key=lambda x: x[1])
            print(f"🏆 最高スコア: {best_score:.1f}点の画像を選択")
            
            # ファイル名生成
            filename = self._generate_filename(text, best_image)
            
            # 画像をダウンロード
            downloaded_path = self.download_image(best_image, output_dir, filename)
            
            if downloaded_path:
                print(f"✅ 画像ダウンロード完了: {downloaded_path}")
                return downloaded_path
            else:
                print("❌ 画像ダウンロードに失敗しました")
                return None
                
        except Exception as e:
            print(f"❌ 画像取得エラー: {e}")
            return None
    
    def _validate_image_data(self, image: Dict) -> bool:
        """画像データの妥当性をチェック（各サービスでオーバーライド可能）"""
        required_fields = ['id']
        return all(key in image for key in required_fields)
    
    def _generate_filename(self, text: str, image: Dict) -> str:
        """ファイル名を生成（各サービスでオーバーライド可能）"""
        image_id = image.get('id', 'unknown')
        prefix = self.__class__.__name__.lower().replace('imagefetcher', '')
        return FilenameGenerator.generate_smart_filename(text, image_id, prefix)
    
    def _download_file(self, url: str, filepath: str) -> bool:
        """ファイルをダウンロードする共通メソッド"""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"❌ ダウンロードエラー: {e}")
            return False

class ImageScoringMixin:
    """画像採点の共通ミックスイン"""
    
    def calculate_resolution_score(self, width: int, height: int, max_score: float = 25.0) -> float:
        """解像度スコアを計算"""
        if width >= 1920 and height >= 1080:
            return max_score
        elif width >= 1200 and height >= 800:
            return max_score * 0.8
        elif width >= 800 and height >= 600:
            return max_score * 0.6
        else:
            return max_score * 0.4
    
    def calculate_aspect_ratio_score(self, width: int, height: int, max_score: float = 20.0) -> float:
        """アスペクト比スコアを計算（16:9を最適とする）"""
        if width > 0 and height > 0:
            aspect_ratio = width / height
            target_ratio = 16/9
            ratio_diff = abs(aspect_ratio - target_ratio)
            
            if ratio_diff < 0.1:
                return max_score
            elif ratio_diff < 0.3:
                return max_score * 0.75
            else:
                return max_score * 0.5
        return 0
    
    def calculate_keyword_relevance_score(self, image_text: str, keywords: List[str], max_score: float = 25.0) -> float:
        """キーワード関連性スコアを計算"""
        if not image_text or not keywords:
            return 0
        
        image_text_lower = image_text.lower()
        matches = 0
        total_weight = 0
        
        for keyword_item in keywords:
            if isinstance(keyword_item, str) and '(' in keyword_item:
                keyword = keyword_item.split('(')[0].lower()
                weight = float(keyword_item.split('(')[1].rstrip(')'))
            else:
                keyword = str(keyword_item).lower()
                weight = 1.0
            
            if keyword in image_text_lower:
                matches += weight
            
            total_weight += weight
        
        if total_weight > 0:
            relevance_ratio = matches / total_weight
            return max_score * relevance_ratio
        
        return 0 