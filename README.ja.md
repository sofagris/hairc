# Home Assistant IRC 統合

この統合により、Home AssistantはIRCサーバーに接続し、IRCとHome Assistant間の双方向通信を可能にします。

## 機能

- IRCサーバーへの接続（SSL対応）
- メッセージの送受信
- IRCメッセージに基づく自動化のトリガー
- Home AssistantからのIRCメッセージ送信
- 接続切断時の自動再接続

## インストール

### HACS経由（推奨）

1. Home AssistantインスタンスでHACSを開く
2. 「統合」セクションに移動
3. 右上の3点メニューをクリックし、「カスタムリポジトリ」を選択
4. このリポジトリを追加: `https://github.com/sofagris/hairc`
5. 「追加」をクリック
6. HACSストアで「IRC」を検索
7. 「Home Assistant IRC」統合の「インストール」をクリック
8. Home Assistantを再起動

### 手動インストール

1. `hairc`ディレクトリをHome Assistantの`custom_components`ディレクトリにコピー
2. Home Assistantを再起動

## 設定

`configuration.yaml`に以下を追加:

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: あなたのボット
  channel: "#あなたのチャンネル"
  ssl: true
  password: あなたのパスワード  # オプション
```

## 使用方法

### メッセージの送信

`hairc.send_message`サービスを使用してIRCにメッセージを送信できます:

```yaml
service: hairc.send_message
data:
  message: "Home Assistantからのメッセージです！"
  channel: "#あなたのチャンネル"  # オプション、指定しない場合はデフォルトチャンネルを使用
```

### メッセージの受信

IRCメッセージは`hairc_message`イベントをトリガーします。これらのイベントに基づいて自動化を作成できます:

```yaml
alias: "IRC pingへの応答"
trigger:
  platform: event
  event_type: hairc_message
  event_data:
    message: "ping"
    type: public
action:
  service: hairc.send_message
  data:
    message: "pong"
```

### ウェルカムメッセージ

ボットがチャンネルに接続したときにウェルカムメッセージを送信するには、以下の自動化を追加します:

```yaml
alias: "IRCウェルカムメッセージ"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistantがサービスを提供します。コマンド一覧は!helpと入力してください"
```

## トラブルシューティング

問題が発生した場合:

1. Home Assistantのログでエラーメッセージを確認
2. IRCサーバー設定を確認
3. ファイアウォールがIRCサーバーへの送信接続を許可していることを確認
4. ボットがチャンネルに参加する権限を持っていることを確認

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細はLICENSEファイルを参照してください。 