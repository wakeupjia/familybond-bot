import os
import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()


def on_message_receive(data: P2ImMessageReceiveV1) -> None:
    """收到消息后自动回复"""
    msg = data.event.message
    if msg.message_type == "text":
        text = json.loads(msg.content)["text"]
    else:
        text = "（暂不支持非文本消息）"

    reply_content = json.dumps({"text": f"收到：{text}"})

    if msg.chat_type == "p2p":
        # 私聊 -> 用 create 发送
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
        # 群聊 -> 用 reply 回复
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
