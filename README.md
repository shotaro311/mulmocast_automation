# 📺 毎日投資ニュース動画自動化システム

毎日の投資・経済ニュースの台本から動画とYouTube用目次を完全自動生成するシステムです。

## 🚀 クイックスタート

### 1. 初回セットアップ（一度だけ）
```bash
# 固定画像を生成してtoken節約を有効化
python3 tools/setup_fixed_images.py
```

### 2. 毎日の動画生成
```bash
# 朝用ニュース動画生成
./quick_news_video.sh "台本テキスト"

# 夜用ニュース動画生成（夜の挨拶文を使用）
./quick_evening_news_video.sh "台本テキスト"
```

## 📁 ディレクトリ構造

```
mulmocast/
├── quick_news_video.sh          # 朝用ニュース動画生成スクリプト
├── quick_evening_news_video.sh  # 夜用ニュース動画生成スクリプト
├── .env                         # API設定
├── README.md                    # このファイル
├── tools/                       # 各種ツール
│   ├── text_to_mulmo.py        # 台本→JSON変換
│   ├── youtube_chapters.py     # YouTube目次生成
│   └── setup_fixed_images.py   # 固定画像セットアップ
├── config/                      # 設定ファイル
│   └── fixed_images_config.json # 固定画像設定
├── output/                      # 生成結果
│   └── movie/                  # 整理された出力ファイル
│       ├── news_YYYYMMDD_HHMMSS/      # 朝用動画フォルダ（時刻別）
│       │   ├── news_YYYYMMDD_HHMMSS.mp4              # 動画ファイル
│       │   ├── news_YYYYMMDD_HHMMSS_studio.json      # mulmocast内部ファイル
│       │   ├── news_YYYYMMDD_HHMMSS_youtube_chapters.txt    # チャプター一覧
│       │   ├── news_YYYYMMDD_HHMMSS_youtube_description.txt # YouTube説明文
│       │   └── news_YYYYMMDD_HHMMSS.mp3              # 音声ファイル
│       └── evening_news_YYYYMMDD_HHMMSS/  # 夜用動画フォルダ（時刻別）
│           ├── evening_news_YYYYMMDD_HHMMSS.mp4      # 動画ファイル
│           └── （同様のファイル構成）
│   └── images/                 # 生成画像（共有）
└── docs/                       # ドキュメント
    └── mulmo_manual.md         # mulmocastマニュアル
```

## ✨ 機能

### 🎬 **動画自動生成**
- 台本テキスト → mulmocastスクリプト形式に自動変換
- beats数を7-11範囲に自動調整
- 内容に応じた画像プロンプト自動生成
- 日本語音声・字幕付き動画出力
- **時間帯別対応**: 朝用・夜用の挨拶文切り替え

### 💰 **Token節約機能**
- オープニング・クロージング用固定画像を再利用
- API呼び出し削減（2枚分節約）
- 初回セットアップ後は永続的に効果

### 📋 **YouTube目次自動生成**
- 実際の内容に基づいた具体的なチャプター名
- 正確なタイムスタンプ付き
- コピペ用YouTube説明文テンプレート
- OP/EDチャプター除外で本編のみ
- 重複チャプター名の自動統合

### 📁 **整理された出力管理**
- **時刻ベースファイル命名**（`news_YYYYMMDD_HHMMSS`）で上書き防止
- `output/movie/`ディレクトリに集約
- 動画・音声・チャプター・説明文を一括管理
- **同日複数動画対応**: 各動画が独立したフォルダに保存

## 📊 生成例

### 出力ファイル構成
```
# 朝用動画（例：2025年6月21日 08:30:15 生成）
output/movie/news_20250621_083015/news_20250621_083015.mp4              # 動画ファイル
output/movie/news_20250621_083015/news_20250621_083015_youtube_chapters.txt     # チャプター一覧
output/movie/news_20250621_083015/news_20250621_083015_youtube_description.txt  # YouTube説明文

# 夜用動画（例：2025年6月21日 21:45:30 生成）
output/movie/evening_news_20250621_214530/evening_news_20250621_214530.mp4      # 動画ファイル
output/movie/evening_news_20250621_214530/evening_news_20250621_214530_youtube_chapters.txt  # チャプター一覧
```

### 動画チャプター（OP/ED除外）
```
0:17 💹 日銀政策・金利動向
0:22 🏠 住宅ローン対策（固定化検討）
0:26 💼 新NISA制度の活用状況
0:37 📈 株式市場の動向
```

## 🛠️ 技術仕様

- **mulmocast-cli**: AI動画生成エンジン
- **Python 3**: 台本処理・目次生成
- **ffmpeg**: 動画エンコーディング
- **OpenAI API**: 画像・音声生成
- **PATH設定**: `/opt/homebrew/bin` 必須

## 📈 効率化実績

- **作業時間**: 手動5分 → 自動3分
- **Token節約**: 固定画像2枚再利用
- **品質向上**: beats数自動調整で安定品質
- **YouTube対応**: 目次自動生成でUX向上
- **ファイル管理**: 時刻ベース命名で上書き防止・複数動画対応

## 🔧 トラブルシューティング

### よくある問題
1. **ffmpeg not found**: `brew install ffmpeg`
2. **API Error**: `.env`ファイルのAPIキー確認
3. **固定画像エラー**: `python3 tools/setup_fixed_images.py`再実行

### 設定確認
```bash
# 固定画像設定の確認
python3 tools/setup_fixed_images.py check

# 生成ファイルの確認（最新のフォルダ）
ls -la output/movie/news_*/
ls -la output/movie/evening_news_*/
```

---

**🎉 これで毎日の投資ニュース動画作成が完全自動化されました！**
