# Migration Plan

## 1. 目的

Phase1 のデータ資産を、Phase2 の `Master Leads` を中心とする構造へ安全に移行する。  
対象はコード移植ではなく、**ルールとデータの移行**である。

---

## 2. 移行の前提

### Phase1 の主なデータソース
- CRM シート
  - YouTube 起点の情報を保持
- Phase5 シート
  - 公式 URL 起点のスクレイピング結果を保持
- SQLite / ログ
  - phase5_data.db
  - send logs
  - validation logs

### Phase2 の移行先
- `Master Leads`
- 補助ログ群
  - `Crawl Evidence`
  - `Validation Log`
  - `Outreach Log`（将来用）

---

## 3. 基本方針

1. 旧システムは当面読み取り専用として扱う
2. 新システムの正本は Master Leads
3. 移行は一括一発ではなく、段階的に行う
4. 同値判定・正規化・重複除去を行う
5. 不確実データは manual review に逃がす

---

## 4. 移行ステップ

### Step 1: Extract
旧システムからデータを抽出する。
- CRM シート
- Phase5 シート
- Phase1 DB
- ログ

### Step 2: Normalize
- URL 正規化
- ドメイン抽出
- `"None"` → 空欄
- 空白トリム
- enum 再マッピング
- datetime フォーマット統一

### Step 3: Match
同一 lead を突合する。

推奨キー優先順:
1. `official_domain`
2. `official_url`
3. 会社名 + URL
4. `youtube_channel_id`
5. 手動確認対象

### Step 4: Merge
優先ルールに従って current state を作る。

採用の原則:
- 公式サイト由来 > YouTube 由来
- 手動確定 > 自動推定
- 検証済み > 未検証

### Step 5: Load
Master Leads に投入する。

### Step 6: Verify
件数・欠損率・重複率を検証する。

---

## 5. 代表的な変換ルール

### 会社名
採用順:
1. 手動確定
2. 公式サイトの会社名
3. CRM 上の会社名
4. YouTube チャンネル名

### official_url
採用順:
1. 手動確定 URL
2. Phase5 URL
3. CRM / YouTube 由来候補 URL

### email
採用順:
1. 検証済み official_email
2. official site 由来 email
3. その他は manual review

### lead_stage
- YouTube 情報のみ → `discovered_from_youtube`
- official_url あり → `official_url_identified`
- official site crawl 済み → `official_site_scraped`
- 連絡先あり → `contact_extracted`
- validation 済み → `validated`
