# Runbook

## 1. 目的

Phase2-Core の運用手順を整理する。  
この段階では、送信運用ではなく、**データ整備・クロール・検証・整合性維持**を対象とする。

---

## 2. 主要タブ

- `Master Leads` : current state の正本
- `Crawl Evidence` : 抽出証拠
- `Validation Log` : 検証履歴
- `Outreach Log` : 将来用
- `Settings` : 列定義 / enum / 設定値

---

## 3. 日常運用でやること

### 3.1 Master Leads の確認
確認項目:
- `record_status = active`
- `lead_stage`
- `official_url`
- `crawl_status`
- `official_email`
- `contact_form_url`
- `contactability_status`
- `outreach_ready`

### 3.2 クロール失敗の確認
確認項目:
- `crawl_status = failed`
- `crawl_error_code`
- `crawl_error_message`

### 3.3 manual review 対象の確認
例:
- `official_site_status = candidate_found`
- `contactability_status = manual_review`
- `record_status = duplicate`

---

## 4. 推奨運用フロー

### migration 前
1. 旧 CRM / 旧 Phase5 を snapshot
2. dry-run migration 実行
3. 件数差分を確認

### migration 後
1. Master Leads 件数確認
2. duplicate 件数確認
3. official_url 欠損率確認
4. manual_review 件数確認

### 日次または任意実行
1. crawl plan
2. crawl run
3. validation 取り込み
4. recompute
5. 差分確認
