#!/bin/bash

# 共通関数ライブラリ
# 朝用・夜用ニュース動画生成スクリプトで使用される共通関数

# カラー定数
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[1;33m'
readonly COLOR_RED='\033[0;31m'
readonly COLOR_NC='\033[0m' # No Color

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

# 固定画像設定チェック関数
check_fixed_images() {
    print_info "固定画像設定をチェック中..."
    if [ -f "config/fixed_images_config.json" ]; then
        print_success "固定画像設定済み"
        
        # 設定ファイルの詳細を表示
        if command -v jq >/dev/null 2>&1; then
            local opening_image=$(jq -r '.opening_image' config/fixed_images_config.json)
            local closing_image=$(jq -r '.closing_image' config/fixed_images_config.json)
            local created_at=$(jq -r '.created_at' config/fixed_images_config.json)
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
}

# JSON構文チェック関数
check_json_syntax() {
    local json_file="$1"
    print_info "JSON構文をチェック中..."
    
    if ! python3 -m json.tool "$json_file" > /dev/null 2>&1; then
        print_error "JSON構文エラーが検出されました"
        return 1
    fi
    
    print_success "JSON構文OK"
    return 0
}

# beats数カウント関数
count_beats() {
    local json_file="$1"
    python3 -c "
import json
with open('$json_file', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(len(data.get('beats', [])))
"
}

# Token使用量予測表示
show_token_prediction() {
    local beats_count="$1"
    
    if [ -f "config/fixed_images_config.json" ]; then
        local new_images=$((beats_count - 2))
        echo "💰 Token使用予測: 新規画像生成 ${new_images}枚 + 固定画像再利用 2枚"
    else
        echo "💰 Token使用予測: 全画像新規生成 ${beats_count}枚"
    fi
}

# ファイル整理関数
organize_output_files() {
    local base_name="$1"
    local output_movie_dir="$2"
    
    print_info "ファイルを整理中..."
    
    # 動画ファイルを移動
    if [ -f "output/${base_name}_ja__ja.mp4" ]; then
        mv "output/${base_name}_ja__ja.mp4" "$output_movie_dir/${base_name}.mp4"
        print_success "動画ファイル移動完了: $output_movie_dir/${base_name}.mp4"
    else
        print_warning "動画ファイルが見つかりません"
    fi
    
    # 音声ファイルを移動
    if [ -f "output/${base_name}.mp3" ]; then
        mv "output/${base_name}.mp3" "$output_movie_dir/${base_name}.mp3"
    fi
    
    # studio.jsonファイルを移動
    local studio_json="output/${base_name}_studio.json"
    if [ -f "$studio_json" ]; then
        mv "$studio_json" "$output_movie_dir/${base_name}_studio.json"
    fi
}

# 生成統計表示
show_generation_stats() {
    local beats_count="$1"
    
    print_info "生成統計:"
    echo "- beats数: $beats_count (目標: 7-11)"
    
    # 構成の内訳を表示
    if [ "$beats_count" -ge 3 ]; then
        local main_beats=$((beats_count - 2))
        echo "- 構成: オープニング(1) + 本文($main_beats) + クロージング(1)"
    else
        echo "- 構成: 全体($beats_count)"
    fi
    
    if [ -f "config/fixed_images_config.json" ]; then
        local new_images=$((beats_count - 2))
        echo "- Token節約: 固定画像再利用 2枚 / 新規生成 ${new_images}枚"
        echo "- 固定画像設定: ✅ 有効"
    else
        echo "- Token節約: ❌ 無効"
    fi
}

# YouTube目次生成
generate_youtube_chapters() {
    local base_name="$1"
    local output_movie_dir="$2"
    
    print_status "YouTube目次を生成中..."
    local latest_studio="$output_movie_dir/${base_name}_studio.json"
    
    if [ -f "$latest_studio" ]; then
        python3 tools/youtube_chapters.py "$latest_studio" "$output_movie_dir" "$base_name"
        
        if [ $? -eq 0 ]; then
            print_success "YouTube目次生成完了！"
            
            # 生成されたチャプターファイルを表示
            local chapters_file="$output_movie_dir/${base_name}_youtube_chapters.txt"
            local description_file="$output_movie_dir/${base_name}_youtube_description.txt"
            
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
}

# 最終完了メッセージ
print_completion_message() {
    local output_movie_dir="$1"
    local base_name="$2"
    
    echo ""
    print_success "すべて完了！"
    echo "📂 出力ディレクトリ: $output_movie_dir"
    echo "📄 ベースファイル名: $base_name"
    echo "📋 YouTube用ファイル: ${base_name}_youtube_*.txt"
} 