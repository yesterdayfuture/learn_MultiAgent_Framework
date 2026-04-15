"""
使用工作流
在工作流运行过程中，人工参与
"""
from agno.workflow import Workflow, Step, StepInput, StepOutput, OnReject
from agno.workflow.types import HumanReview
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.knowledge.embedder.openai import OpenAIEmbedder
import os
from dotenv import load_dotenv
from agno.models.openai.like import OpenAILike
from agno.db.sqlite import SqliteDb


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
    human_review=HumanReview(
        requires_confirmation=True,     # 是否需要人工审核
        confirmation_message="请确认是否生成学习计划",   # 审核消息
        on_reject=OnReject.skip,       # 如果拒绝，是否跳过
    )
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

finance_agent_step = Step(
    name="Finance Agent Step",
    agent=finance_agent,
    human_review=HumanReview(
        requires_confirmation=True,     # 是否需要人工审核
        confirmation_message="请确认是否生成评估过程",   # 审核消息
        on_reject=OnReject.skip,       # 如果拒绝，是否跳过
    )
)


# 创建工作流
client_workflow = Workflow(
    name="test workflow",
    db=SqliteDb(db_file="./custom/workflow.db"),        # 使用人工参与时，必须配置数据库，保存和恢复工作流状态
    steps=[news_agent, finance_agent_step, content_planning_step],
)

# 非流式调用
run_response = client_workflow.run("写一篇关于langfuse的200字描述,并给出评分和对应评估过程")

while True:
    # 检查工作流是否因等待人工确认而暂停
    if run_response.is_paused:
        # 遍历所有需要确认的步骤
        for req in run_response.steps_requiring_confirmation:
            print(f"需要确认的步骤: {req.step_name}")
            print(f"确认消息: {req.confirmation_message}")
            user_decision = input("请确认 (y/n): ").strip().lower()
            if user_decision == 'y':
                req.confirm()  # 批准
            else:
                req.reject()   # 拒绝，行为由 on_reject 参数决定

        # 所有确认处理完毕后，使用 continue_run 恢复工作流
        # 注意：需要将 run_response 传递回去
        run_response = client_workflow.continue_run(run_response)
    else:
        # 如果工作流没有暂停，直接输出结果
        final_response = run_response
        break


print(final_response.content)