import json
import os

import requests
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
AGENT_BASE_URL = os.getenv("AGENT_BASE_URL", "http://localhost:9000")
FALLBACK_REPLY = "我刚刚有点忙，没来得及处理这条消息，稍后再试试好吗？"

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()


def call_agent(user_id: str, message: str) -> str:
    payload = {
        "user_id": user_id,
        "user_role": "elder",
        "message": message,
        "source": "feishu",
        "session_id": f"feishu_{user_id}",
    }
    try:
        session = requests.Session()
        session.trust_env = False
        resp = session.post(
            f"{AGENT_BASE_URL}/invoke",
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        reply = data.get("reply_text", "")
        if not reply:
            return FALLBACK_REPLY
        return reply
    except Exception as e:
        print(f"Agent 调用失败: {e}")
        return FALLBACK_REPLY


def send_text_message(msg, text: str):
    reply_content = json.dumps({"text": text})

    if msg.chat_type == "p2p":
        req = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(msg.chat_id)
                .msg_type("text")
                .content(reply_content)
                .build()
            )
            .build()
        )
        resp = client.im.v1.message.create(req)
    else:
        req = (
            ReplyMessageRequest.builder()
            .message_id(msg.message_id)
            .request_body(
                ReplyMessageRequestBody.builder()
                .msg_type("text")
                .content(reply_content)
                .build()
            )
            .build()
        )
        resp = client.im.v1.message.reply(req)

    if not resp.success():
        print(f"消息回复失败: code={resp.code}, msg={resp.msg}")


def on_message_receive(data: P2ImMessageReceiveV1) -> None:
    msg = data.event.message
    if msg.message_type == "text":
        text = json.loads(msg.content)["text"]
    else:
        text = "（暂不支持非文本消息）"

    sender_id = data.event.sender.sender_id.open_id or data.event.sender.sender_id.user_id
    reply = call_agent(sender_id, text)
    send_text_message(msg, reply)


# WebSocket 长连接 + 事件分发
event_handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_im_message_receive_v1(on_message_receive)
    .build()
)

ws_client = lark.ws.Client(
    APP_ID,
    APP_SECRET,
    event_handler=event_handler,
    log_level=lark.LogLevel.DEBUG,
)

if __name__ == "__main__":
    print("Lark Bot 已启动，等待消息...")
    ws_client.start()
