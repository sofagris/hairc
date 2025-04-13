# Home Assistant IRC 集成

此集成允许 Home Assistant 连接到 IRC 服务器，实现 IRC 和 Home Assistant 之间的双向通信。

## 功能

- 连接到 IRC 服务器（支持 SSL）
- 发送和接收消息
- 基于 IRC 消息触发自动化
- 从 Home Assistant 发送消息到 IRC
- 连接断开时自动重连

## 安装

### 通过 HACS（推荐）

1. 在 Home Assistant 实例中打开 HACS
2. 转到"集成"部分
3. 点击右上角的三点菜单，选择"自定义存储库"
4. 添加此存储库：`https://github.com/sofagris/hairc`
5. 点击"添加"
6. 在 HACS 商店中搜索"IRC"
7. 点击"Home Assistant IRC"集成的"安装"
8. 重启 Home Assistant

### 手动安装

1. 将 `hairc` 目录复制到 Home Assistant 的 `custom_components` 目录
2. 重启 Home Assistant

## 配置

在 `configuration.yaml` 中添加以下内容：

```yaml
hairc:
  server: irc.example.com
  port: 6697
  nickname: 你的机器人
  channel: "#你的频道"
  ssl: true
  password: 你的密码  # 可选
```

## 使用

### 发送消息

可以使用 `hairc.send_message` 服务向 IRC 发送消息：

```yaml
service: hairc.send_message
data:
  message: "来自 Home Assistant 的消息！"
  channel: "#你的频道"  # 可选，未指定时使用默认频道
```

### 接收消息

IRC 消息会触发 `hairc_message` 事件。可以基于这些事件创建自动化：

```yaml
alias: "响应 IRC ping"
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

### 欢迎消息

要让机器人在加入频道时发送欢迎消息，添加以下自动化：

```yaml
alias: "IRC 欢迎消息"
trigger:
  platform: event
  event_type: hairc_connected
action:
  service: hairc.send_message
  data:
    message: "Home Assistant 为您服务。输入 !help 查看命令列表"
```

## 故障排除

如果遇到问题：

1. 检查 Home Assistant 日志中的错误消息
2. 验证 IRC 服务器设置
3. 确保防火墙允许到 IRC 服务器的出站连接
4. 检查机器人是否有加入频道的权限

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。 