#!/bin/bash

# 色付きメッセージ用の関数
print_status() {
    echo "🎬 $1"
}

print_success() {
    echo "✅ $1"
}

print_warning() {
    echo "⚠️  $1"
}

print_error() {
    echo "❌ $1"
}

print_info() {
    echo "📝 $1"
}

# 引数チェック
if [ $# -eq 0 ]; then
    print_error "使用方法: $0 \"台本テキスト\""
    exit 1
fi

# スクリプトの場所を取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 出力ディレクトリを準備
OUTPUT_MOVIE_DIR="output/movie"
mkdir -p "$OUTPUT_MOVIE_DIR"

# 日付ベースのファイル名を生成
DATE_STR=$(date +%Y%m%d)
BASE_NAME="news_${DATE_STR}"

print_status "Quick News Video Generator v2.4 (Organized Output)"
echo "============================================="
print_info "📁 出力先: $OUTPUT_MOVIE_DIR"
print_info "📄 ベースファイル名: $BASE_NAME"

# 固定画像設定をチェック
print_info "固定画像設定をチェック中..."
if [ -f "config/fixed_images_config.json" ]; then
    print_success "固定画像設定済み"
    # 設定ファイルの詳細を表示
    if command -v jq >/dev/null 2>&1; then
        opening_image=$(jq -r '.opening_image' config/fixed_images_config.json)
        closing_image=$(jq -r '.closing_image' config/fixed_images_config.json)
        created_at=$(jq -r '.created_at' config/fixed_images_config.json)
        echo "📁 オープニング画像: $opening_image"
        echo "📁 クロージング画像: $closing_image"
        echo "📅 作成日時: $created_at"
        
        # ファイル存在チェック
        if [ -f "$opening_image" ] && [ -f "$closing_image" ]; then
            print_success "全ての固定画像ファイルが存在します"
        else
            print_warning "一部の固定画像ファイルが見つかりません"
        fi
    fi
else
    print_warning "固定画像が未設定です"
    echo "💡 python3 tools/setup_fixed_images.py を実行してtoken節約を有効にしてください"
fi

echo ""

# 台本をmulmocastスクリプトに変換
print_info "台本をmulmocastスクリプトに変換中..."
echo "🎯 beats数調整: 7-11cut範囲"

# 固定画像設定の有無を表示
if [ -f "config/fixed_images_config.json" ]; then
    echo "💰 token節約: ✅ 有効"
else
    echo "💰 token節約: ❌ 無効"
fi

# Python スクリプトを実行して台本を変換
python3 tools/text_to_mulmo.py "$1"

if [ $? -ne 0 ]; then
    print_error "台本変換に失敗しました"
    exit 1
fi

# 最新の生成されたJSONファイルを取得
latest_json=$(ls -t news_script_*.json 2>/dev/null | head -n 1)

if [ -z "$latest_json" ]; then
    print_error "変換されたJSONファイルが見つかりません"
    exit 1
fi

# JSONファイルを新しい命名規則でリネーム
renamed_json="${BASE_NAME}.json"
cp "$latest_json" "$renamed_json"

print_info "JSON構文をチェック中..."

# JSON構文チェック
if ! python3 -m json.tool "$renamed_json" > /dev/null 2>&1; then
    print_error "JSON構文エラーが検出されました"
    exit 1
fi

print_success "JSON構文OK"

# beats数をカウント
beats_count=$(python3 -c "
import json
with open('$renamed_json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(len(data.get('beats', [])))
")

echo "📊 生成されたbeats数: $beats_count"

# token使用量予測
if [ -f "config/fixed_images_config.json" ]; then
    new_images=$((beats_count - 2))
    echo "💰 Token使用予測: 新規画像生成 ${new_images}枚 + 固定画像再利用 2枚"
else
    echo "💰 Token使用予測: 全画像新規生成 ${beats_count}枚"
fi

# PATH設定（ffmpeg用）
export PATH="/opt/homebrew/bin:$PATH"

# 動画生成を実行
print_status "動画生成を開始..."
start_time=$(date "+⏰ 開始時刻: #%p")
echo "$start_time"

mulmo movie "$renamed_json" -l ja -c ja

if [ $? -eq 0 ]; then
    end_time=$(date "+⏰ 完了時刻: #%p")
    print_success "動画生成完了！"
    echo "$end_time"
    echo ""
    
    # 生成されたファイルをoutput/movie/に移動
    print_info "ファイルを整理中..."
    
    # 動画ファイルを移動
    if [ -f "output/${BASE_NAME}_ja__ja.mp4" ]; then
        mv "output/${BASE_NAME}_ja__ja.mp4" "$OUTPUT_MOVIE_DIR/${BASE_NAME}.mp4"
        print_success "動画ファイル移動完了: $OUTPUT_MOVIE_DIR/${BASE_NAME}.mp4"
    else
        print_warning "動画ファイルが見つかりません"
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
    rm -f "$latest_json" "$renamed_json"
    
    print_info "生成されたファイル:"
    ls -lh "$OUTPUT_MOVIE_DIR/${BASE_NAME}.mp4" 2>/dev/null
    ls -lh "$OUTPUT_MOVIE_DIR/${BASE_NAME}_studio.json" 2>/dev/null
    ls -lh "$OUTPUT_MOVIE_DIR/${BASE_NAME}.mp3" 2>/dev/null
    
    echo ""
    print_info "生成統計:"
    echo "- beats数: $beats_count (目標: 7-11)"
    
    # 構成の内訳を表示
    if [ "$beats_count" -ge 3 ]; then
        main_beats=$((beats_count - 2))
        echo "- 構成: オープニング(1) + 本文($main_beats) + クロージング(1)"
    else
        echo "- 構成: 全体($beats_count)"
    fi
    
    if [ -f "config/fixed_images_config.json" ]; then
        new_images=$((beats_count - 2))
        echo "- Token節約: 固定画像再利用 2枚 / 新規生成 ${new_images}枚"
        echo "- 固定画像設定: ✅ 有効"
    else
        echo "- Token節約: ❌ 無効"
    fi
    
    echo ""
    
    # YouTube目次生成
    print_status "YouTube目次を生成中..."
    latest_studio="$OUTPUT_MOVIE_DIR/${BASE_NAME}_studio.json"
    
    if [ -f "$latest_studio" ]; then
        python3 tools/youtube_chapters.py "$latest_studio" "$OUTPUT_MOVIE_DIR" "$BASE_NAME"
        
        if [ $? -eq 0 ]; then
            print_success "YouTube目次生成完了！"
            
            # 生成されたチャプターファイルを表示
            chapters_file="$OUTPUT_MOVIE_DIR/${BASE_NAME}_youtube_chapters.txt"
            description_file="$OUTPUT_MOVIE_DIR/${BASE_NAME}_youtube_description.txt"
            
            if [ -f "$chapters_file" ]; then
                echo ""
                print_info "📋 YouTube用チャプター:"
                cat "$chapters_file"
                echo ""
                print_info "📁 ファイル出力:"
                echo "- チャプター一覧: $chapters_file"
                echo "- YouTube説明文: $description_file"
            fi
        else
            print_warning "YouTube目次生成に失敗しました"
        fi
    else
        print_warning "studio.jsonファイルが見つかりません"
    fi
    
    echo ""
    print_success "すべて完了！"
    echo "📂 出力ディレクトリ: $OUTPUT_MOVIE_DIR"
    echo "📄 ベースファイル名: $BASE_NAME"
    echo "📋 YouTube用ファイル: ${BASE_NAME}_youtube_*.txt"
    
else
    print_error "動画生成に失敗しました"
    exit 1
fi 