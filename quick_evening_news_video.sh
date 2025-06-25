#!/bin/bash

# 夜用ニュース動画生成スクリプト
# 使用方法: ./quick_evening_news_video.sh "台本テキスト"

# エラーハンドリングを有効化
set -e

if [ $# -eq 0 ]; then
    echo "❌ 使用方法: ./quick_evening_news_video.sh \"台本テキスト\""
    echo "例: ./quick_evening_news_video.sh \"今日の重要ニュース...\""
    exit 1
fi

# PATHにHomebrewのbinディレクトリを追加
export PATH="/opt/homebrew/bin:$PATH"

# 引数から台本テキストを取得
SCRIPT_TEXT="$1"

echo "🌙 夜用ニュース動画生成を開始します..."
echo "📝 台本: ${SCRIPT_TEXT:0:50}..."

# タイムスタンプでファイル名を生成
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="evening_news_script_${TIMESTAMP}.json"

echo "🔄 mulmocastスクリプト生成中..."

# text_to_mulmo.pyを使用してスクリプト生成（夜用）
python3 tools/text_to_mulmo.py "$SCRIPT_TEXT" "$OUTPUT_FILE" "evening"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "❌ スクリプトファイルの生成に失敗しました"
    exit 1
fi

echo "🎬 動画生成中..."

# mulmoを使用して動画生成
mulmo movie "$OUTPUT_FILE" -l ja -c ja

if [ $? -eq 0 ]; then
    echo "✅ 夜用ニュース動画の生成が完了しました！"
    echo "📁 スクリプトファイル: $OUTPUT_FILE"
    echo "📂 動画ファイルは output/ ディレクトリに保存されました"
    
    # YouTube章節ファイルも自動生成
    echo "📋 YouTube章節ファイル生成中..."
    STUDIO_FILE="output/${OUTPUT_FILE%.*}_studio.json"
    if [ -f "$STUDIO_FILE" ]; then
        python3 tools/youtube_chapters.py "$STUDIO_FILE"
        echo "✅ YouTube章節ファイルも生成完了"
    else
        echo "⚠️  studio.jsonが見つかりません。YouTube章節は手動で生成してください。"
    fi
    
else
    echo "❌ 動画生成に失敗しました"
    exit 1
fi

echo "🎉 夜用ニュース動画の生成が完了しました！"
echo "💡 動画の確認後、YouTubeにアップロードしてください" 