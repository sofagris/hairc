# IRC Home Assistant 集成

一个 Home Assistant 集成，允许您连接到 IRC 服务器和频道，与您的 Home Assistant 实例进行通信。

## 功能

- 连接到 IRC 服务器
- 加入 IRC 频道
- 支持 SSL 加密
- 支持服务器密码
- 记录传入消息
- 图形界面配置

## 安装

### HACS 安装（推荐）

1. 在您的 Home Assistant 实例中打开 HACS
2. 转到"集成"部分
3. 点击右上角的三个点
4. 选择"自定义存储库"
5. 添加此存储库：
   - 存储库：`yourusername/hairc`
   - 类别：集成
6. 点击"添加"
7. 在列表中找到"IRC Home Assistant Integration"
8. 点击"安装"
9. 重启 Home Assistant

### 手动安装

1. 将 `custom_components/hairc` 文件夹复制到您的 Home Assistant `custom_components` 文件夹
2. 重启 Home Assistant
3. 在 Home Assistant GUI 中转到集成
4. 点击"+ 添加集成"
5. 搜索"IRC Home Assistant Integration"
6. 填写以下字段：
   - 服务器（您要连接的 IRC 服务器）
   - 端口（默认 6667）
   - 昵称（机器人的用户名）
   - 频道（您要加入的频道）
   - 密码（可选，如果服务器需要）
   - SSL（如果您想使用安全连接）

## 配置

### YAML 配置（可选）

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

## 故障排除

如果您遇到连接问题：

1. 验证服务器地址是否正确
2. 确认端口是否正确
3. 验证昵称是否可用
4. 检查频道是否存在
5. 在 Home Assistant 日志中查找错误消息

## 贡献

欢迎贡献！请按照以下步骤操作：

1. Fork 项目
2. 创建新分支
3. 进行更改
4. 提交拉取请求

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。 