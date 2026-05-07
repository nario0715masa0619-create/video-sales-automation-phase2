# video-sales-automation-phase2

営業自動化基盤の Phase2 リポジトリです。  
Phase1 の実運用知見を引き継ぎつつ、コード・データモデル・Google スプレッドシート運用を整理し直し、**拡張しやすい土台**を作ることを目的とします。

## 目的

Phase1 では、以下の流れで営業活動を支える自動化が実装されていました。

- CRM シートに YouTube 起点の情報を蓄積
- 公式 URL を抽出して Phase5 シートへ連携
- 公式サイトをクロールして電話・メール等を抽出
- ZeroBounce でメール検証
- 営業メール送信
- 運用ログ / 日次メトリクス記録

Phase2 では、この流れを壊さずに、次の課題を解決します。

- データの正本が複数に分散している
- スクリプト単位で責務が密結合している
- YouTube 起点情報と公式サイト起点情報の統合ルールが曖昧
- 将来の営業チャネル拡張（メール + 問い合わせフォーム）を載せにくい

## Phase2 の基本方針

### Phase2-Core
まずは「きれいな土台」を作ります。

- Master Leads を新設し、唯一の業務台帳にする
- 2 系統の収集パイプラインを統合する
- クロール対象と抽出ルールを明文化する
- 検証・営業可否判定を整理する
- CLI / config / logging / repository 層を整備する
- migration 方針を整備する

### 後段で実装するもの
以下は **Phase2-Core の後** に載せます。

- 営業メール送信
- 問い合わせフォーム送信
- 実行結果追跡
- 再送ルール
- A/B テストや送信チャネル最適化

## Source of Truth

Phase2 では、**Google Spreadsheet の `Master Leads` タブを source of truth とする**設計を採用します。

- 現在状態の正本: `Master Leads`
- 履歴・証拠・監査: 補助ログ / DB / 補助タブ
- 旧 CRM シートと旧 Phase5 シート: **移行元**
- 新コードが更新する主要対象: **Master Leads**

対象スプレッドシート:
- System of Record: https://docs.google.com/spreadsheets/d/1yxjsn-AZFlYPEq17mprYrDXmpd9CHsif-j2lUdHm78g/edit?usp=sharing

参考リポジトリ:
- Phase1: https://github.com/nario0715masa0619-create/video-sales-automation-phase1

## 収集パイプライン

Phase2 では、収集は 2 系統のまま維持します。

### 1. YouTube Discovery Pipeline
役割:
- YouTube チャンネル起点で候補企業を発見する
- チャンネル情報、概要欄、候補 URL を収集する

### 2. Official Site Enrichment Pipeline
役割:
- 公式 URL から企業情報と連絡先を精査する
- 会社名、電話番号、メールアドレス、問い合わせフォーム URL などを抽出する

## Master Leads の位置づけ

`Master Leads` は、**1 行 = 1 営業対象の現在状態**を表します。

ここに持つもの:
- 統合済み企業名
- YouTube 起点情報の要約
- 公式サイト起点情報
- 連絡先情報
- 検証結果
- 営業可否
- 次アクション
- 直近の接触サマリ

ここに持たないもの:
- クロールの全生ログ
- フォーム送信の詳細実行ログ
- メール送信の全履歴
- ZeroBounce の raw レスポンス

## ディレクトリ構成案

```text
src/
  vsa/
    config/
    domain/
    application/
    infrastructure/
    interfaces/
    shared/
docs/
  architecture/
  migration/
  implementation/
  operations/
tests/
scripts/
```

## 実装スコープ

### In Scope: Phase2-Core
- Master Leads のデータモデル整備
- YouTube discovery 入力の受け皿
- official site enrichment の再設計
- クロール対象ポリシー
- 電話 / メール / フォーム URL 抽出の整理
- source-of-truth ルール
- migration script
- CLI の骨格
- テスト方針の整備

### Out of Scope: 初期実装ではやらない
- 実メール送信
- 問い合わせフォーム自動送信
- CAPTCHA 回避
- 自動返信解析
- 商談自動管理
- フルダッシュボード

## 実装優先順位

1. ドキュメント確定
2. データモデル確定
3. repo 雛形作成
4. settings / logging / CLI ベース
5. Google Sheets repository
6. migration script
7. official site enrichment 再実装
8. YouTube discovery 取り込み整理

## 参照ドキュメント

- `docs/architecture/overview.md`
- `docs/architecture/data-model.md`
- `docs/architecture/scraping-target-policy.md`
- `docs/migration/migration-plan.md`
- `docs/implementation/roadmap.md`
- `docs/operations/runbook.md`
