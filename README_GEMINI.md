# SUB to SRT Multi-language Translator with Gemini 2.5 Flash Preview

Gemini 2.5 Flash Preview APIを使用してSUBファイルをSRTファイルに変換し、複数言語に翻訳するプログラムです。

## 特徴

- **高品質翻訳**: Gemini 2.5 Flash Previewによる文脈を考慮した自然な翻訳
- **多言語対応**: 英語、韓国語、中国語繁体字など7言語をサポート
- **全文一括翻訳**: 大容量コンテキストで全体の文脈を維持
- **日本語対話メニュー**: 初心者でも簡単操作、分かりやすい日本語案内
- **ドラッグ&ドロップ対応**: ファイルをドロップするだけで起動
- **すべて翻訳プリセット**: 英語→韓国語→中国語繁体字を一括実行
- **安全な処理**: 順次翻訳と同時翻訳の選択が可能
- **無料利用可能**: Gemini 2.5 Flash Previewで確実に無料利用可能

## 必要な準備

### 1. 依存関係のインストール

```bash
pip install -r requirements_gemini.txt
```

### 2. Gemini API キーの取得

1. [Google AI Studio](https://aistudio.google.com/)にアクセス
2. "Create API Key"をクリック
3. APIキーをコピー

### 3. APIキーの設定

以下のいずれかの方法でAPIキーを設定：

**方法1: 環境変数（Windows推奨）**
```cmd
setx GEMINI_API_KEY1 "your_api_key_here"
```

**方法2: WSL/Linux環境変数**
```bash
export GEMINI_API_KEY1='your_api_key_here'
```

**方法3: コマンドライン引数**
```bash
python sub_to_srt_gemini.py sample.sub en --api-key your_api_key_here
```

**注意**: 環境変数名は `GEMINI_API_KEY1` です（末尾に1が必要）

## 使用方法

### 新機能！3つの使用方法

#### 1. 対話モード（推奨・初心者向け）
```cmd
python sub_to_srt_gemini.py
```
日本語メニューで簡単操作！ファイル選択から言語選択まで対話形式で完了。

#### 2. ドラッグ&ドロップモード
SUBファイルをプログラムファイル（`sub_to_srt_gemini.py`）にドラッグ&ドロップするだけで起動！

#### 3. コマンドラインモード（上級者向け）
```bash
# 英語に翻訳
python sub_to_srt_gemini.py sample.sub en

# 複数言語に翻訳（推奨：順次翻訳）
python sub_to_srt_gemini.py sample.sub en,ko,zh-tw

# 同時翻訳（高速だが制限リスクあり）
python sub_to_srt_gemini.py sample.sub en,ko,zh-tw --mode simultaneous
```

### 対話モードの使用例

```
==================================================
         字幕翻訳プログラム (Gemini 2.5)
==================================================

翻訳したいSUBファイルのパスを入力してください: sample.sub
✅ ファイル: sample.sub

翻訳言語を選択してください:
0. すべて翻訳 (英語 → 韓国語 → 中国語繁体字)  ← 人気のプリセット！
1. 英語 (English)
2. 韓国語 (Korean)
3. 中国語繁体字 (Traditional Chinese)
...

番号を入力してください: 0
✅ すべて翻訳を選択しました (英語, 韓国語, 中国語繁体字)
```

### オプション

| オプション | 説明 | デフォルト |
|-----------|------|----------|
| `--mode` | 翻訳モード (`batch` または `simultaneous`) | `batch` |
| `--output-dir` | 出力ディレクトリ | 入力ファイルと同じディレクトリ |
| `--api-key` | Gemini APIキー | 環境変数から取得 |

### 対応言語

| 言語コード | 言語名 |
|-----------|--------|
| `en` | English |
| `ko` | Korean |
| `zh-tw` | Traditional Chinese |
| `zh-cn` | Simplified Chinese |
| `es` | Spanish |
| `fr` | French |
| `de` | German |

## 使用例

### 例1: 英語と韓国語に翻訳（安全な順次翻訳）

```bash
python sub_to_srt_gemini.py sample.sub en,ko
```

出力ファイル:
- `sample_en.srt` (英語)
- `sample_ko.srt` (韓国語)

### 例2: 3言語同時翻訳（高速）

```bash
python sub_to_srt_gemini.py sample.sub en,ko,zh-tw --mode simultaneous
```

### 例3: 出力ディレクトリ指定

```bash
python sub_to_srt_gemini.py sample.sub en,ko --output-dir ./translations
```

## 翻訳モードの選択

### 順次翻訳 (batch) - 推奨

**特徴:**
- ✅ 安全で確実
- ✅ API制限にかかりにくい
- ✅ エラー時の復旧が容易
- ❌ 処理時間が長い

**使用例:**
```bash
python sub_to_srt_gemini.py sample.sub en,ko,zh-tw --mode batch
```

### 同時翻訳 (simultaneous)

**特徴:**
- ✅ 高速処理
- ✅ 全言語で文脈一貫性
- ❌ API制限リスク
- ❌ 失敗時に全て失う

**使用例:**
```bash
python sub_to_srt_gemini.py sample.sub en,ko --mode simultaneous
```

## トークン使用量の目安

### あなたのsample.subファイルの場合

**順次翻訳 (3言語):**
- 1言語あたり: 入力800 + 出力1,200 = 2,000トークン
- 3言語合計: 6,000トークン
- **無料範囲内で余裕で利用可能** ✅

**同時翻訳 (3言語):**
- 入力800 + 出力3,600 = 4,400トークン
- **無料範囲内で利用可能** ✅

## エラーハンドリング

プログラムには以下のエラーハンドリング機能があります：

- **レート制限対応**: 自動的に待機時間を調整
- **部分的成功**: 一部の言語が失敗しても他は保存
- **トークン推定**: 事前にトークン使用量を警告
- **エラー詳細表示**: 失敗理由の明確な表示

## トラブルシューティング

### APIキーエラー
```
Error: Gemini API key is required
```
**解決方法**: APIキーを環境変数または--api-keyで設定

### レート制限エラー
```
Rate limiting: waiting 1.0 seconds...
```
**解決方法**: 自動的に待機するため、そのまま待つ

### トークン制限警告
```
Warning: Estimated token usage is high
```
**解決方法**: `--mode batch`を使用するか、ファイルを分割

### 翻訳結果が不完全
```
Expected 8 translations, got 6
```
**解決方法**: `--mode batch`を試すか、再実行

## 料金について

- **Gemini 2.5 Flash Preview**: 無料（明確な無料枠あり）
  - RPM: 10リクエスト/分
  - TPM: 250,000トークン/分  
  - RPD: 500リクエスト/日
- **sample.subサイズ**: 完全に無料範囲内
- **大容量ファイル**: 有料版への移行が必要な場合あり

## モデル選択について

### 利用可能なGeminiモデル

| モデル名 | 無料利用 | 性能 | 備考 |
|---------|----------|------|------|
| `gemini-2.5-flash-preview-05-20` | ✅ 確実 | 高性能 | **現在使用中・推奨** |
| `gemini-2.5-pro-preview-06-05` | ❌ 有料のみ | 最高性能 | 無料枠なし |
| `gemini-1.5-flash` | ✅ あり | 標準 | 安定版 |
| `gemini-1.5-pro` | ✅ あり | 高性能 | 制限が厳しい |

**重要**: Gemini 2.5 Pro Previewは無料枠がないため、現在はGemini 2.5 Flash Previewを使用しています。

## ファイル構成

```
zimaku_sub_to_srt/
├── sub_to_srt_gemini.py          # メインプログラム
├── requirements_gemini.txt        # 依存関係
├── README_GEMINI.md              # このファイル
├── sample.sub                    # 入力ファイル例
├── sample_en.srt                # 出力例（英語）
├── sample_ko.srt                # 出力例（韓国語）
└── sample_zh-tw.srt             # 出力例（中国語繁体字）
```

## 注意事項

1. **無料版の制限**: 厳しいレート制限があるため、大量処理には注意
2. **ネットワーク接続**: インターネット接続が必要
3. **文字エンコーディング**: UTF-8とShift_JISに対応
4. **APIキーの管理**: APIキーは安全に管理してください

---

## セットアップガイド（Windows）

### 1. 仮想環境の準備
```cmd
# 仮想環境を有効化
venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements_gemini.txt
```

### 2. 環境変数の設定（永続的）
```cmd
# APIキーを永続的に設定
setx GEMINI_API_KEY1 "your_api_key_here"

# 設定後、新しいターミナルを開く
```

### 3. プログラムの実行
```cmd
# 仮想環境を有効化
venv\Scripts\activate

# 翻訳実行（環境変数を自動認識）
python sub_to_srt_gemini.py sample.sub en,ko,zh-tw
```

**開発者向け情報**

このプログラムは以下の技術を使用しています：
- Google Generative AI Python SDK
- Gemini 2.5 Flash Preview API (`gemini-2.5-flash-preview-05-20`)
- 正規表現によるテキスト解析
- レート制限とエラーハンドリング
- Windows環境変数管理