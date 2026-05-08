# VSA Phase2-Core

Version 0.1.0


## 概要

VSA Phase 2 は Phase 1 のクリーン・リライトです。

- 単一ソース・オブ・トゥルース: Google Sheets Master Leads
- 4層アーキテクチャ
- マイグレーション対応
- スケーラビリティ


## CLI コマンド

vsa --help
vsa version
vsa migrate --mode dry-run


## Milestone 1: Foundation

- Python プロジェクト構造作成
- pyproject.toml, .env.example
- 6層アーキテクチャ
- MasterLeadsColumns (52列)
- Enum定義 (21種類)
- MasterLead dataclass (52フィールド)
- CLIフレームワーク
- テストスイート (7/7 PASS)


## Milestone 2: Google Sheets Integration

- Google Sheets API クライアント
- Row ↔ Model 変換ロジック
- Google Sheets Repository 実装
- Enum定義拡張 (21種類)
- 列定数拡張 (52列)
- MasterLead モデル完成
- 統合テスト (9/9 PASS)


## Milestone 3: Migration Script

- Extractor: Phase 1 データ抽出
- Normalizer: URL正規化、Enum マッピング
- Matcher: 重複リード検出
- Merger: 優先度ルール適用
- Loader: Master Leads へのロード
- Orchestrator: 全パイプライン統合
- 実装: 1,682行追加、16/16 テスト PASS


## テスト結果

16 passed in 1.34s

- test_constants.py: 2
- test_converters.py: 9
- test_enums.py: 2
- test_models.py: 2
- test_settings.py: 1

Warnings: 0


## プロジェクト構成

src/vsa/
├── config/settings.py
├── shared/constants.py, enums.py
├── domain/models.py
├── application/migration_*.py (6ファイル)
├── infrastructure/sheets_*.py, repository.py, converters.py
└── interfaces/cli.py, logging_setup.py

tests/
├── test_constants.py
├── test_converters.py
├── test_enums.py
├── test_models.py
└── test_settings.py


## Master Leads (52列)

A-L: 識別・運用 (12列)
lead_id, record_status, lead_stage, canonical_company_name, corp_type, industry, company_prefecture, owner, lead_rank, ng_flag, sales_status, memo

M-T: YouTube Discovery (8列)
youtube_channel_id, youtube_channel_url, youtube_channel_name, youtube_handle, youtube_description, youtube_external_links, youtube_discovered_at, youtube_scrape_status

U-AC: 公式サイト (9列)
official_url, official_domain, official_site_status, official_company_name, official_company_name_source_url, company_address, source_type, source_name, source_url

AD-AL: クロール制御 (9列)
crawl_enabled, crawl_scope, crawl_target_pages, crawl_priority, last_crawled_at, crawl_status, pages_scanned, crawl_error_code, crawl_error_message

AM-AV: 連絡先抽出 (10列)
phone_number, phone_source_url, phone_confidence, official_email, email_source_url, email_confidence, contact_form_url, contact_form_status, contact_form_required_fields, contact_evidence_summary

AW-BG: 検証・営業可否 (11列)
email_validation_status, email_validation_score, email_validation_provider, email_validation_at, email_sendable, form_sendable, preferred_outreach_channel, contactability_status, outreach_ready, outreach_block_reason, next_action

BH-BP: 営業実行サマリ (9列)
last_contacted_at, last_contact_channel, last_contact_result, email_contact_count, form_contact_count, reply_count, last_reply_at, deal_status, next_contact_at

BQ-BU: 統合・監査 (5列)
identity_confidence, primary_source_type, primary_source_ref, created_at, updated_at


## マイグレーション優先度ルール

- canonical_company_name: official_site > CRM > YouTube
- official_url: verified > candidate
- phone_number, email: official_site pipeline のみ採用
- 重複検出: domain, URL, company_name ベース


## 次のマイルストーン (Milestone 4)

- A) Official Site Enrichment
- B) YouTube Discovery
- C) Validation & Contactability
- D) Documentation


## ドキュメント

- docs/architecture/overview.md
- docs/architecture/data-model.md
- docs/migration/migration-plan.md
- docs/implementation/roadmap.md

---

Version: 0.1.0
Last Updated: 2026-05-08
Repository: https://github.com/nario0715masa0619-create/video-sales-automation-phase2

