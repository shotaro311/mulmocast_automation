#!/bin/bash

# テック系ニュース動画生成スクリプト（Pexels統合対応）
# 使用方法: ./quick_tech_news_video.sh "台本テキスト" [--use-pexels]

# 共通関数を読み込み
source shared_functions.sh

# 引数チェック
if [ $# -eq 0 ]; then
    print_error "使用方法: $0 \"台本テキスト\" [--use-pexels]"
    echo "例: $0 \"AppleがVision Pro 2を発表...\""
    echo "    $0 \"AppleがVision Pro 2を発表...\" --use-pexels"
    exit 1
fi

# スクリプトの場所を取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 出力ディレクトリを準備
OUTPUT_BASE_DIR="output/movie"
# 日付+時刻ベースのユニークなファイル名を生成
DATETIME_STR=$(date +%Y%m%d_%H%M%S)
BASE_NAME="tech_news_${DATETIME_STR}"
OUTPUT_MOVIE_DIR="$OUTPUT_BASE_DIR/$BASE_NAME"
mkdir -p "$OUTPUT_MOVIE_DIR"

# Pexelsオプションチェック
USE_PEXELS=""
if [[ "$*" == *"--use-pexels"* ]]; then
    USE_PEXELS="--use-pexels"
    print_info "🖼️  Pexels統合モード有効"
fi

print_status "Tech News Video Generator v1.0 (Pexels Integration)"
echo "============================================="
print_info "📁 出力先: $OUTPUT_MOVIE_DIR"
print_info "📄 ベースファイル名: $BASE_NAME"

# 固定画像設定をチェック
check_fixed_images

echo ""

# 台本をmulmocastスクリプトに変換
print_info "台本をmulmocastスクリプトに変換中..."
echo "🎯 beats数調整: 7-11cut範囲"
echo "🎪 ジャンル: テクノロジーニュース"

# 固定画像設定の有無を表示
if [ -f "config/fixed_images_config.json" ]; then
    echo "💰 token節約: ✅ 有効"
else
    echo "💰 token節約: ❌ 無効"
fi

# Pexels統合状況を表示
if [ -n "$USE_PEXELS" ]; then
    echo "🖼️  画像取得: Pexels API使用"
else
    echo "🖼️  画像取得: AI生成プロンプト使用"
fi

# 台本テキストを取得（--use-pexelsを除去）
SCRIPT_TEXT="${1}"

# Python スクリプトを実行して台本を変換
if [ -n "$USE_PEXELS" ]; then
    python3 tools/text_to_mulmo_with_pexels.py "$SCRIPT_TEXT" morning $USE_PEXELS
else
    python3 tools/text_to_mulmo_with_pexels.py "$SCRIPT_TEXT" morning
fi

if [ $? -ne 0 ]; then
    print_error "台本変換に失敗しました"
    exit 1
fi

# 最新の生成されたJSONファイルを取得
if [ -n "$USE_PEXELS" ]; then
    latest_json=$(ls -t tech_pexels_script_*.json 2>/dev/null | head -n 1)
else
    latest_json=$(ls -t tech_script_*.json 2>/dev/null | head -n 1)
fi

if [ -z "$latest_json" ]; then
    print_error "変換されたJSONファイルが見つかりません"
    exit 1
fi

# JSONファイルを新しい命名規則でリネーム
renamed_json="${BASE_NAME}.json"
cp "$latest_json" "$renamed_json"

# JSON構文チェック
if ! check_json_syntax "$renamed_json"; then
    exit 1
fi

# beats数をカウント
beats_count=$(count_beats "$renamed_json")
echo "📊 生成されたbeats数: $beats_count"

# token使用量予測
show_token_prediction "$beats_count"

# PATH設定（ffmpeg用）
export PATH="/opt/homebrew/bin:$PATH"

# 動画生成を実行
print_status "動画生成を開始..."
start_time=$(date "+⏰ 開始時刻: %H:%M:%S")
echo "$start_time"

mulmo movie "$renamed_json" -l ja -c ja

if [ $? -eq 0 ]; then
    end_time=$(date "+⏰ 完了時刻: %H:%M:%S")
    print_success "動画生成完了！"
    echo "$end_time"
    echo ""
    
    # 生成されたファイルを整理
    organize_output_files "$BASE_NAME" "$OUTPUT_MOVIE_DIR"
    
    # 元のJSONファイルをクリーンアップ
    rm -f "$latest_json" "$renamed_json"
    
    print_info "生成されたファイル:"
    ls -lh "$OUTPUT_MOVIE_DIR/${BASE_NAME}.mp4" 2>/dev/null
    ls -lh "$OUTPUT_MOVIE_DIR/${BASE_NAME}_studio.json" 2>/dev/null
    ls -lh "$OUTPUT_MOVIE_DIR/${BASE_NAME}.mp3" 2>/dev/null
    
    echo ""
    
    # 生成統計表示
    show_generation_stats "$beats_count"
    
    # Pexels使用状況を表示
    if [ -n "$USE_PEXELS" ]; then
        echo "- 画像取得: Pexels API使用"
    else
        echo "- 画像取得: AI生成プロンプト使用"
    fi
    
    echo ""
    
    # YouTube目次生成
    generate_youtube_chapters "$BASE_NAME" "$OUTPUT_MOVIE_DIR"
    
    # 完了メッセージ
    print_completion_message "$OUTPUT_MOVIE_DIR" "$BASE_NAME"
    
else
    print_error "動画生成に失敗しました"
    exit 1
fi

echo "🎉 テック系ニュース動画の生成が完了しました！"
echo "💡 動画の確認後、YouTubeにアップロードしてください" 