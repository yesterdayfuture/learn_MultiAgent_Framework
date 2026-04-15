"""
使用团队，流式输出与非流式输出
"""
from agno.team import Team, TeamMode
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.knowledge.embedder.openai import OpenAIEmbedder
import os
from dotenv import load_dotenv
from agno.models.openai.like import OpenAILike


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


# 支持 openai格式 的模型，使用 OpenAILike 来进行调用
# 初始化语言模型
client_model = OpenAILike(
    base_url=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    id=os.getenv("model_name"),
    cache_response=True,        # 缓存结果
    cache_ttl=60 * 60 * 24,     # 缓存过期时间
    cache_dir="./custom/cache"  # 缓存存放目录
)

news_agent = Agent(
    name="Writer",
    role="根据给定的主题编写一段文章"
)

finance_agent = Agent(
    name="Evluate",
    role="对文件进行评分，并给出评估过程"
)

# 创建团队
# 如果成员没有指定模型，则使用团队的模型
"""
模式	配置	用例
协调	mode=TeamMode.coordinate（默认）	分解工作，委派给成员，综合结果
路线	mode=TeamMode.route	直接联系一位专家并回复其意见。
播送	mode=TeamMode.broadcast	将同一任务分配给所有成员并进行综合分析。
任务	mode=TeamMode.tasks	运行任务列表循环，直到目标完成。
"""
team = Team(
    name="Research Team",
    members=[news_agent, finance_agent],
    model=client_model,
    instructions="对问题进行解析，然后基于各个角色，进行分配任务",
    mode=TeamMode.coordinate,   # 协调模式
    # debug_mode= True,           # debug 调试
)

# # 非流式调用
# response = team.run("写一篇关于langchain的200字描述,并给出评分和对应评估过程")
# print(response.content)

# 流式调用
stream = team.run("写一篇关于langchain的200字描述,并给出评分和对应评估过程", stream=True)
for chunk in stream:
    print(chunk.content, end="", flush=True)