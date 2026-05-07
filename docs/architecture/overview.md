# Architecture Overview

## 1. このドキュメントの目的

Phase2 のアーキテクチャ全体像を定義する。  
主な目的は以下。

- Master Leads を中心としたデータフローの明確化
- 2 系統の収集パイプラインの責務分離
- source-of-truth の統一
- Phase2-Core と後続機能の境界明確化
- 別 AI 実装者が迷わずコードに落とせる状態を作る

---

## 2. 全体設計の要点

Phase2 は「営業自動化の土台」を作るフェーズである。  
この段階では、**収集・統合・判定**までを担当し、**送信実行**は後段に分ける。

### Phase2-Core の責務
- YouTube 起点の候補情報収集
- 公式 URL の保持
- 公式サイトクロール
- 会社名 / 電話 / メール / 問い合わせフォーム URL 抽出
- 検証結果の保持
- 営業可否の現在状態整理
- Master Leads の整合性維持
- migration の実行

### 後段機能の責務
- メール送信
- 問い合わせフォーム送信
- 実行履歴管理
- 再送制御
- 応答分析

---

## 3. Source of Truth ルール

### 正本
- `Master Leads` タブ

### 移行元
- 旧 CRM シート
- 旧 Phase5 シート
- Phase1 DB / ログ

### 補助ログ
- `Outreach Log`
- `Crawl Evidence`
- `Validation Log`

### 原則
1. 現在状態は必ず `Master Leads` に集約する
2. 履歴は Master Leads に埋め込まない
3. 同じ概念を複数箇所で手入力しない
4. システム更新対象は原則 Master Leads のみ
5. 旧シートは参照専用とし、段階的に更新停止する

---

## 4. 論理パイプライン

### 4.1 YouTube Discovery Pipeline

入力:
- YouTube チャンネル情報
- 概要欄
- 外部リンク
- 既存 CRM データ

出力:
- YouTube 起点の候補 lead
- 公式 URL 候補
- 候補企業名
- 初期ステージ

Master Leads への主な反映列:
- `youtube_channel_id`
- `youtube_channel_url`
- `youtube_channel_name`
- `youtube_handle`
- `youtube_description`
- `youtube_external_links`
- `primary_source_type`
- `lead_stage`

### 4.2 Official Site Enrichment Pipeline

入力:
- `official_url`
- `official_domain`
- クロールポリシー
- discovery 済み lead

出力:
- 会社名
- 住所
- 電話番号
- メールアドレス
- 問い合わせフォーム URL
- クロール状態
- 抽出根拠

Master Leads への主な反映列:
- `official_url`
- `official_domain`
- `official_company_name`
- `company_address`
- `phone_number`
- `official_email`
- `contact_form_url`
- `crawl_status`
- `lead_stage`

---

## 5. システムレイヤ構成

```text
interfaces
  └─ CLI / job entrypoint

application
  └─ use cases / orchestration

domain
  └─ business models / rules / policies

infrastructure
  └─ Google Sheets / crawler / parser / validation / logging / storage
```

### interfaces
- CLI コマンド定義
- バッチ実行入口
- dry-run / plan モード制御

### application
- ユースケースの順序制御
- DTO / port の接続
- エラー伝播の整理

### domain
- Lead モデル
- 統合ルール
- 営業可否判定ルール
- ステージ遷移ルール

### infrastructure
- Google Sheets 操作
- クローラ実装
- 抽出ロジック
- 検証サービス接続
- ログ保存

---

## 6. 想定ユースケース一覧

### Core ユースケース
1. `ingest_youtube_leads`
2. `resolve_official_url`
3. `plan_crawl_targets`
4. `crawl_official_site`
5. `extract_contact_evidence`
6. `merge_lead_state`
7. `validate_email`
8. `recompute_contactability`
9. `sync_master_leads`
10. `migrate_phase1_data`

### 後段ユースケース
1. `plan_outreach_targets`
2. `send_email`
3. `submit_contact_form`
4. `record_outreach_result`

---

## 7. ステージ遷移

推奨 `lead_stage`:
- `discovered_from_youtube`
- `official_url_identified`
- `official_site_scraped`
- `contact_extracted`
- `validated`
- `outreach_ready`
- `contacted`
- `archived`

---

## 8. 設計上の重要ルール

- 収集は 2 系統、管理は 1 系統
- Master Leads は source of truth
- 履歴と current state を分離する
- outreach 実装は Core に混ぜない
- Phase1 のコードではなく、Phase1 の知見を移行する
