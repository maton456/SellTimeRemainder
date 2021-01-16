# SellTimeRemainder_GetItems
## AWS Lambda設定
- IAMロール：DynamoDBへのアクセス権
- タイムアウト：3分（ライブラリのロードに5秒ほどかかる模様）
- トリガー：EventBridge
  - 2021年、毎日JST12時(=UT3時)に起動
  - cron(0 3 * * ? 2021)

## コードのアップロード手順
AWS LambdaではPythonライブラリごとzipで固めてアップロードする必要があります。
### ライブラリをコードと同じディレクトリにインストール
```
cd SellTimeRemainder_GetItems
pip3 install requests -t ./
pip3 install beautifulsoup4 -t ./
```
要らないものを削除
```
rm *.dist-info -r
```
### ディレクトリごとzipで固める
```
sudo apt install zip
zip -r SellTimeRemainder_GetItems.zip ./*
```

WindowsでWSLを使っている場合、zipをWSL環境からWindows環境にコピーする
```
cp SellTimeRemainder_GetItems.zip /mnt/c/Users/<Windowsユーザー名>/Desktop/
```
SellTimeRemainder_GetItems.zipをLambdaにアップロードします。