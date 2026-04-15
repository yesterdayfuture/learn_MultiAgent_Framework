"""
初步使用 模型, 使用记忆

记忆存储学习到的用户信息（“Sarah 更喜欢电子邮件”）
会话历史存储对话消息以保持连续性
"""
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai.like import OpenAILike
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# 支持 openai格式 的模型，使用 OpenAILike 来进行调用
# 初始化模型
client_model = OpenAILike(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    id=os.getenv("model_name"),
    cache_response=True,        # 缓存结果
    cache_ttl=60 * 60 * 24,     # 缓存过期时间
    cache_dir="./custom/cache"  # 缓存存放目录
)


# 初始化记忆管理器
memory_manager = MemoryManager(
    model=client_model,
    db=SqliteDb("./custom/db.sqlite", session_table="session_table", memory_table="memory_table"),
)

# 初始化代理
client_agent = Agent(
    session_id="test",
    user_id="user_123",
    name="Researcher",              # 代理名称
    role="Research information",    # 代理角色
    model=client_model,             # 模型
    # 如果模型调用失败，则使用 fallback_models
    fallback_models=[OpenAILike(
        base_url=os.getenv("base_url"),
        api_key=os.getenv("api_key"),
        id=os.getenv("model_name_2"),
    ),],
    db=SqliteDb("./custom/db.sqlite", session_table="session_table", memory_table="memory_table"),      # 数据库地址，建立连接; session_table表来存储会话信息; memory_table表来存储记忆
    memory_manager=memory_manager,  # 启用记忆管理
    update_memory_on_run=True,      # update_memory_on_run=True，智能助手会在每次对话后自动创建和更新记忆。它会提取相关信息并存储起来，并在需要时调用，无需人工干预。
    enable_agentic_memory=True,     # 代理通过内置工具完全控制内存管理。它会根据对话上下文决定何时创建、更新或删除内存。
    add_memories_to_context=True,   # 将记忆添加到对话上下文中
)


if __name__ == "__main__":
    # 非流式调用
    nostreaming_result = client_agent.run("你好，我是wjm", max_tokens=1000, user_id="user_123")
    print(f"assitant:  {nostreaming_result.content}")
    nostreaming_result = client_agent.run("你知道我叫什么吗", max_tokens=1000, user_id="user_123")
    print(f"assitant:  {nostreaming_result.content}")

    # 检索当前用户的记忆
    user_id = "user_123"
    memories = client_agent.get_user_memories(user_id=user_id)
    if memories:
        for memory in memories:
            print(f"会话ID： {memory.user_id}")
            print(f"当前会话最后一次运行的消息和回复： {memory.memory}")  # List of runs with messages and responses

    else:
        print(f"未找到会话 {user_id}")

