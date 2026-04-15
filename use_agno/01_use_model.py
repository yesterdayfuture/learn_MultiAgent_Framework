"""
初步使用 模型
"""
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai.like import OpenAILike

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 支持 openai格式 的模型，使用 OpenAILike 来进行调用
# 初始化模型
client_model = OpenAILike(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    id=os.getenv("model_name_2"),
    cache_response=True,        # 缓存结果
    cache_ttl=60 * 60 * 24,     # 缓存过期时间
    cache_dir="./custom/cache"  # 缓存存放目录
)


# 初始化代理
client_agent = Agent(
    name="Researcher",              # 代理名称
    role="Research information",    # 代理角色
    model=client_model,             # 模型
    # 如果模型调用失败，则使用 fallback_models
    fallback_models=[OpenAILike(
        base_url=os.getenv("base_url"),
        api_key=os.getenv("api_key"),
        id=os.getenv("model_name_2"),
    ),]
)


if __name__ == "__main__":
    # # 非流式调用
    # nostreaming_result = client_agent.run("请写一个关于机器学习的文章", max_tokens=1000)
    # print(nostreaming_result.content)
    # nostreaming_result = client_agent.run("请写一个关于机器学习的文章", max_tokens=1000)
    # print(nostreaming_result.content)

    # 流式调用
    for streaming_result in client_agent.run("请写一个关于机器学习的文章", max_tokens=1000, stream=True):
        print(streaming_result.content, end="", flush=True)
