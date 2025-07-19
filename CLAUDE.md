# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

日本語文章校正システム - AIとルールベース技術を組み合わせた高精度な文章校正アプリケーション

## 開発コマンド

### 環境構築
```bash
# Docker環境起動
docker-compose up -d

# 依存関係インストール
make install

# 開発環境起動
make dev
```

### テスト・品質チェック
```bash
# 全テスト実行
make test

# バックエンドテスト
cd backend && pytest

# フロントエンドテスト  
cd frontend && npm test

# リンター実行
make lint

# コード整形
make format
```

### 個別起動
```bash
# バックエンド（FastAPI）
cd backend && uvicorn app.main:app --reload

# フロントエンド（Next.js）
cd frontend && npm run dev
```

## アーキテクチャ

### 技術スタック
- **フロントエンド**: React/Next.js + TypeScript + Chakra UI
- **バックエンド**: Python/FastAPI + SQLAlchemy
- **データベース**: PostgreSQL
- **キャッシュ**: Redis
- **AI/ML**: HuggingFace Transformers + 日本語BERT
- **インフラ**: Docker + Docker Compose

### ディレクトリ構造
```
proofreading_app/
├── backend/              # Python/FastAPI バックエンド
│   ├── app/
│   │   ├── api/         # API エンドポイント
│   │   ├── core/        # 設定・認証・ログ
│   │   ├── models/      # データベースモデル
│   │   ├── services/    # ビジネスロジック
│   │   └── utils/       # ユーティリティ
│   ├── tests/           # テスト
│   └── requirements.txt # Python依存関係
├── frontend/            # React/Next.js フロントエンド
│   ├── src/
│   │   ├── components/  # UIコンポーネント
│   │   ├── pages/       # ページ
│   │   ├── hooks/       # カスタムフック
│   │   ├── services/    # API通信
│   │   └── utils/       # ユーティリティ
│   └── package.json     # Node.js依存関係
├── scripts/             # データベース初期化等
└── docs/                # ドキュメント
```

### 主要機能
1. **ルールベースエンジン**: パターンマッチング校正
2. **AIエンジン**: BERT-based 文脈校正
3. **統合処理層**: 両エンジンの結果統合
4. **リアルタイムUI**: WebSocket対応校正インターフェース

## 開発ガイドライン

### ブランチ戦略
- `main`: 本番環境
- `develop`: 開発統合
- `feature/*`: 機能開発
- `hotfix/*`: 緊急修正

### コーディング規約
- **Python**: Black + isort + flake8 + mypy
- **TypeScript**: ESLint + Prettier
- **コミット**: Conventional Commits形式

### テスト方針
- **バックエンド**: pytest + coverage 90%以上
- **フロントエンド**: Jest + React Testing Library
- **E2E**: 主要フローのみ

## 環境変数

主要な環境変数（詳細は.env.exampleを参照）:
- `DATABASE_URL`: PostgreSQL接続文字列
- `REDIS_URL`: Redis接続文字列  
- `SECRET_KEY`: JWT署名キー
- `MODEL_PATH`: AIモデル格納パス

## トラブルシューティング

### よくある問題
1. **Docker起動失敗**: `make clean`でクリーンアップ後再起動
2. **依存関係エラー**: `make install`で再インストール
3. **ポート競合**: docker-compose.ymlのポート番号変更
4. **AIモデル読み込み失敗**: models/ディレクトリの権限確認

### パフォーマンス
- データベースクエリは適切にインデックス使用
- AIモデル推論結果はRedisキャッシュ活用
- フロントエンドは遅延読み込み・仮想化実装