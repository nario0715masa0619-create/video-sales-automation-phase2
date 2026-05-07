# Implementation Roadmap

## 1. 目的

Phase2-Core を実装するための順序、優先順位、最初の 1 週間で作るべきものを整理する。

---

## 2. スコープ境界

### Phase2-Core に含む
- repo 雛形
- config / logger / CLI 基盤
- Master Leads モデル
- Google Sheets gateway
- migration
- official site enrichment 再設計
- discovery 情報の取り込み口
- contactability 判定
- 補助ログの保存枠

### 後段に回す
- メール送信
- 問い合わせフォーム送信
- 送信自動再試行
- CAPTCHA 対応
- 自動商談管理

---

## 3. マイルストーン

### Milestone 1: Foundation
- `pyproject.toml`
- `src/`
- `tests/`
- 設定読み込み
- logging
- CLI エントリポイント
- enum / constants

### Milestone 2: Data Model & Sheets
- ヘッダ定義
- 列定数
- row ↔ model 変換
- Google Sheets repository

### Milestone 3: Migration
- extractor
- normalizer
- matcher
- merger
- loader
- 検証レポート

### Milestone 4: Official Site Enrichment
- target planner
- crawler
- phone extractor
- email extractor
- form URL detector
- evidence 保存

### Milestone 5: Recompute & Reporting
- validation status 取り込み
- contactability 判定
- next_action 計算
- summary レポート

---

## 4. 最初の 1 週間の実装計画

### Day 1
- repo 初期構成を作る
- README / docs を配置する
- `pyproject.toml` を作る
- lint / format / test 方針を決める

### Day 2
- `MasterLead` の型定義を作る
- enum 定義を作る
- 列名定数を作る
- row parser / serializer を作る

### Day 3
- Google Sheets client を作る
- `MasterLeadsRepository` を作る
- 読み込み / 更新の最小動作を作る

### Day 4
- migration の normalize 関数を作る
- URL 正規化
- enum mapping
- `"None"` 排除

### Day 5
- match / merge ロジックを作る
- 検証レポート出力
- dry-run migration 実行
