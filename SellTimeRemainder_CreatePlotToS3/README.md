# SellTimeRemainder_CreatePlotToS3
## 機能
DynamoDBのレコードに変更があったときにトリガーとして起動するLambda関数。変更があったレコードを読み出し、カード価格をグラフ化し、S3にpngでアップロードする。グラフはmplfinanceを使い、日毎グラフと週足グラフを作る。

## リソース
- DynamoeDB: SellTimeRemainder (us-west-2)
- S3: highso.com (ap-northeast-1)

## DynamoDBストリームの設定
- DynamoDBでテーブルを選択→エクスポートおよびストリーム→有効化
- 表示タイプ: 新しいイメージ
- ストリームの有効化

## IAM
### DynamoDB読み出しポリシー作成
ポリシーの作成→ビジュアルエディタ
- サービスの選択: DynamoDB
- アクション
  - GetShardIterator
  - GetRecords
  - ListStream
  - DescribeStream
- リソース: ARN arn:aws:dynamodb:us-west-2:<AWSアカウントID>:table/SellTimeRemainder/stream/*
- ポリシー名: SellTImeRemainder_DynamoDBStream
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetShardIterator",
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords",
                "dynamodb:ListStreams"
            ],
            "Resource": "arn:aws:dynamodb:us-west-2:<AWSアカウントID>:table/SellTimeRemainder/stream/*"
        }
    ]
}
```
### S3書き出しポリシー作成
ポリシーの作成→ビジュアルエディタ
- サービスの選択: DynamoDB
- アクション: PutObject
- リソース:
  - Bucket name: highso.com
  - Object name: すべて
- ポリシー名: SellTimeRemainder_PutToS3
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::highso.com/*"
        }
    ]
}
```
### Lambda用ロール作成
- ロールの作成
  - ユースケースの選択: Lambda
  - ポリシーのアタッチ:
    - SellTimeRemainder_DynamoDBStream
    - SellTimeRemainder_PutToS3
    - AWSLambdaBasicExecutionRole
  - ロール名: SellTimeRemainder_CreatePlotToS3

## Lambda関数
関数の作成
- 関数の新規作成
  - 関数名: SellTimeRemainder_CreatePlotToS3
  - ランタイム: Python3.8
  - 実行ロール: SellTimeRemainder_CreatePlotToS3
  - 再試行: 10回 （デフォルトの-1だと、lambdaがエラーになったときに無限に繰り返されてしまう可能性あり）
- 設定→一般設定→編集
  - タイムアウト: 10秒
- トリガー
  - トリガー: DynamoDB
  - DynamoDBテーブル: SellTimeRemainder
  - バッチサイズ；100（デフォルト）


## Lambdaコードのアップロード手順
AWS LambdaではPythonライブラリごとzipで固めてアップロードする必要があります。
### ライブラリをコードと同じディレクトリにインストール
```
$ cd SellTimeRemainder_CreatePlotToS3
$ pip3 install -U pip
$ pip3 install mplfinance -t ./
```
要らないものを削除
```
$ rm *.dist-info -r
$ rm *.so
$ rm *.pth
```
### ディレクトリごとzipで固める
```
$ sudo apt install zip
$ zip -r SellTimeRemainder_CreatePlotToS3.zip ./*
```

WindowsでWSLを使っている場合、zipをWSL環境からWindows環境にコピーする
```sh:wsl2
$ cp SellTimeRemainder_CreatePlotToS3.zip /mnt/c/Users/<Windowsユーザー名>/Desktop/
```

### Lambdaへのデプロイ
zipのデプロイ方法は3通りある
- (1)webコンソールからアップロード
- (2)AWS CLIでアップロード
- (3)S3に保存してwebコンソールからアップロード操作
(1)は10MBまで、(2)は7MB程度まで。mplfinanceライブラリは、numpyやpandasを含むため、ライブラリを全てzipにすると40MB程度になる。よって選択肢は(3)のみ。
- Amazon S3を経由してアップロードする手順
  - S3でzipアップロード専用のバケットを作る。
    - リージョン: us-west-2
    - バケット名: lambda-zip-maton
  - aws cliを使ってzipをアップロードする
```sh:wsl2
$ aws s3 cp SellTimeRemainder_CreatePlotToS3.zip s3://lambda-zip-maton/SellTimeRemainder_CreatePlotToS3.zip
```
  - webコンソールでS3を開いて、アップロードしたzipのオブジェクトURL(https://lambda-zip-maton.s3-us-west-2.amazonaws.com/SellTimeRemainder_CreatePlotToS3.zip )をコピー
  - webコンソールでLambdaを開いて、オブジェクトURLを設定する
