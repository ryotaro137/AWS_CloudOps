# ハンズオン：シナリオ7（CloudFront のキャッシュ制御と罠）

このハンズオンでは、「キャッシュが効きすぎて古いデータが返る」「スマホなのにPC向け画面が出る」といった、CloudFront運用時によく発生するトラブルをあえて発生させ、それを解決する一連の流れを体験します。

---

## 🚀 ステップ1：オリジンサーバー（EC2）の構築

動的なAPIレスポンスと静的ファイルを返す、簡単なWebサーバーを構築します。

1. **EC2インスタンスの作成**:
   - OS: Amazon Linux 2023
   - M/T: t2.micro（無料枠）
   - セキュリティグループ: `HTTP (80)` を `0.0.0.0/0` から許可
2. **Webサーバー（Nginx または Python）の起動**:
   EC2にSSH接続（またはSession Manager）し、以下のコマンドでテスト用のディレクトリとファイルを作成し、簡易サーバーを立ち上げます。

```bash
# テスト用ディレクトリ作成
mkdir -p ~/cf-test/api
mkdir -p ~/cf-test/css
cd ~/cf-test

# 1. 動的APIのエミュレート（アクセスされた時刻を返す）
echo "<?php echo json_encode(['time' => date('Y-m-d H:i:s')]); ?>" > api/data.php

# 2. 静的CSSファイル
echo "body { background-color: blue; }" > css/style.css

# 3. ユーザーエージェント(スマホ/PC)を判定して表示を変えるHTML（簡易版）
cat << 'EOF' > index.php
<?php
$ua = $_SERVER['HTTP_USER_AGENT'];
$device = preg_match('/iPhone|Android.*Mobile/i', $ua) ? "Mobile" : "PC";
?>
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <h1>This is <?php echo $device; ?> version!</h1>
</body>
</html>
EOF

# PHPビルトインサーバーをポート80で起動（sudoが必要）
sudo dnf install -y php
sudo php -S 0.0.0.0:80 -t ~/cf-test > /dev/null 2>&1 &
```

> **確認**: ブラウザで `http://<EC2のパブリックIP>/` にアクセスし、「This is PC version!」と表示されることを確認します。

---

## 🚀 ステップ2：CloudFront ディストリビューションの作成（罠の設定）

わざと最適化されていない「デフォルト」の設定でCloudFrontを作成します。

1. **CloudFront コンソール**を開き、「ディストリビューションを作成」をクリック。
2. **オリジンドメイン**: 作成したEC2インスタンスのパブリックIPv4 DNSを選択（プロトコルはHTTPのみ）。
3. **デフォルトのキャッシュビヘイビア**:
   - **ビューワープロトコルポリシー**: HTTP and HTTPS
   - **許可されたHTTPメソッド**: GET, HEAD
   - **キャッシュキーとオリジンリクエスト**:
     - `Cache policy and origin request policy` を選択
     - キャッシュポリシー: `CachingOptimized`（デフォルト）
4. これで作成を開始します。展開（Deploy）完了まで数分待ちます。

---

## 😱 ステップ3：問題（罠）の発生を確認する

CloudFrontのドメイン名（例: `d12345.cloudfront.net`）にアクセスしてトラブルを再現します。

### 罠1：PCとスマホの画面が同じになってしまう（表示崩れ）
1. パソコンのブラウザで `http://dXXXXX.cloudfront.net/` にアクセスし、「This is **PC** version!」と出るのを確認。
2. 次に、スマホの実機（またはChromeのデベロッパーツールでスマホモード）にして同じURLにアクセス。
3. **結果**: スマホなのに「This is **PC** version!」と表示されます。（※一番最初にPCでアクセスした結果がCloudFrontにキャッシュされ、全員にそれが返っているため）

### 罠2：APIのデータが更新されない（古いデータ問題）
1. ブラウザで `http://dXXXXX.cloudfront.net/api/data.php` にアクセス。
2. 表示された時刻（例: `{"time":"2026-03-08 12:00:00"}`）をメモ。
3. 数分待ってからページをリロード（F5）する。
4. **結果**: 時間が全く進みません。（APIのような動的データまでCloudFrontがキャッシュしてしまっているため）

### 罠3：デザイン（CSS）を直したのに反映されない（Invalidationのコスト）
1. EC2のターミナルに戻り、CSSの背景色を赤に変更します。
   `echo "body { background-color: red; }" > ~/cf-test/css/style.css`
2. ブラウザでトップページをリロード。
3. **結果**: 背景は**青**のままです。（CloudFrontに古いCSSがキャッシュされているため）
4. **悪い解決策**: CloudFrontの「キャッシュ削除（Invalidation）」タブから `/*` を実行すれば赤になりますが、実務でこれを頻繁にやると**多額の課金**が発生します。

---

## 🛠️ ステップ4：解決のためのトラブルシューティング（実務の正解）

### 解決1: デバイス(User-Agent)ごとのキャッシュ分割
CloudFrontに「PCとスマホで別々のキャッシュを持たせる」設定をします。

1. **CloudFront** -> 対象のディストリビューション -> **ビヘイビア**タブでデフォルトルート(`Default (*)`)を編集。
2. 「キャッシュキーとオリジンリクエスト」で**キャッシュポリシー**を新しく作成（CustomPolicy）。
3. 「ヘッダー」の項目で `CloudFront-Is-Mobile-Viewer` と `CloudFront-Is-Desktop-Viewer` を追加。
4. ※実務ではオリジンリクエストポリシーも作成し、同じヘッダーをオリジンに転送するようにします。
5. **確認**: 設定反映後、PCとスマホでアクセスすると別々のバージョンが表示されるようになります。

### 解決2: APIへの「Cache-Control: no-store」
動的なAPIはそもそもCloudFrontにキャッシュさせないのが正解です。
（EC2のターミナルでAPIのコードを修正し、HTTPヘッダーを出力するようにします）

```php
# api/data.php を修正
<?php 
header("Cache-Control: no-store, no-cache, must-revalidate");
echo json_encode(['time' => date('Y-m-d H:i:s')]); 
?>
```
> これにより、CloudFrontは（`CachingOptimized`ポリシーであっても）オリジンの指示に従い、キャッシュを行わなくなります。リロードするたびに時間が進むようになります。

### 解決3: URLバージョニングによるCSSの即時反映
キャッシュ削除（Invalidation）を使わずに、新しいCSSを読み込ませるテクニックです。
（HTMLの読み込みタグに `?v=2` のようなクエリパラメータを付与します）

```php
# index.php の一部を修正 (.../css/style.css ではなく、うしろに ?v=2 をつける)
<link rel="stylesheet" href="/css/style.css?v=2">
```
> **注意**: これをCloudFrontで機能させるには、ビヘイビアのキャッシュポリシー設定で「クエリストリング（Query strings）」を「すべて（All）」または特定のパラメータをキャッシュキーに含めるように設定変更が必要です。
> これにより、CloudFrontは「パラメータが違う未知の新しいファイルだ」と認識し、オリジンへ最新のCSSを取りに行きます。

---

## 🧹 ステップ5：お片付け
検証が終わったら、無駄な課金を防ぐためにリソースを即座に削除します。

1. **CloudFrontディストリビューションの「無効化（Disable）」** -> 数分待ち、ステータスが変わったら「削除（Delete）」
2. **EC2インスタンスの終了（Terminate）**

## メモ
- `mkdir -p` : 親ディレクトリが存在しない場合も含めて、必要なディレクトリ階層を一度に作成するオプション。（例: `mkdir -p ~/cf-test/api`）
- **UseCacheOriginHeaders** の方がEC2（動的サーバー）に勧められている理由は？
  - **結論**: CloudFront側で一律にキャッシュする（CachingOptimizedなど）よりも、**「EC2上のアプリケーション（PHP, Node.js, Nginx等）自身が、そのコンテンツをキャッシュすべきか（Cache-Controlヘッダー）を一番よく知っているから」**です。
  - **詳細**:
    - S3がオリジンの場合は「全て静的ファイル」なので、CloudFrontの `CachingOptimized`（CloudFront側で一律に長くキャッシュする）が適しています。
    - しかし、EC2がオリジンの場合は「静的ファイル」と「動的なAPI・HTML」が混在することが多いです。
    - `UseOriginCacheControlHeaders` 系のポリシー（または `Managed-CachingOptimized` の内部仕様）を使うと、**「EC2が `Cache-Control` ヘッダーを返してきた場合はそれを尊重し、返してこなかった場合（ただの画像など）はCloudFrontのデフォルト設定でキャッシュする」**という柔軟で安全な挙動になります。これにより「APIの古いデータがキャッシュされ続ける」という重大な事故を防ぐことができます。
- **`sudo ss -atulpn | grep :80` の意味**
  - **概要**: 「現在、ポート80番で通信を待ち受けている（Listenしている）プログラムは誰か？」を調べるトラブルシューティングコマンドです。「Webサーバーが起動しない（Address already in use）」時の原因調査によく使われます。
  - **コマンドの分解**:
    - `sudo` : プロセスのネットワーク詳細を見るための管理者権限。
    - `ss` : Socket Statistics（ネットワーク接続状況の確認）。
    - `-atulpn` : `a`(すべて) `t`(TCP) `u`(UDP) `l`(Listen状態) `p`(プロセス名とPIDを表示) `n`(名前解決せずポート番号を数字で表示) のオプションを合わせたもの。
    - `| grep :80` : 出力結果から「:80」が含まれる行（ポート80番に関する行）だけを抽出。
  - **出力例と活用**: `tcp LISTEN 0 1024 0.0.0.0:80 0.0.0.0:* users:(("php",pid=12345,fd=6))` 
    - → 「ポート80番を現在 `php` (PID: 12345) が使っている」と特定できるため、不要なプロセスなら `sudo kill 12345` で強制終了させてポートを解放する、などの対応が可能になります。

- クラウドフロントのビヘイビアの設定でhttpオンリーにしてなかったから接続できなかった。
