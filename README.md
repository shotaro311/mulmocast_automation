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
# 台本テキストを指定してワンライナー実行
./quick_news_video.sh "台本テキスト"
```

## 📁 ディレクトリ構造

```
mulmocast/
├── quick_news_video.sh          # メイン実行スクリプト
├── .env                         # API設定
├── README.md                    # このファイル
├── tools/                       # 各種ツール
│   ├── text_to_mulmo.py        # 台本→JSON変換
│   ├── youtube_chapters.py     # YouTube目次生成
│   └── setup_fixed_images.py   # 固定画像セットアップ
├── config/                      # 設定ファイル
│   └── fixed_images_config.json # 固定画像設定
├── output/                      # 生成結果
│   ├── *.mp4                   # 動画ファイル
│   ├── *_studio.json           # mulmocast内部ファイル
│   └── images/                 # 生成画像
└── docs/                       # ドキュメント
    └── mulmo_manual.md         # mulmocastマニュアル
```

## ✨ 機能

### 🎬 **動画自動生成**
- 台本テキスト → mulmocastスクリプト形式に自動変換
- beats数を7-11範囲に自動調整
- 内容に応じた画像プロンプト自動生成
- 日本語音声・字幕付き動画出力

### 💰 **Token節約機能**
- オープニング・クロージング用固定画像を再利用
- API呼び出し削減（2枚分節約）
- 初回セットアップ後は永続的に効果

### 📋 **YouTube目次自動生成**
- 実際の内容に基づいた具体的なチャプター名
- 正確なタイムスタンプ付き
- コピペ用YouTube説明文テンプレート

## 📊 生成例

### 動画チャプター
```
0:00 🎬 オープニング・挨拶
0:17 💼 新NISA利用状況（88％が活用）
0:34 📊 新NISA積立額の増加トレンド
0:51 ⚡ 非課税枠完全活用の戦略
1:08 💹 日銀議事要旨（段階的利上げ方針）
1:25 🏠 住宅ローン対策（固定化検討）
1:42 💱 為替動向（円高進行の影響）
1:59 🤖 Microsoft AI戦略（営業利益率最高）
2:16 🍎 Apple関税対策（インド生産転換）
2:33 👍 チャンネル登録のお願い
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

## 🔧 トラブルシューティング

### よくある問題
1. **ffmpeg not found**: `brew install ffmpeg`
2. **API Error**: `.env`ファイルのAPIキー確認
3. **固定画像エラー**: `python3 tools/setup_fixed_images.py`再実行

### 設定確認
```bash
# 固定画像設定の確認
python3 tools/setup_fixed_images.py check

# 生成ファイルの確認
ls -la output/
```

---

**🎉 これで毎日の投資ニュース動画作成が完全自動化されました！**
