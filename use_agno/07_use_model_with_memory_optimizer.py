"""
初步使用 模型, 使用记忆, 记忆优化

记忆存储学习到的用户信息（“Sarah 更喜欢电子邮件”）
会话历史存储对话消息以保持连续性
"""
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai.like import OpenAILike
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager, SummarizeStrategy      # 记忆管理器和摘要策略
from agno.memory.strategies.types import MemoryOptimizationStrategyType  # 记忆优化策略类型枚举
from agno.session.summary import SessionSummaryManager


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


# 定义 SQLite 数据库文件路径
db_file = "./custom/memory_summarize_strategy.db"
# 创建 SQLite 数据库连接实例
db = SqliteDb(db_file=db_file)

# 指定当前用户标识（用于区分不同用户的记忆）
user_id = "user2"

# 创建一个启用记忆功能的 Agent
agent = Agent(
    model=client_model,   # 使用的模型（注意：实际应为有效模型名，如 "gpt-4"）
    db=db,                                 # 关联数据库，用于持久化记忆
    update_memory_on_run=True,             # 每次运行 agent 时自动从对话中提取并更新记忆
)

# ---------- 第一阶段：向 agent 提供多段对话，让 agent 自动提取并存储记忆 ----------
print("Creating memories...")
# 第一条对话：描述宠物狗 Max 的信息
agent.print_response(
    "I have a wonderful pet dog named Max who is 3 years old. He's a golden retriever and he's such a friendly and energetic dog. "
    "We got him as a puppy when he was just 8 weeks old. He loves playing fetch in the park and going on long walks. "
    "Max is really smart too - he knows about 15 different commands and tricks. Taking care of him has been one of the most "
    "rewarding experiences of my life. He's basically part of the family now.",
    user_id=user_id,    # 关联到指定用户
)

# 第二条对话：描述居住地和工作情况（旧金山，产品经理）
agent.print_response(
    "I currently live in San Francisco, which is an amazing city despite all its challenges. I've been here for about 5 years now. "
    "I work in the tech industry as a product manager at a mid-sized software company. The tech scene here is incredible - "
    "there are so many smart people working on interesting problems. The cost of living is definitely high, but the opportunities "
    "and the community make it worthwhile. I live in the Mission district which has great food and a vibrant culture.",
    user_id=user_id,
)

# 第三条对话：描述周末爱好（徒步、探索新餐厅）
agent.print_response(
    "On weekends, I really enjoy hiking in the beautiful areas around the Bay Area. There are so many amazing trails - "
    "from Mount Tamalpais to Big Basin Redwoods. I usually go hiking with a group of friends and we try to explore new trails every month. "
    "I also love trying new restaurants. San Francisco has such an incredible food scene with cuisines from all over the world. "
    "I'm always on the lookout for hidden gems and new places to try. My favorite types of cuisine are Japanese, Thai, and Mexican.",
    user_id=user_id,
)

# 第四条对话：描述学习钢琴的经历
agent.print_response(
    "I've been learning to play the piano for about a year and a half now. It's something I always wanted to do but never had time for. "
    "I finally decided to commit to it and I practice almost every day, usually for 30-45 minutes. "
    "I'm working through classical pieces right now - I can play some simple Bach and Mozart compositions. "
    "My goal is to eventually be able to play some jazz piano as well. Having a creative hobby like this has been great for my mental health "
    "and it's nice to have something completely different from my day job.",
    user_id=user_id,
)

# ---------- 第二阶段：查看优化前的记忆情况 ----------
print("\nBefore optimization:")
# 从数据库获取当前用户的所有记忆条目
memories_before = agent.get_user_memories(user_id=user_id)
print(f"  Memory count: {len(memories_before)}")

# 创建 SummarizeStrategy 实例，用于统计记忆的 token 数量（为后续对比优化效果）
strategy = SummarizeStrategy()
tokens_before = strategy.count_tokens(memories_before)   # 计算优化前的总 token 数
print(f"  Token count: {tokens_before} tokens")

# 打印每条原始记忆内容
print("\nIndividual memories:")
for i, memory in enumerate(memories_before, 1):
    print(f"  {i}. {memory.memory}")

# ---------- 第三阶段：创建记忆管理器，并执行“摘要”优化策略 ----------
# MemoryManager 负责对用户记忆进行批量管理、优化（如合并、摘要、删除等）
memory_manager = MemoryManager(
    model=client_model,   # 用于生成摘要的模型
    db=db,                                 # 关联同一数据库，读取/写入记忆
)

print("\nOptimizing memories with 'summarize' strategy...")
# optimize_memories 方法：根据指定的策略优化指定用户的记忆
# MemoryOptimizationStrategyType.SUMMARIZE 表示将所有记忆合并成一条简洁的摘要
# apply=True 表示将优化结果直接写入数据库（永久生效）
memory_manager.optimize_memories(
    user_id=user_id,
    strategy=MemoryOptimizationStrategyType.SUMMARIZE,
    apply=True,
)

# ---------- 第四阶段：查看优化后的记忆，对比效果 ----------
print("\nAfter optimization:")
memories_after = agent.get_user_memories(user_id=user_id)
print(f"  Memory count: {len(memories_after)}")

# 计算优化后的 token 总数
tokens_after = strategy.count_tokens(memories_after)
print(f"  Token count: {tokens_after} tokens")

# 计算 token 减少量和百分比，展示优化效果
if tokens_before > 0:
    reduction_pct = ((tokens_before - tokens_after) / tokens_before) * 100
    tokens_saved = tokens_before - tokens_after
    print(f"  Reduction: {reduction_pct:.1f}% ({tokens_saved} tokens saved)")

# 打印摘要后的记忆内容（通常只有一条，包含之前所有关键信息的总结）
if memories_after:
    print("\nSummarized memory:")
    print(f"  {memories_after[0].memory}")
else:
    print("\n No memories found after optimization")