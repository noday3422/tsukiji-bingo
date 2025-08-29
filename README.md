# 築地ビンゴ MVP

友人3人で共有できるビンゴゲーム。マスをタップすると穴が開き、同じURLを見ている全員の画面に共有される。

## 構成
- **S3**: フロントエンド（index.html）をホスティング
- **API Gateway (HTTP API)** + **Lambda (Python)**: 盤面の読み書きAPI
- **DynamoDB**: 盤面の状態（labels, marks, updatedAt）を保持
- 共有はURLパラメータ `?id=gameId` で識別。認証なし、CORS有効。

## 必要ツール
- Python 3.12
- AWS CLI
- AWS SAM CLI
- AWSアカウント（リージョン: ap-northeast-1）
- conda (推奨)

## 環境構築
```bash
# conda環境作成
conda create -n tsukiji-bingo python=3.12 -y
conda activate tsukiji-bingo

# CLI類インストール
conda install -c conda-forge awscli aws-sam-cli -y

# バージョン確認
aws --version
sam --version

# AWS設定
aws configure set region ap-northeast-1
aws configure set output json
aws configure   # Access Key / Secret Key を入力

## デプロイ関連
### index.htmlのアップデート
aws s3 cp frontend/index.html s3://tsukiji-bingo-site/index.html --cache-control "no-store" --content-type text/html

### それ以外
sam build && sam deploy --no-confirm-changeset