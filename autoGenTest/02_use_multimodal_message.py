"""
使用多模态消息
"""

from autogen_agentchat.messages import MultiModalMessage

from io import BytesIO

import requests
from autogen_core import Image as AGImage
from PIL import Image
import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

with open("/Users/zhangtian/Downloads/gw/test2.png", "rb") as f:
    pil_image = Image.open(BytesIO(f.read()))

img = AGImage(pil_image)
multi_modal_message = MultiModalMessage(content=["你是一位军事信息专家和图片阅读大师，请详细描述一下这张图片,输出图片中都包含哪些物体、物体的位置、数量、当前状态等信息?", img], source="User")

print(multi_modal_message)