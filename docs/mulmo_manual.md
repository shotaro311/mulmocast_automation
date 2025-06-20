# 🎬 mulmocast（マルモキャスト）完全マニュアル

## 📋 目次
1. [mulmocastとは？](#mulmocastとは)
2. [必要な環境・準備](#必要な環境準備)
3. [基本的な使い方](#基本的な使い方)
4. [コマンド詳細解説](#コマンド詳細解説)
5. [実践例・ワークフロー](#実践例ワークフロー)
6. [トラブルシューティング](#トラブルシューティング)
7. [応用テクニック](#応用テクニック)

---

## 🎯 mulmocastとは？

**mulmocast（マルモキャスト）**は、中島聡さん（元Microsoft、Windows 95設計者）が開発した**AIマルチモーダル動画生成ツール**です。

### ✨ 何ができるの？
- 📝 **テキスト** → 🎬 **動画** への完全自動変換
- 🎵 **AI音声合成**（ナレーション自動生成）
- 🖼️ **AI画像生成**（シーンに合った画像を自動作成）
- 📄 **PDFスライド**や🎙️**ポッドキャスト**も生成可能

### 💡 従来との違い
| 従来の動画制作 | mulmocast |
|---|---|
| 数時間〜数日 | **約5分** |
| 高額な編集ソフト必要 | **約1ドル** |
| 専門知識必要 | **テキストを書くだけ** |
| 手動編集 | **完全自動** |

---

## 🛠️ 必要な環境・準備

### 📋 事前準備チェックリスト
- [ ] **Node.js** がインストール済み
- [ ] **ffmpeg** がインストール済み
- [ ] **OpenAI APIキー** を取得済み
- [ ] **ElevenLabs APIキー** を取得済み（音声合成用、オプション）

### 🔧 インストール手順

#### 1. mulmocast-cliのインストール
```bash
npm install -g mulmocast-cli
```

#### 2. インストール確認
```bash
mulmo --version
```

#### 3. APIキー設定
プロジェクトフォルダに`.env`ファイルを作成：
```bash
OPENAI_API_KEY=sk-xxxxxx
ELEVENLABS_API_KEY=elevenlabs-xxxxxx  # オプション
```

---

## 🚀 基本的な使い方

### 📝 Step 1: 台本（MulmoScript）の作成

#### 方法A: ChatGPTで自動生成（推奨）
```bash
# 1. プロンプト生成（自動でクリップボードにコピー）
mulmo tool prompt -t business

# 2. ChatGPTにプロンプトを貼り付け
# 3. 生成されたスクリプトをコピー
```

#### 方法B: 手動でJSONスクリプト作成
```json
{
  "title": "サンプル動画",
  "scenes": [
    {
      "narration": "こんにちは、今日は素晴らしい一日ですね",
      "image_prompt": "beautiful sunny day with blue sky"
    }
  ]
}
```

### 🎬 Step 2: 動画生成
```bash
# クリップボードから直接生成（最も簡単）
mulmo movie __clipboard

# ファイルから生成
mulmo movie script.json
```

### 📁 Step 3: 結果確認
```
output/
├── script_20250101_123456.json  # 生成されたスクリプト
├── script_20250101_123456.mp3   # 音声ファイル
├── script_20250101_123456.mp4   # 完成動画
├── audio/                       # 音声素材
└── images/                      # 生成画像
```

---

## 📚 コマンド詳細解説

### 🎬 `mulmo movie` - 動画生成
**最も重要なコマンド。テキストから動画を生成します。**

```bash
# 基本形
mulmo movie <ファイル名>

# 主要オプション
mulmo movie script.json -l ja        # 日本語音声
mulmo movie script.json -c ja        # 日本語字幕
mulmo movie script.json -l ja -c ja  # 日本語音声+字幕
mulmo movie __clipboard              # クリップボードから直接
```

### 🛠️ `mulmo tool` - ツール群
**スクリプト作成やプロンプト生成に使用**

```bash
# プロンプト生成（テンプレート別）
mulmo tool prompt -t business      # ビジネス向け
mulmo tool prompt -t ghibli_strips # ジブリ風
mulmo tool prompt -t children_book # 子供向け絵本
mulmo tool prompt -t comic_strips  # コミック風

# その他のツール
mulmo tool schema                   # スクリプト書式確認
mulmo tool story_to_script story.txt # テキストから変換
```

### 🎵 個別生成コマンド
```bash
mulmo audio script.json    # 音声のみ生成
mulmo images script.json   # 画像のみ生成
mulmo pdf script.json      # PDFスライド生成
mulmo translate script.json # 翻訳
```

---

## 💼 実践例・ワークフロー

### 🎯 Case 1: ビジネスプレゼン動画
```bash
# 1. ビジネス向けプロンプト生成
mulmo tool prompt -t business

# 2. ChatGPTで以下のような指示
# "Create a presentation about AI in healthcare"

# 3. 生成されたスクリプトで動画作成
mulmo movie __clipboard -l ja -c ja
```

### 🎨 Case 2: ジブリ風ストーリー動画
```bash
# 1. ジブリ風プロンプト生成
mulmo tool prompt -t ghibli_strips

# 2. ChatGPTで物語を生成
# 3. 動画化
mulmo movie __clipboard
```

### 📚 Case 3: 教育コンテンツ
```bash
# 1. 子供向けプロンプト生成
mulmo tool prompt -t children_book

# 2. 教育的な内容でスクリプト生成
# 3. 日本語で動画作成
mulmo movie __clipboard -l ja -c ja
```

### 🔄 Case 4: ブログ記事の動画化
```bash
# 1. 既存のテキストファイルから変換
mulmo tool story_to_script blog_article.txt

# 2. 生成されたスクリプトで動画化
mulmo movie generated_script.json
```

---

## 🆘 トラブルシューティング

### ❌ よくあるエラーと対処法

#### 1. `mulmo: command not found`
**原因**: インストールが不完全
**対処法**:
```bash
npm install -g mulmocast-cli
# または
npx mulmocast --version
```

#### 2. `ffmpeg not found`
**原因**: ffmpegがインストールされていない
**対処法**:
```bash
# macOS
brew install ffmpeg

# Windows
# https://ffmpeg.org からダウンロードしてPATH設定
```

#### 3. `OpenAI API Error`
**原因**: APIキーの設定ミス
**対処法**:
```bash
# .envファイルを確認
cat .env
# OPENAI_API_KEY=sk-... が正しく設定されているか確認
```

#### 4. 動画生成が途中で止まる
**原因**: メモリ不足、API制限
**対処法**:
```bash
# ドライラン実行でテスト
mulmo movie script.json --dryRun

# 強制再実行
mulmo movie script.json --force
```


---

## 🎨 **全テンプレート完全ガイド（ver0.0.16対応）**

mulmocastでは19種類のテンプレートが用意されています。用途に応じて最適なテンプレートを選択できます。

### **📊 ビジネス・プレゼンテーション系**

#### 🏢 **business**
```bash
mulmo tool prompt -t business > script.json
```
**概要**: ビジネスプレゼンテーション用テンプレート  
**用途**: 企業発表、営業資料、戦略説明  
**出力**: スライド形式（テキスト、表、グラフ、図表対応）  
**特徴**: Markdown、Mermaid図、Chart.js対応、TailwindCSS使用可能

#### 💻 **coding**
```bash
mulmo tool prompt -t coding > script.json
```
**概要**: 技術プレゼンテーション用テンプレート  
**用途**: 技術解説、コードレビュー、開発者向け発表  
**出力**: コードハイライト付きスライド  
**特徴**: TypeScript/JavaScript/Python等のコード表示、複数言語対応

#### 🎙️ **podcast_standard**
```bash
mulmo tool prompt -t podcast_standard > script.json
```
**概要**: ポッドキャスト番組用テンプレート  
**用途**: 音声コンテンツ、ラジオ番組風動画  
**出力**: 音声中心、シンプルな画像構成  
**特徴**: 複数話者対応、BGM設定可能

---

### **🎬 映像・動画系**

#### 🎥 **realistic_movie**
```bash
mulmo tool prompt -t realistic_movie > script.json
```
**概要**: リアルな映像作品用テンプレート  
**用途**: ドキュメンタリー、解説動画、教育コンテンツ  
**出力**: 写実的な映像（1536×1024）  
**特徴**: 動画プロンプト対応、シネマティック表現

#### 📱 **shorts**
```bash
mulmo tool prompt -t shorts > script.json
```
**概要**: YouTube Shorts用テンプレート  
**用途**: 縦型ショート動画、TikTok、Instagram Reels  
**出力**: 縦型動画（720×1280）  
**特徴**: フック重視の構成、動画プロンプト対応

#### 🎬 **trailer**
```bash
mulmo tool prompt -t trailer > script.json
```
**概要**: 映画予告編用テンプレート  
**用途**: 作品のトレーラー、プロモーション動画  
**出力**: シネマティック映像（1280×720）  
**特徴**: BGM付き、各シーン5秒構成、ドラマティック演出

#### 🖼️ **portrait_movie**
```bash
mulmo tool prompt -t portrait_movie > script.json
```
**概要**: ポートレート動画用テンプレート  
**用途**: 人物紹介、インタビュー動画  
**出力**: 人物中心の映像構成

---

### **📚 コミック・ストーリー系**

#### 📖 **children_book**
```bash
mulmo tool prompt -t children_book > script.json
```
**概要**: 児童書・絵本用テンプレート  
**用途**: 子供向けコンテンツ、教育動画、読み聞かせ  
**出力**: 温かみのある手描き風イラスト（1536×1024）  
**特徴**: 日本語対応、物語性重視、各ページに詳細な画像プロンプト

#### 🎌 **akira_comic**
```bash
mulmo tool prompt -t akira_comic > script.json
```
**概要**: AKIRA風コミック用テンプレート  
**用途**: SF・サイバーパンク系コンテンツ  
**出力**: AKIRA美学のコミック風動画  
**特徴**: 専用キャラクター画像、近未来的表現

#### 🌸 **ghibli_comic**
```bash
mulmo tool prompt -t ghibli_comic > script.json
```
**概要**: ジブリ風コミック用テンプレート  
**用途**: ファンタジー、自然系コンテンツ  
**出力**: ジブリスタイルのアニメ風動画  
**特徴**: 専用プレゼンター画像、温かい表現

#### 🎭 **comic_strips**
```bash
mulmo tool prompt -t comic_strips > script.json
```
**概要**: アメリカンコミック用テンプレート  
**用途**: ユーモア系コンテンツ、オフィス系ネタ  
**出力**: 1990年代アメリカ職場ユーモア風  
**特徴**: ミニマルなライン、落ち着いた色調

#### 👻 **ghost_comic**
```bash
mulmo tool prompt -t ghost_comic > script.json
```
**概要**: ホラー・ゴースト系コミック用テンプレート  
**用途**: ホラーコンテンツ、怖い話  
**出力**: ゴシック・ダーク系表現

#### 🏴‍☠️ **onepiece_comic**
```bash
mulmo tool prompt -t onepiece_comic > script.json
```
**概要**: ワンピース風コミック用テンプレート  
**用途**: 冒険系、少年漫画風コンテンツ  
**出力**: 少年漫画スタイル

#### 🤖 **drslump_comic**
```bash
mulmo tool prompt -t drslump_comic > script.json
```
**概要**: Dr.スランプ風コミック用テンプレート  
**用途**: ギャグ系、コメディコンテンツ  
**出力**: 鳥山明風ギャグ漫画スタイル

#### 🎬 **ghibli_shorts**
```bash
mulmo tool prompt -t ghibli_shorts > script.json
```
**概要**: ジブリ風ショート動画用テンプレート  
**用途**: 短編アニメ風コンテンツ  
**出力**: ジブリスタイルの短編動画

---

### **📝 テキスト・シンプル系**

#### 📄 **text_only**
```bash
mulmo tool prompt -t text_only > script.json
```
**概要**: テキストのみ用テンプレート  
**用途**: シンプルな解説、音声重視コンテンツ  
**出力**: テキストベースの最小構成  
**特徴**: 画像生成なし、高速処理

#### 🖼️ **text_and_image**
```bash
mulmo tool prompt -t text_and_image > script.json
```
**概要**: テキスト＋画像用テンプレート  
**用途**: 基本的な解説動画、教育コンテンツ  
**出力**: テキストスライド＋関連画像

---

### **🎓 教育・解説系**

#### 👨‍🏫 **sensei_and_taro**
```bash
mulmo tool prompt -t sensei_and_taro > script.json
```
**概要**: 先生と生徒の対話形式テンプレート  
**用途**: 教育コンテンツ、Q&A形式の解説  
**出力**: 対話形式の教育動画  
**特徴**: 複数キャラクター、会話形式

---

### **💡 テンプレート選択のコツ**

| 用途 | おすすめテンプレート | 理由 |
|------|-------------------|------|
| **企業プレゼン** | `business` | グラフ・表・図表対応 |
| **技術解説** | `coding` | コードハイライト機能 |
| **YouTube動画** | `shorts` | 縦型フォーマット対応 |
| **子供向け** | `children_book` | 温かいイラスト |
| **ストーリー** | `ghibli_comic` | 物語性のある表現 |
| **教育** | `sensei_and_taro` | 対話形式で理解しやすい |
| **音声重視** | `podcast_standard` | 音質・BGM最適化 |
| **高速作成** | `text_only` | 最小構成で高速 |

### **🔄 テンプレート切り替え方法**
```bash
# テンプレート確認
mulmo tool prompt -t テンプレート名

# 実際の生成
mulmo tool prompt -t business > business_script.json
mulmo movie business_script.json
```

---

## 🎨 応用テクニック

### 🔧 高度な設定

#### カスタム出力ディレクトリ
```bash
mulmo movie script.json -o ./my_videos/
```

#### 詳細ログ出力
```bash
mulmo movie script.json --verbose
```

#### プレゼンテーションスタイル指定
```bash
mulmo movie script.json -p "professional"
```

### 📝 MulmoScript カスタマイズ

#### 基本構造
```json
{
  "title": "動画タイトル",
  "description": "動画の説明",
  "scenes": [
    {
      "narration": "ナレーション内容",
      "image_prompt": "画像生成用プロンプト",
      "duration": 5,
      "background_music": "optional"
    }
  ],
  "style": {
    "voice": "professional",
    "image_style": "realistic"
  }
}
```

### 🎵 音声・画像のカスタマイズ

#### 音声設定
```json
{
  "voice_settings": {
    "language": "ja",
    "speed": 1.0,
    "pitch": 0,
    "voice_id": "specific_voice"
  }
}
```

#### 画像スタイル統一
```json
{
  "image_settings": {
    "style": "anime, studio ghibli style",
    "quality": "high",
    "aspect_ratio": "16:9"
  }
}
```

### 🔄 バッチ処理
```bash
# 複数ファイルを一括処理
for file in scripts/*.json; do
  mulmo movie "$file" -l ja -c ja
done
```

### 📊 品質管理

#### テスト実行
```bash
# 実際に生成せずに設定確認
mulmo movie script.json --dryRun --verbose
```

#### 段階的生成
```bash
# 1. 画像のみ生成して確認
mulmo images script.json

# 2. 音声のみ生成して確認  
mulmo audio script.json

# 3. 問題なければ動画生成
mulmo movie script.json
```

---

## 📈 効率化のコツ

### ⚡ 作業スピードアップ

1. **テンプレート活用**: よく使うスタイルはプロンプトテンプレートとして保存
2. **クリップボード活用**: `__clipboard` を積極的に使用
3. **バッチ処理**: 複数コンテンツは一括生成
4. **段階確認**: 画像→音声→動画の順で段階的にチェック

### 💰 コスト最適化

1. **ドライラン活用**: `--dryRun` で事前確認
2. **画像再利用**: 同じ画像プロンプトは使い回し
3. **音声最適化**: 短いセンテンスに分割して効率化

### 🎯 品質向上

1. **具体的なプロンプト**: 画像生成は詳細に指定
2. **ナレーション調整**: 読みやすい文章を心がける
3. **スタイル統一**: 一貫したトーンを維持

---

## 🔗 参考リンク

- **公式GitHub**: https://github.com/receptron/mulmocast-cli
- **OpenAI API**: https://platform.openai.com/api-keys
- **ElevenLabs**: https://www.elevenlabs.io/
- **ffmpeg**: https://ffmpeg.org/

---

## 📞 サポート・コミュニティ

問題が解決しない場合は：
1. **GitHub Issues**: バグ報告・機能要望
2. **公式ドキュメント**: 最新情報を確認
3. **コミュニティ**: 他のユーザーと情報交換

---

**🎉 これでmulmocastマスターです！素晴らしい動画コンテンツを作成してください！**
