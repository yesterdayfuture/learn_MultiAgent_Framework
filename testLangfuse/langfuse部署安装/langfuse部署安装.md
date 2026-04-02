## Langfuse 安装

> Langfuse 是一个**开源的 LLM 工程平台**（[GitHub](https://github.com/langfuse/langfuse)），它可以帮助团队协作调试、分析和迭代他们的 LLM 应用程序。所有平台功能都已原生集成，以加速开发工作流程。Langfuse 是开源的、可自托管的且可扩展的

### 从github 上拉去源码

```shell
git clone https://github.com/langfuse/langfuse.git
cd langfuse

```

### 使用docker compose 启动

```
docker compose up
```

`http://localhost:3000`在浏览器中打开即可访问 Langfuse 用户界面





## Langfuse使用



### 与 openai 集成

#### 初步使用，使用默认配置

```python
"""
测试使用 langfuse 跟踪监测 openai 调用
"""
from langfuse.openai import OpenAI
import os


os.environ["LANGFUSE_SECRET_KEY"] = "xxx"
os.environ["LANGFUSE_PUBLIC_KEY"] = "xxx"
os.environ["LANGFUSE_BASE_URL"] = "xxx"


client = OpenAI(
    base_url='xxx',
    api_key='xxxxx'
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city for which to get the weather."
                    }
                },
                "required": ["city"]
            }
        }
    }
]


def non_stream(user_message: str = "你叫什么名字?"):
    result = client.chat.completions.create(
        model="qwen3.5-27b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{user_message}"}
        ]
    )
    return result.choices[-1].message.content


def chat_stream(user_message):
    messages = [{"role": "user", "content": user_message}]

    stream = client.chat.completions.create(
        model="qwen3.5-27b",
        messages=messages,
        stream=True
    )

    # 收集流式响应
    full_response = ""

    for chunk in stream:
        delta = chunk.choices[0].delta

        # 处理内容
        if delta.content:
            full_response += delta.content
            print(delta.content, end="", flush=True)

# 测试
chat_stream("你可以做什么？")

# print(non_stream())
```

#### 使用session

```python
"""
测试使用 langfuse 跟踪监测 openai 调用,添加session
"""
from langfuse import get_client, propagate_attributes
from langfuse.openai import OpenAI
import os


os.environ["LANGFUSE_SECRET_KEY"] = "xxx"
os.environ["LANGFUSE_PUBLIC_KEY"] = "xxxx"
os.environ["LANGFUSE_BASE_URL"] = "xxx"


langfuse_client = get_client()


client = OpenAI(
    base_url='xxxx',
    api_key='xxxx'
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city for which to get the weather."
                    }
                },
                "required": ["city"]
            }
        }
    }
]


def non_stream(user_message: str = "你叫什么名字?"):
    result = client.chat.completions.create(
        model="qwen3.5-27b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{user_message}"}
        ]
    )
    return result.choices[-1].message.content


def chat_stream(user_message):
    messages = [{"role": "user", "content": user_message}]

    stream = client.chat.completions.create(
        model="qwen3.5-27b",
        messages=messages,
        stream=True
    )

    # 收集流式响应
    full_response = ""

    for chunk in stream:
        delta = chunk.choices[0].delta

        # 处理内容
        if delta.content:
            full_response += delta.content
            print(delta.content, end="", flush=True)


with langfuse_client.start_as_current_observation(as_type="span", name="qwen3.5-27b"):
    with propagate_attributes(session_id="session-id"):
        # 测试
        chat_stream("你是谁？")

        # print(non_stream())
```





