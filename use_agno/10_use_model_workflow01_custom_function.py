"""
使用工作流
在工作流中使用自定义函数
"""
from agno.workflow import Workflow, Step, StepInput, StepOutput
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


# 自定义函数
"""
所有自定义函数都遵循以下一致的结构
# 1. Custom preprocessing
# 2. Call agents/teams as needed
# 3. Custom postprocessing
"""
def custom_content_planning_function(step_input: StepInput) -> StepOutput:
    """
    Custom function that does intelligent content planning with context awareness
    """
    message = step_input.input
    previous_step_content = step_input.previous_step_content

    # Create intelligent planning prompt
    planning_prompt = f"""
        学习计划规划

        主题: {message}

       相关信息: {previous_step_content[:500] if previous_step_content else "No research results"}

        计划要求:
        1. 创建一份周计划
        2. 详细对整体内容进行分阶段
        3. 详细制定每天的任务和学习时长

        请制定一份详细且可执行的内容计划。
    """

    try:
        response = content_planner.run(planning_prompt)

        enhanced_content = f"""
            ## 开始制定计划

            **计划主题:** {message}

            **内容整合:** {f"✓ Research-based:  {previous_step_content}" if previous_step_content else "✗ No research foundation"}

            **内容:**
            {response.content}

        """.strip()

        return StepOutput(content=enhanced_content)

    except Exception as e:
        return StepOutput(
            content=f"Custom content planning failed: {str(e)}",
            success=False,
        )

# 创建工作流中的步骤
content_planning_step = Step(
    name="Content Planning Step",
    executor=custom_content_planning_function,
)


# 创建代理
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

content_planner = Agent(
    model=client_model,
    name="Content Planner",
    role="根据给定的主题，制定内容计划",
)


# 创建工作流
client_workflow = Workflow(
    name="test workflow",
    steps=[news_agent, finance_agent, content_planning_step],
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


# client_workflow.print_response(input="写一篇关于langchain的200字描述,并给出评分和对应评估过程")