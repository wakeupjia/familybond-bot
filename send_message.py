"""主动向用户发送消息（通过 open_id）"""
import os
import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
DEFAULT_OPEN_ID = os.getenv("OPEN_ID", "ou_f65ce37374c05423469f1197d5ebff7c")

client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()


def send_text(open_id: str, text: str) -> bool:
    req = (
        CreateMessageRequest.builder()
        .receive_id_type("open_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(open_id)
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()
        )
        .build()
    )
    resp = client.im.v1.message.create(req)
    if resp.success():
        print(f"发送成功: {text}")
        return True
    else:
        print(f"发送失败: code={resp.code}, msg={resp.msg}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        open_id, text = sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 2:
        open_id, text = DEFAULT_OPEN_ID, sys.argv[1]
    else:
        print("用法: python send_message.py [open_id] <消息内容>")
        sys.exit(1)

    send_text(open_id, text)
