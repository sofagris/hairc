# IRC Home Assistant 統合

Home Assistant インスタンスと通信するために IRC サーバーとチャンネルに接続できる Home Assistant 統合です。

## 機能

- IRC サーバーへの接続
- IRC チャンネルへの参加
- SSL 暗号化のサポート
- サーバーパスワードのサポート
- 受信メッセージのログ記録
- GUI 設定

## インストール

### HACS インストール（推奨）

1. Home Assistant インスタンスで HACS を開く
2. 「統合」セクションに移動
3. 右上の三点をクリック
4. 「カスタムリポジトリ」を選択
5. このリポジトリを追加：
   - リポジトリ：`yourusername/hairc`
   - カテゴリ：統合
6. 「追加」をクリック
7. リストから「IRC Home Assistant Integration」を探す
8. 「インストール」をクリック
9. Home Assistant を再起動

### 手動インストール

1. `custom_components/hairc` フォルダを Home Assistant の `custom_components` フォルダにコピー
2. Home Assistant を再起動
3. Home Assistant GUI で統合に移動
4. 「+ 統合を追加」をクリック
5. 「IRC Home Assistant Integration」を検索
6. 以下のフィールドを入力：
   - サーバー（接続する IRC サーバー）
   - ポート（デフォルト 6667）
   - ニックネーム（ボットのユーザー名）
   - チャンネル（参加するチャンネル）
   - パスワード（オプション、サーバーで必要な場合）
   - SSL（セキュア接続を使用する場合）

## 設定

### YAML 設定（オプション）

```yaml
# configuration.yaml
hairc:
  server: irc.example.com
  port: 6667
  nickname: homeassistant
  channel: "#homeassistant"
  password: !secret irc_password
  ssl: false
```

## トラブルシューティング

接続に問題がある場合：

1. サーバーアドレスが正しいことを確認
2. ポートが正しいことを確認
3. ニックネームが利用可能であることを確認
4. チャンネルが存在することを確認
5. Home Assistant ログでエラーメッセージを確認

## 貢献

貢献は大歓迎です！以下の手順に従ってください：

1. プロジェクトをフォーク
2. 新しいブランチを作成
3. 変更を加える
4. プルリクエストを送信

## ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルを参照してください。 