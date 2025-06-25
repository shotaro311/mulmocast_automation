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

# 日付+時刻ベースのユニークなファイル名を生成
DATETIME_STR=$(date +%Y%m%d_%H%M%S)
BASE_NAME="evening_news_${DATETIME_STR}"
OUTPUT_FILE="${BASE_NAME}.json"

# 出力ディレクトリを準備
OUTPUT_BASE_DIR="output/movie"
OUTPUT_MOVIE_DIR="$OUTPUT_BASE_DIR/$BASE_NAME"
mkdir -p "$OUTPUT_MOVIE_DIR"

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
    echo ""
    
    # 生成されたファイルをoutput/movie/に移動
    echo "📁 ファイルを整理中..."
    
    # 動画ファイルを移動
    if [ -f "output/${BASE_NAME}_ja__ja.mp4" ]; then
        mv "output/${BASE_NAME}_ja__ja.mp4" "$OUTPUT_MOVIE_DIR/${BASE_NAME}.mp4"
        echo "✅ 動画ファイル移動完了: $OUTPUT_MOVIE_DIR/${BASE_NAME}.mp4"
    else
        echo "⚠️  動画ファイルが見つかりません"
    fi
    
    # 音声ファイルを移動
    if [ -f "output/${BASE_NAME}.mp3" ]; then
        mv "output/${BASE_NAME}.mp3" "$OUTPUT_MOVIE_DIR/${BASE_NAME}.mp3"
    fi
    
    # studio.jsonファイルを移動
    studio_json="output/${BASE_NAME}_studio.json"
    if [ -f "$studio_json" ]; then
        mv "$studio_json" "$OUTPUT_MOVIE_DIR/${BASE_NAME}_studio.json"
    fi
    
    # 元のJSONファイルをクリーンアップ
    rm -f "$OUTPUT_FILE"
    
    # YouTube章節ファイルも自動生成
    echo "📋 YouTube章節ファイル生成中..."
    latest_studio="$OUTPUT_MOVIE_DIR/${BASE_NAME}_studio.json"
    if [ -f "$latest_studio" ]; then
        python3 tools/youtube_chapters.py "$latest_studio" "$OUTPUT_MOVIE_DIR" "$BASE_NAME"
        echo "✅ YouTube章節ファイルも生成完了"
        
        # 生成されたチャプターファイルを表示
        chapters_file="$OUTPUT_MOVIE_DIR/${BASE_NAME}_youtube_chapters.txt"
        description_file="$OUTPUT_MOVIE_DIR/${BASE_NAME}_youtube_description.txt"
        
        if [ -f "$chapters_file" ]; then
            echo ""
            echo "📋 YouTube用チャプター:"
            cat "$chapters_file"
            echo ""
            echo "📁 ファイル出力:"
            echo "- チャプター一覧: $chapters_file"
            echo "- YouTube説明文: $description_file"
        fi
    else
        echo "⚠️  studio.jsonが見つかりません。YouTube章節は手動で生成してください。"
    fi
    
    echo ""
    echo "✅ すべて完了！"
    echo "📂 出力ディレクトリ: $OUTPUT_MOVIE_DIR"
    echo "📄 ベースファイル名: $BASE_NAME"
    echo "📋 YouTube用ファイル: ${BASE_NAME}_youtube_*.txt"
    
else
    echo "❌ 動画生成に失敗しました"
    exit 1
fi

echo "🎉 夜用ニュース動画の生成が完了しました！"
echo "💡 動画の確認後、YouTubeにアップロードしてください" 