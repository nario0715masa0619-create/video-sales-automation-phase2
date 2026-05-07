# Data Model

## 1. 目的

このドキュメントは、Phase2 の `Master Leads` タブを実装・運用するための正式な列仕様を定義する。  
ここでのルールは、Google Sheets 上の列定義、コードの DTO / domain model、migration script のすべてに共通で適用する。

---

## 2. 基本原則

### 2.1 1 行の意味
- **1 行 = 1 営業対象 lead**

### 2.2 source of truth
- current state の正本は `Master Leads`
- 履歴は補助ログへ分離

### 2.3 値の扱い
- `"None"` 文字列は禁止
- 未設定は空欄
- 未判定は enum で表す
- 真偽値は `TRUE/FALSE`
- 日時は `YYYY-MM-DD HH:MM:SS`

### 2.4 URL
- 正規化して保存する
- `https` 優先
- 末尾スラッシュの扱いを統一する
- 不要なクエリは除去する

---

## 3. Master Leads の主要フィールド群

### A〜L: 識別・運用基本情報
- `lead_id`
- `record_status`
- `lead_stage`
- `canonical_company_name`
- `corp_type`
- `industry`
- `company_prefecture`
- `owner`
- `lead_rank`
- `ng_flag`
- `sales_status`
- `memo`

### M〜T: YouTube discovery 情報
- `youtube_channel_id`
- `youtube_channel_url`
- `youtube_channel_name`
- `youtube_handle`
- `youtube_description`
- `youtube_external_links`
- `youtube_discovered_at`
- `youtube_scrape_status`

### U〜AC: 公式サイト・流入元情報
- `official_url`
- `official_domain`
- `official_site_status`
- `official_company_name`
- `official_company_name_source_url`
- `company_address`
- `source_type`
- `source_name`
- `source_url`

### AD〜AL: クロール制御・実行結果
- `crawl_enabled`
- `crawl_scope`
- `crawl_target_pages`
- `crawl_priority`
- `last_crawled_at`
- `crawl_status`
- `pages_scanned`
- `crawl_error_code`
- `crawl_error_message`

### AM〜AV: 連絡先抽出結果
- `phone_number`
- `phone_source_url`
- `phone_confidence`
- `official_email`
- `email_source_url`
- `email_confidence`
- `contact_form_url`
- `contact_form_status`
- `contact_form_required_fields`
- `contact_evidence_summary`

### AW〜BG: 検証・営業可否
- `email_validation_status`
- `email_validation_score`
- `email_validation_provider`
- `email_validation_at`
- `email_sendable`
- `form_sendable`
- `preferred_outreach_channel`
- `contactability_status`
- `outreach_ready`
- `outreach_block_reason`
- `next_action`

### BH〜BP: 営業実行サマリ
- `last_contacted_at`
- `last_contact_channel`
- `last_contact_result`
- `email_contact_count`
- `form_contact_count`
- `reply_count`
- `last_reply_at`
- `deal_status`
- `next_contact_at`

### BQ〜BU: 統合・監査
- `identity_confidence`
- `primary_source_type`
- `primary_source_ref`
- `created_at`
- `updated_at`

---

## 4. 採用ルール

### canonical_company_name
優先順:
1. `official_company_name`
2. CRM 上の会社名
3. YouTube チャンネル名

### official_url
優先順:
1. 手動確定 URL
2. 公式サイトとして検証済み URL
3. YouTube 外部リンクから抽出された候補 URL

### phone_number / official_email / contact_form_url
- official site pipeline 由来のみを採用対象とする
- discovery 系の値は evidence としては保持しても、採用列には直接入れない

### outreach_ready
`TRUE` にする条件の基本案:
- `record_status = active`
- `ng_flag = FALSE`
- `sales_status NOT IN (won, lost, ng)`
- `contactability_status != unreachable`
- `official_site_status = verified` が望ましい

---

## 5. 補助ログに分けるもの

### Outreach Log
- 実行日時
- チャネル
- 実行結果
- エラー
- 実行 ID

### Crawl Evidence
- 抽出値
- 抽出元 URL
- confidence
- 抽出日時

### Validation Log
- provider
- status
- score
- raw_response_ref
- checked_at
