# 日本語文章校正システム

AIとルールベース技術を組み合わせた高精度な日本語文章校正システムです。

## 概要

本システムは、以下の機能を提供します：

- **誤字脱字検出**: 高精度な誤字・脱字の自動検出
- **文法チェック**: 助詞の誤用、語順間違い等の文法エラー検出
- **表記統一**: 送り仮名、数字表記等の統一支援
- **リアルタイム校正**: 入力しながらの即座な校正提案

## アーキテクチャ

- **フロントエンド**: React/Next.js + TypeScript
- **バックエンド**: Python/FastAPI
- **AI エンジン**: 日本語BERT + カスタム校正モデル
- **ルールエンジン**: 独自開発の文法・表記チェック
- **データベース**: PostgreSQL

## 開発環境セットアップ

### 前提条件

- Docker & Docker Compose
- Node.js 18+
- Python 3.9+

### 起動方法

```bash
# リポジトリクローン
git clone https://github.com/HappyMana/proofreading_app.git
cd proofreading_app

# Docker環境起動
docker-compose up -d

# フロントエンド起動 (開発時)
cd frontend
npm install
npm run dev

# バックエンド起動 (開発時)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## プロジェクト構造

```
proofreading_app/
├── backend/              # Python/FastAPI バックエンド
│   ├── app/
│   │   ├── api/         # API エンドポイント
│   │   ├── core/        # 設定・認証
│   │   ├── models/      # データモデル
│   │   ├── services/    # ビジネスロジック
│   │   └── utils/       # ユーティリティ
│   ├── tests/           # テストコード
│   └── scripts/         # スクリプト
├── frontend/            # React/Next.js フロントエンド
│   ├── src/
│   │   ├── components/  # UIコンポーネント
│   │   ├── pages/       # ページコンポーネント
│   │   ├── hooks/       # カスタムフック
│   │   ├── services/    # API通信
│   │   └── utils/       # ユーティリティ
│   └── tests/           # テストコード
├── docs/                # ドキュメント
└── scripts/             # 開発スクリプト
```

## 開発フロー

1. **Issue作成**: GitHubでタスクを管理
2. **ブランチ作成**: `feature/issue-number-description`
3. **開発**: ローカル環境で実装
4. **テスト**: 自動テスト実行
5. **PR作成**: レビュー依頼
6. **マージ**: メインブランチへ統合

## ライセンス

MIT License