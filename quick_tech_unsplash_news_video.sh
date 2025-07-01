#!/bin/bash
#
# テック系ニュース動画自動生成スクリプト（Unsplash統合版）
# 使用方法: ./quick_tech_unsplash_news_video.sh
#
# 主な機能:
# - Unsplash APIによる高品質画像の自動取得
# - テック系ニュースに特化したプロンプト生成
# - 7-11枚の画像を使用した効率的な動画構成
# - YouTube目次自動生成
#

set -e  # エラー時に即座に終了

# 色付きログ出力
log_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

log_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR/tools"
OUTPUT_DIR="$SCRIPT_DIR/output"
CONFIG_DIR="$SCRIPT_DIR/config"

# Unsplash API設定確認
check_unsplash_config() {
    log_info "Unsplash API設定を確認中..."
    
    if [ ! -f "$TOOLS_DIR/unsplash_image_fetcher.py" ]; then
        log_error "Unsplash画像取得ツールが見つかりません: $TOOLS_DIR/unsplash_image_fetcher.py"
        exit 1
    fi
    
    if [ ! -f "$TOOLS_DIR/text_to_mulmo_with_unsplash.py" ]; then
        log_error "Unsplash統合版変換ツールが見つかりません: $TOOLS_DIR/text_to_mulmo_with_unsplash.py"
        exit 1
    fi
    
    # .envファイルの存在確認
    if [ ! -f ".env" ]; then
        log_warning ".envファイルが見つかりません"
        log_info "env.exampleを参考に.envファイルを作成してください:"
        log_info "1. cp env.example .env"
        log_info "2. .envファイルを編集してUnsplash APIキーを設定"
        log_info "3. https://unsplash.com/developers でアクセスキーを取得"
        
        read -p ".envファイルを作成しますか？ (y/N): " -r create_env
        if [[ $create_env =~ ^[Yy]$ ]]; then
            cp env.example .env
            log_success ".envファイルを作成しました"
            log_info ".envファイルを編集してUnsplash APIキーを設定してください"
            read -p "設定後、Enter を押して続行してください..." -r
        else
            log_error ".envファイルが必要です"
            exit 1
        fi
    fi
    
    # 環境変数の設定確認
    source .env 2>/dev/null || true
    if [ -z "$UNSPLASH_ACCESS_KEY" ] || [ "$UNSPLASH_ACCESS_KEY" = "your_unsplash_access_key_here" ]; then
        log_warning "UNSPLASH_ACCESS_KEYが設定されていません"
        log_info ".envファイルを編集してUnsplash APIキーを設定してください"
        log_info "https://unsplash.com/developers でアクセスキーを取得"
        read -p "設定済みの場合は Enter を押して続行してください..." -r
    fi
    
    log_success "Unsplash設定確認完了"
}

# 依存関係チェック
check_dependencies() {
    log_info "依存関係をチェック中..."
    
    # Python依存関係
    python3 -c "import requests, googletrans, janome, dotenv" 2>/dev/null || {
        log_error "必要なPythonライブラリが不足しています"
        log_info "以下のコマンドでインストールしてください:"
        log_info "pip3 install requests googletrans==4.0.0rc1 janome python-dotenv"
        exit 1
    }
    
    # mulmoコマンド確認
    if ! command -v mulmo &> /dev/null; then
        log_error "mulmoコマンドが見つかりません"
        log_info "mulmocastがインストールされていることを確認してください"
        exit 1
    fi
    
    log_success "依存関係チェック完了"
}

# 出力ディレクトリ準備
prepare_directories() {
    log_info "出力ディレクトリを準備中..."
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR/images/unsplash"
    log_success "ディレクトリ準備完了"
}

# テック系ニュース台本のサンプル
get_sample_tech_script() {
    cat << 'EOF'
Appleが新しいSiri機能を発表し、音声アシスタント技術に革新をもたらしています。この改良により、ユーザーとの対話がより自然で直感的になり、日常生活での利便性が大幅に向上すると期待されています。

Metaが新たなAI研究所を設立し、次世代の人工知能開発に本格的に取り組むことを発表しました。この研究所では、大規模言語モデルやマルチモーダルAIの研究開発を進め、メタバースとAIの融合を目指しています。

Cloudflareが新しいウェブサイト保護サービスを開始し、スクレイピングボットからウェブサイトを守る革新的なソリューションを提供しています。このサービスにより、企業のデータ保護とウェブセキュリティが大幅に強化されることが期待されています。
EOF
}

# ユーザー入力取得
get_user_input() {
    log_info "テック系ニュース動画生成を開始します"
    echo
    
    # 台本入力方法の選択
    echo "台本の入力方法を選択してください:"
    echo "1) サンプル台本を使用（推奨・テスト用）"
    echo "2) 自分で台本を入力"
    echo "3) ファイルから台本を読み込み"
    echo
    read -p "選択 (1-3): " -r input_method
    
    case $input_method in
        1)
            SCRIPT_TEXT=$(get_sample_tech_script)
            log_info "サンプル台本を使用します"
            ;;
        2)
            echo "台本テキストを入力してください（複数行可、最後に空行で終了）:"
            SCRIPT_TEXT=""
            while IFS= read -r line; do
                if [[ -z "$line" ]]; then
                    break
                fi
                SCRIPT_TEXT="$SCRIPT_TEXT$line"$'\n'
            done
            ;;
        3)
            read -p "台本ファイルのパスを入力してください: " -r script_file
            if [[ -f "$script_file" ]]; then
                SCRIPT_TEXT=$(cat "$script_file")
                log_info "ファイルから台本を読み込みました: $script_file"
            else
                log_error "ファイルが見つかりません: $script_file"
                exit 1
            fi
            ;;
        *)
            log_error "無効な選択です"
            exit 1
            ;;
    esac
    
    # 時間帯選択
    echo
    echo "動画の時間帯を選択してください:"
    echo "1) 朝用（デフォルト）"
    echo "2) 夜用"
    echo
    read -p "選択 (1-2): " -r time_choice
    
    case $time_choice in
        2)
            TIME_PERIOD="evening"
            log_info "夜用動画として生成します"
            ;;
        *)
            TIME_PERIOD="morning"
            log_info "朝用動画として生成します"
            ;;
    esac
    
    # Unsplash使用確認
    echo
    echo "Unsplash APIを使用しますか？"
    echo "1) はい（推奨・高品質画像）"
    echo "2) いいえ（AI生成プロンプト使用）"
    echo
    read -p "選択 (1-2): " -r unsplash_choice
    
    case $unsplash_choice in
        1)
            USE_UNSPLASH=true
            log_info "Unsplash APIを使用した高品質画像で生成します"
            ;;
        *)
            USE_UNSPLASH=false
            log_info "AI生成プロンプトを使用します"
            ;;
    esac
}

# mulmocastスクリプト生成
generate_mulmo_script() {
    log_info "mulmocastスクリプトを生成中..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    if [ "$USE_UNSPLASH" = true ]; then
        SCRIPT_FILE="tech_unsplash_news_${TIMESTAMP}.json"
        python3 "$TOOLS_DIR/text_to_mulmo_with_unsplash.py" \
            "$SCRIPT_TEXT" \
            "$SCRIPT_FILE" \
            "$TIME_PERIOD" \
            --use-unsplash
    else
        SCRIPT_FILE="tech_news_${TIMESTAMP}.json"
        python3 "$TOOLS_DIR/text_to_mulmo_with_unsplash.py" \
            "$SCRIPT_TEXT" \
            "$SCRIPT_FILE" \
            "$TIME_PERIOD"
    fi
    
    if [[ ! -f "$SCRIPT_FILE" ]]; then
        log_error "スクリプト生成に失敗しました"
        exit 1
    fi
    
    log_success "mulmocastスクリプト生成完了: $SCRIPT_FILE"
}

# 動画生成
generate_video() {
    log_info "動画を生成中..."
    
    # PATH設定（Homebrew対応）
    export PATH="/opt/homebrew/bin:$PATH"
    
    # mulmoコマンド実行
    if mulmo movie "$SCRIPT_FILE" -l ja -c ja; then
        log_success "動画生成完了"
        
        # 生成されたファイルを確認
        VIDEO_FILE=$(find . -name "*.mp4" -newer "$SCRIPT_FILE" | head -1)
        AUDIO_FILE=$(find . -name "*.wav" -newer "$SCRIPT_FILE" | head -1)
        
        if [[ -n "$VIDEO_FILE" ]]; then
            VIDEO_SIZE=$(du -h "$VIDEO_FILE" | cut -f1)
            log_success "動画ファイル: $VIDEO_FILE ($VIDEO_SIZE)"
        fi
        
        if [[ -n "$AUDIO_FILE" ]]; then
            AUDIO_SIZE=$(du -h "$AUDIO_FILE" | cut -f1)
            log_success "音声ファイル: $AUDIO_FILE ($AUDIO_SIZE)"
        fi
        
        # 出力ディレクトリに移動
        if [[ -n "$VIDEO_FILE" ]] && [[ -f "$VIDEO_FILE" ]]; then
            mv "$VIDEO_FILE" "$OUTPUT_DIR/"
            VIDEO_FILE="$OUTPUT_DIR/$(basename "$VIDEO_FILE")"
            log_info "動画ファイルを出力ディレクトリに移動しました"
        fi
        
        if [[ -n "$AUDIO_FILE" ]] && [[ -f "$AUDIO_FILE" ]]; then
            mv "$AUDIO_FILE" "$OUTPUT_DIR/"
            log_info "音声ファイルを出力ディレクトリに移動しました"
        fi
        
    else
        log_error "動画生成に失敗しました"
        exit 1
    fi
}

# YouTube目次生成
generate_youtube_chapters() {
    log_info "YouTube目次を生成中..."
    
    if [[ -f "$SCRIPT_FILE" ]] && [[ -n "$VIDEO_FILE" ]]; then
        CHAPTERS_FILE="${VIDEO_FILE%.*}_youtube_chapters.txt"
        
        if python3 "$TOOLS_DIR/youtube_chapters.py" "$SCRIPT_FILE" > "$CHAPTERS_FILE"; then
            log_success "YouTube目次生成完了: $CHAPTERS_FILE"
            
            echo
            log_info "=== YouTube目次 ==="
            cat "$CHAPTERS_FILE"
            echo
        else
            log_warning "YouTube目次生成に失敗しました"
        fi
    fi
}

# 生成結果サマリー
show_summary() {
    log_info "=== 生成結果サマリー ==="
    
    if [[ -f "$SCRIPT_FILE" ]]; then
        echo "📄 スクリプトファイル: $SCRIPT_FILE"
        BEATS_COUNT=$(jq '.beats | length' "$SCRIPT_FILE" 2>/dev/null || echo "不明")
        echo "📊 beats数: $BEATS_COUNT"
    fi
    
    if [[ -n "$VIDEO_FILE" ]] && [[ -f "$VIDEO_FILE" ]]; then
        VIDEO_SIZE=$(du -h "$VIDEO_FILE" | cut -f1)
        echo "🎬 動画ファイル: $VIDEO_FILE ($VIDEO_SIZE)"
        
        # 動画時間を取得（ffprobeが利用可能な場合）
        if command -v ffprobe &> /dev/null; then
            DURATION=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null | cut -d. -f1)
            if [[ -n "$DURATION" ]] && [[ "$DURATION" -gt 0 ]]; then
                MINUTES=$((DURATION / 60))
                SECONDS=$((DURATION % 60))
                echo "⏱️  動画時間: ${MINUTES}分${SECONDS}秒"
            fi
        fi
    fi
    
    if [ "$USE_UNSPLASH" = true ]; then
        echo "🎨 画像取得: Unsplash API（高品質画像）"
        UNSPLASH_IMAGES=$(find "$OUTPUT_DIR/images/unsplash" -name "*.jpg" -newer "$SCRIPT_FILE" 2>/dev/null | wc -l)
        echo "📸 Unsplash画像数: $UNSPLASH_IMAGES"
    else
        echo "🤖 画像生成: AI生成プロンプト"
    fi
    
    echo "📁 出力ディレクトリ: $OUTPUT_DIR"
    echo
    log_success "テック系ニュース動画生成完了！"
}

# メイン実行
main() {
    log_info "=== テック系ニュース動画生成（Unsplash統合版）==="
    echo
    
    # 事前チェック
    check_unsplash_config
    check_dependencies
    prepare_directories
    
    # ユーザー入力
    get_user_input
    
    # スクリプト生成
    generate_mulmo_script
    
    # 動画生成
    generate_video
    
    # YouTube目次生成
    generate_youtube_chapters
    
    # 結果表示
    show_summary
}

# スクリプト実行
main "$@" 