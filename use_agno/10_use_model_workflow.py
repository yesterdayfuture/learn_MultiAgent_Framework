"""
使用团队，流式输出与非流式输出
"""
from agno.workflow import Workflow
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
    model=client_model,
    name="Writer",
    role="根据给定的主题编写一段文章"
)

finance_agent = Agent(
    model=client_model,
    name="Evluate",
    role="对文件进行评分，并给出评估过程"
)

# 创建工作流
client_workflow = Workflow(
    name="test workflow",
    steps=[news_agent, finance_agent],
)

# 非流式调用
response = client_workflow.run("写一篇关于langchain的200字描述,并给出评分和对应评估过程")
print(response.content)


# from agno.run.workflow import WorkflowRunEvent
# # 流式调用
# stream = client_workflow.run("写一篇关于langgraph的200字描述,并给出评分和对应评估过程", stream=True)
# for event in stream:
#         if event.event == WorkflowRunEvent.condition_execution_started.value:
#             print(event)
#             print()
#         elif event.event == WorkflowRunEvent.condition_execution_completed.value:
#             print(event)
#             print()
#         elif event.event == WorkflowRunEvent.workflow_started.value:
#             print(event)
#             print()
#         elif event.event == WorkflowRunEvent.step_started.value:
#             print(event)
#             print()
#         elif event.event == WorkflowRunEvent.step_completed.value:
#             print(event)
#             print()
#         elif event.event == WorkflowRunEvent.workflow_completed.value:
#             print(event)
#             print()