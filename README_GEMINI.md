# SUB to SRT Multi-language Translator with Gemini 2.5 Pro

Gemini 2.5 Pro APIを使用してSUBファイルをSRTファイルに変換し、複数言語に翻訳するプログラムです。

## 特徴

- **高品質翻訳**: Gemini 2.5 Proによる文脈を考慮した自然な翻訳
- **多言語対応**: 英語、韓国語、中国語繁体字など7言語をサポート
- **全文一括翻訳**: 100万トークンのコンテキストで全体の文脈を維持
- **安全な処理**: 順次翻訳と同時翻訳の選択が可能
- **無料利用可能**: Gemini 2.5 Pro実験版で無料利用可能

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

**方法1: 環境変数**
```bash
export GEMINI_API_KEY='your_api_key_here'
```

**方法2: コマンドライン引数**
```bash
python sub_to_srt_gemini.py sample.sub en --api-key your_api_key_here
```

## 使用方法

### 基本的な使用方法

```bash
# 英語に翻訳
python sub_to_srt_gemini.py sample.sub en

# 複数言語に翻訳（推奨：順次翻訳）
python sub_to_srt_gemini.py sample.sub en,ko,zh-tw

# 同時翻訳（高速だが制限リスクあり）
python sub_to_srt_gemini.py sample.sub en,ko,zh-tw --mode simultaneous
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

- **Gemini 2.5 Pro実験版**: 無料（制限あり）
- **sample.subサイズ**: 完全に無料範囲内
- **大容量ファイル**: 有料版への移行が必要な場合あり

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

**開発者向け情報**

このプログラムは以下の技術を使用しています：
- Google Generative AI Python SDK
- Gemini 2.5 Pro API
- 正規表現によるテキスト解析
- レート制限とエラーハンドリング