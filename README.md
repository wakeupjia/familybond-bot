# Lark Bot (Python)

基于飞书官方 SDK `lark-oapi` 的轻量 Bot，支持接收消息自动回复和主动发送消息。

## 环境准备

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 配置

编辑 `.env` 文件，填入飞书开放平台的应用凭证：

```
APP_ID=cli_xxxxx
APP_SECRET=xxxxx
```

## 使用

### 1. 启动 Bot（接收并自动回复消息）

```bash
python bot.py
```

启动后 Bot 通过 WebSocket 长连接监听消息。收到文本消息会自动回复"收到：xxx"。支持私聊和群聊。

### 2. 主动发送消息

```bash
# 使用默认 open_id
python send_message.py 你好

# 指定 open_id
python send_message.py ou_xxxxx 你好
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `bot.py` | Bot 主程序，WebSocket 长连接，自动接收回复 |
| `send_message.py` | 主动发送消息脚本 |
| `.env` | 应用凭证配置 |
| `requirements.txt` | Python 依赖 |
