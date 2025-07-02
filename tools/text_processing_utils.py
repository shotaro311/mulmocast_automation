#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テキスト処理共通ユーティリティ
"""

import re
from typing import List, Tuple, Optional

# 定数
MIN_SENTENCE_LENGTH = 10
MIN_BEATS = 7
MAX_BEATS = 11
DEFAULT_BEAT_DURATION = 3.0

class TextProcessor:
    """テキスト処理の共通クラス"""
    
    @staticmethod
    def split_text_into_sentences(text: str, detailed_split: bool = False) -> List[str]:
        """テキストを文単位で分割
        
        Args:
            text: 分割対象のテキスト
            detailed_split: より詳細な分割を行うかどうか
            
        Returns:
            分割された文のリスト
        """
        if detailed_split:
            # より詳細な文分割（複数の区切り文字に対応）
            sentences = re.split(r'[。！？]', text)
            sentences = [s.strip() + '。' for s in sentences if s.strip() and len(s.strip()) > MIN_SENTENCE_LENGTH]
            
            # さらに細かく分割するための追加処理
            refined_sentences = []
            for sentence in sentences:
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
        else:
            # 基本的な文分割
            sentences = re.split(r'(?<![0-9])。', text)
            sentences = [s.strip() + '。' for s in sentences if s.strip() and len(s.strip()) > MIN_SENTENCE_LENGTH]
            
            # 最後の文の重複した。を修正
            if sentences:
                sentences[-1] = sentences[-1].replace('。。', '。')
            
            return sentences
    
    @staticmethod
    def combine_sentences(sentences: List[str], target_beats: int) -> List[str]:
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
    
    @staticmethod
    def split_long_sentences(sentences: List[str], aggressive: bool = False) -> List[str]:
        """長い文を分割
        
        Args:
            sentences: 分割対象の文リスト
            aggressive: より積極的に分割するかどうか
            
        Returns:
            分割された文のリスト
        """
        new_sentences = []
        length_threshold = 80 if aggressive else 100
        
        for sentence in sentences:
            if len(sentence) > length_threshold:
                if aggressive:
                    # より積極的な分割
                    parts = re.split(r'[、,また次に最後にさらに例えばそして]', sentence)
                else:
                    # 基本的な分割
                    parts = re.split(r'[、,]', sentence)
                
                if len(parts) > 1:
                    mid = len(parts) // 2
                    part1 = "、".join(parts[:mid]) + "。"
                    part2 = "、".join(parts[mid:])
                    
                    if aggressive and len(part2.strip()) > MIN_SENTENCE_LENGTH:
                        new_sentences.extend([part1, part2])
                    elif not aggressive:
                        new_sentences.extend([part1, part2])
                    else:
                        new_sentences.append(sentence)
                else:
                    new_sentences.append(sentence)
            else:
                new_sentences.append(sentence)
        
        return new_sentences[:MAX_BEATS] if not aggressive else new_sentences
    
    @staticmethod
    def adjust_beats_count(sentences: List[str], verbose: bool = True) -> List[str]:
        """beats数を目標範囲（7-11）に調整
        
        Args:
            sentences: 調整対象の文リスト
            verbose: ログ出力するかどうか
            
        Returns:
            調整された文のリスト
        """
        if verbose:
            print(f"📝 初期文数: {len(sentences)}")
        
        # まず長い文を分割
        sentences = TextProcessor.split_long_sentences(sentences, aggressive=True)
        if verbose:
            print(f"📝 分割後文数: {len(sentences)}")
        
        # 目標範囲内に調整
        if len(sentences) > MAX_BEATS:
            # 文が多すぎる場合は結合
            sentences = TextProcessor.combine_sentences(sentences, MAX_BEATS)
            if verbose:
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
            if verbose:
                print(f"📝 追加分割後文数: {len(sentences)}")
        
        # 最終的に目標範囲内に収める（厳密に）
        if len(sentences) > MAX_BEATS:
            # 強制的にMAX_BEATSに制限
            sentences = sentences[:MAX_BEATS]
            if verbose:
                print(f"📝 上限調整後文数: {len(sentences)}")
        elif len(sentences) < MIN_BEATS:
            # 不足分を最後の文から分割して補完
            sentences = TextProcessor._fill_missing_beats(sentences, verbose)
        
        # 最終確認
        final_count = len(sentences)
        if verbose:
            if final_count < MIN_BEATS or final_count > MAX_BEATS:
                print(f"⚠️  警告: beats数調整が目標範囲外です ({final_count})")
            else:
                print(f"✅ beats数が目標範囲内に調整されました ({final_count})")
        
        return sentences
    
    @staticmethod
    def _fill_missing_beats(sentences: List[str], verbose: bool = True) -> List[str]:
        """不足するbeatsを補完する内部メソッド"""
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
                    if verbose:
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
                        if verbose:
                            print(f"📝 前文分割: {len(sentences)}文に調整")
                    else:
                        break
                else:
                    break
        
        return sentences

class JapaneseAnalyzer:
    """日本語解析の共通クラス"""
    
    def __init__(self):
        """初期化"""
        try:
            from janome.tokenizer import Tokenizer
            self.tokenizer = Tokenizer()
            self.available = True
        except ImportError:
            print("⚠️  janomeがインストールされていません。基本的な分割を使用します。")
            self.tokenizer = None
            self.available = False
    
    def split_japanese_query(self, query: str) -> List[str]:
        """日本語クエリを意味のあるキーワードに分割"""
        try:
            if self.available and self.tokenizer:
                tokens = self.tokenizer.tokenize(query)
                keywords = [token.surface for token in tokens 
                           if token.part_of_speech.split(',')[0] in ['名詞', '動詞', '形容詞'] 
                           and len(token.surface) > 1]
                
                # 重複を除去し、最初の10個まで
                unique_keywords = list(dict.fromkeys(keywords))[:10]
                return unique_keywords
            else:
                return self._fallback_split(query)
                
        except Exception as e:
            print(f"⚠️  日本語解析エラー: {e}")
            return self._fallback_split(query)
    
    def _fallback_split(self, query: str) -> List[str]:
        """フォールバック: 基本的な分割"""
        # カタカナ、ひらがな、漢字、英数字の単語を抽出
        words = re.findall(r'[ァ-ヶー]+|[ひ-ゖ]+|[一-龯]+|[a-zA-Z0-9]+', query)
        return [word for word in words if len(word) > 1][:10]

class QueryGenerator:
    """検索クエリ生成の共通クラス"""
    
    @staticmethod
    def generate_search_queries(weighted_keywords: List[str], max_queries: int = 5) -> List[str]:
        """重み付きキーワードから複数の検索クエリを生成
        
        Args:
            weighted_keywords: 重み付きキーワードのリスト
            max_queries: 最大クエリ数
            
        Returns:
            検索クエリのリスト
        """
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
            keywords = list(dict.fromkeys(keywords))[:max_queries]
            
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
            return queries[:max_queries]
            
        except Exception as e:
            print(f"⚠️  クエリ生成エラー: {e}")
            return ["technology", "innovation", "business"]

class FilenameGenerator:
    """ファイル名生成の共通クラス"""
    
    @staticmethod
    def generate_smart_filename(text: str, image_id: str, prefix: str = "image") -> str:
        """スマートファイル名を生成
        
        Args:
            text: 元テキスト
            image_id: 画像ID
            prefix: ファイル名のプレフィックス
            
        Returns:
            生成されたファイル名
        """
        from datetime import datetime
        
        sanitized_text = re.sub(r'[\\/*?:"<>|]', "_", text[:40])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{sanitized_text}_{image_id}_{timestamp}.jpg"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """ファイル名を安全な形式にサニタイズ"""
        # 危険な文字を置換
        sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
        # 連続するアンダースコアを1つに
        sanitized = re.sub(r'_{2,}', "_", sanitized)
        # 先頭・末尾のアンダースコアを削除
        sanitized = sanitized.strip("_")
        return sanitized 