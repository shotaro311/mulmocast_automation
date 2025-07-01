# 📺 毎日投資ニュース動画自動化システム（Unsplash統合版）

毎日の投資・経済ニュースの台本から動画とYouTube用目次を完全自動生成するシステムです。**Unsplash API統合により高品質な実写画像を使用可能**になりました。

## 🚀 クイックスタート

### 1. 初回セットアップ（一度だけ）

#### API設定
```bash
# 環境変数ファイルを作成
cp env.example .env

# .envファイルを編集してAPIキーを設定
vi .env
```

**必要なAPIキー:**
- **Unsplash API**: [https://unsplash.com/developers](https://unsplash.com/developers)
  - `UNSPLASH_ACCESS_KEY`: アクセスキー
  - `UNSPLASH_SECRET_KEY`: シークレットキー

#### 依存関係インストール
```bash
# Python依存関係のインストール
pip3 install requests googletrans==4.0.0rc1 janome python-dotenv

# 固定画像を生成してtoken節約を有効化
python3 tools/setup_fixed_images.py
```

### 2. 毎日の動画生成

#### 標準版（AI生成プロンプト）
```bash
# 朝用ニュース動画生成
./quick_news_video.sh "台本テキスト"

# 夜用ニュース動画生成（夜の挨拶文を使用）
./quick_evening_news_video.sh "台本テキスト"
```

#### テック系ニュース版
```bash
# テック系ニュース動画生成（Pexels統合）
./quick_tech_news_video.sh

# テック系ニュース動画生成（スマートPexels）
./quick_tech_smart_news_video.sh

# ⭐ テック系ニュース動画生成（Unsplash統合・最高品質）
./quick_tech_unsplash_news_video.sh
```

## 🌟 **新機能: Unsplash統合システム**

### 🎯 **高品質画像選定**
- **AI採点システム**: 100点満点での自動画像評価
  - 解像度（25点）、アスペクト比（20点）、キーワード関連性（25点）
  - 色彩（15点）、いいね数（15点）
- **スマート検索**: 日本語形態素解析→英語翻訳→複数クエリ生成
- **テック系重み付け**: テクノロジー関連キーワードの優先度向上

### 🔧 **技術的特徴**
- **フォールバック機能**: Unsplash失敗時はAI生成プロンプト使用
- **16:9最適化**: 動画用アスペクト比を優先選定
- **API利用規約準拠**: ダウンロード統計の自動送信
- **エラーハンドリング**: 堅牢な例外処理とログ出力

### 📊 **品質向上実績**
- **従来**: AI生成画像（抽象的・アーティスティック）
- **Unsplash版**: 実写高品質画像（具体的・プロフェッショナル）
- **採点例**: 60-82点の詳細スコアリング
- **成功率**: 約65%の画像で正常採点・選定

## 📁 ディレクトリ構造

```
mulmocast/
├── quick_news_video.sh              # 朝用ニュース動画生成スクリプト
├── quick_evening_news_video.sh      # 夜用ニュース動画生成スクリプト
├── quick_tech_unsplash_news_video.sh # ⭐ Unsplash統合テック系動画生成
├── shared_functions.sh              # 共通関数ライブラリ
├── .env                             # API設定（環境変数）
├── env.example                      # 環境変数テンプレート
├── README.md                        # このファイル
├── tools/                           # 各種ツール
│   ├── text_to_mulmo.py            # 台本→JSON変換（リファクタリング済み）
│   ├── text_to_mulmo_with_unsplash.py # ⭐ Unsplash統合版台本変換
│   ├── unsplash_image_fetcher.py    # ⭐ Unsplash画像取得・AI採点
│   ├── pexels_image_fetcher.py      # Pexels画像取得
│   ├── smart_pexels_fetcher.py      # スマートPexels取得
│   ├── youtube_chapters.py          # YouTube目次生成（リファクタリング済み）
│   └── setup_fixed_images.py        # 固定画像セットアップ
├── config/                          # 設定ファイル
│   └── fixed_images_config.json     # 固定画像設定
├── output/                          # 生成結果
│   ├── images/                      # 生成画像
│   │   ├── unsplash/               # ⭐ Unsplash高品質画像
│   │   ├── pexels/                 # Pexels画像
│   │   └── fixed_images_setup/     # 固定画像
│   └── movie/                      # 整理された出力ファイル
│       ├── news_YYYYMMDD_HHMMSS/            # 朝用動画フォルダ（時刻別）
│       │   ├── news_YYYYMMDD_HHMMSS.mp4              # 動画ファイル
│       │   ├── news_YYYYMMDD_HHMMSS_studio.json      # mulmocast内部ファイル
│       │   ├── news_YYYYMMDD_HHMMSS_youtube_chapters.txt    # チャプター一覧
│       │   ├── news_YYYYMMDD_HHMMSS_youtube_description.txt # YouTube説明文
│       │   └── news_YYYYMMDD_HHMMSS.mp3              # 音声ファイル
│       └── evening_news_YYYYMMDD_HHMMSS/    # 夜用動画フォルダ（時刻別）
│           ├── evening_news_YYYYMMDD_HHMMSS.mp4      # 動画ファイル
│           └── （同様のファイル構成）
└── docs/                           # ドキュメント
    ├── mulmo_manual.md             # mulmocastマニュアル
    └── mulmocast_update_log.md     # 更新履歴
```

## ✨ 機能

### 🎬 **動画自動生成**
- 台本テキスト → mulmocastスクリプト形式に自動変換
- beats数を7-11範囲に自動調整
- 内容に応じた画像プロンプト自動生成
- **⭐ Unsplash高品質実写画像**: AI採点による最適画像選定
- 日本語音声・字幕付き動画出力
- **時間帯別対応**: 朝用・夜用の挨拶文切り替え

### 💰 **Token節約機能**
- オープニング・クロージング用固定画像を再利用
- API呼び出し削減（2枚分節約）
- **Unsplash API**: 月間50回まで無料
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

### Unsplash統合版動画例
```
# テック系動画（Unsplash統合）
output/tech_unsplash_final_fixed_ja__ja.mp4    # 1分56秒、3.7MB、HD画質
- Siri/Apple関連: iPhone、Siri、Apple関連の高品質画像
- Meta/AI研究: Meta 3Dロゴ、OpenAI 3Dロゴ
- Instagram/WhatsApp: Instagram画面、ソーシャルメディア画像
- Cloudflare/セキュリティ: クラウド、セキュリティ関連画像
- AI/ロボット: 白いロボット、AI関連画像
```

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
- **⭐ Unsplash API**: 高品質実写画像取得
- **python-dotenv**: 環境変数管理
- **janome**: 日本語形態素解析
- **googletrans**: 自動翻訳
- **PATH設定**: `/opt/homebrew/bin` 必須

## 📈 効率化実績

- **作業時間**: 手動5分 → 自動3分
- **Token節約**: 固定画像2枚再利用
- **品質向上**: beats数自動調整で安定品質
- **⭐ 画像品質**: AI生成 → Unsplash実写高品質画像
- **YouTube対応**: 目次自動生成でUX向上
- **ファイル管理**: 時刻ベース命名で上書き防止・複数動画対応

## 🔧 コード品質・保守性

### リファクタリング実施済み
- **モジュール化**: 長い関数を小さな責務明確な関数に分割
- **定数管理**: ハードコードされた値を定数として定義
- **共通化**: 重複コードを共通関数として抽出
- **可読性向上**: 意味のある関数名・変数名に変更
- **保守性向上**: 変更影響範囲を最小化
- **⭐ 環境変数管理**: セキュアなAPIキー管理

### コード構造
- `shared_functions.sh`: シェルスクリプト共通関数ライブラリ
- `tools/text_to_mulmo.py`: 台本変換エンジン（モジュール化済み）
- `tools/text_to_mulmo_with_unsplash.py`: Unsplash統合版台本変換
- `tools/unsplash_image_fetcher.py`: Unsplash画像取得・AI採点システム
- `tools/youtube_chapters.py`: 目次生成エンジン（辞書ベース設計）

## 🔧 トラブルシューティング

### よくある問題
1. **ffmpeg not found**: `brew install ffmpeg`
2. **API Error**: `.env`ファイルのAPIキー確認
3. **固定画像エラー**: `python3 tools/setup_fixed_images.py`再実行
4. **⭐ Unsplash API Error**: `.env`ファイルのUnsplash APIキー確認

### 設定確認
```bash
# 固定画像設定の確認
python3 tools/setup_fixed_images.py check

# Unsplash API接続確認
python3 tools/unsplash_image_fetcher.py "test"

# 生成ファイルの確認（最新のフォルダ）
ls -la output/movie/news_*/
ls -la output/movie/evening_news_*/
ls -la output/images/unsplash/
```

## 🎯 **今後の展開**

### 完了済み
- ✅ Unsplash API統合
- ✅ AI画像採点システム
- ✅ 日本語対応（形態素解析・翻訳）
- ✅ 環境変数管理
- ✅ エラーハンドリング強化

### 検討中
- 🔄 beats数制御の精密化（目標7-11の厳密遵守）
- 🔄 他の画像プロバイダー統合
- 🔄 動画品質の更なる向上

---

**🎉 これで毎日の投資ニュース動画作成が完全自動化され、Unsplash統合により最高品質の動画が生成可能になりました！**
