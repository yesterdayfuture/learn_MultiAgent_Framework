import uuid
from typing import TypedDict, Annotated, Literal
import operator

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# ==================================================
# 1. 定义图的状态 (State)
# ==================================================
# 状态是工作流中的共享内存，所有节点都可以读取和更新它。
# 它就像一个“存档”，让工作流在中断后能恢复现场。
class AgentState(TypedDict):
    # 代码变更的摘要
    code_summary: str
    # 人工审核状态: "pending", "approved", "rejected", "edited"
    approval_status: str
    # 人工修改后的最终代码变更（如果人工进行了编辑）
    edited_changes: str
    # 部署结果
    deployment_result: str
    # 使用Annotated和operator.add可以允许节点追加消息，形成消息列表
    messages: Annotated[list, operator.add]


# ==================================================
# 2. 定义图中的节点 (Nodes)
# ==================================================
# 节点是工作流中的一个个处理单元。

def draft_changes_node(state: AgentState):
    """
    节点1: 模拟LLM或开发人员起草代码变更。
    此节点不涉及人机交互，只是生成待审核的内容。
    """
    print("🤖 [节点: 起草变更] 正在分析需求并起草代码变更...")
    # 模拟生成一个代码变更摘要
    draft_summary = """
    变更内容:
    1. 修复了用户登录时的会话超时问题。
    2. 为API添加了新的速率限制机制，防止滥用。
    3. 优化了数据库查询索引，预期查询性能提升20%。
    """
    print(f"🤖 拟定的变更: {draft_summary}")
    # 返回更新后的状态字段
    return {"code_summary": draft_summary, "approval_status": "pending"}


def human_approval_node(state: AgentState):
    """
    节点2: 动态人工审核节点。
    这是HITL的核心。调用interrupt()函数会立即暂停图执行，
    将控制权交还给调用方，并等待人工输入。
    """
    print("\n" + "="*50)
    print("👨‍💼 [节点: 人工审核] 等待您的审批或修改...")
    print(f"待审核的代码变更: \n{state['code_summary']}")
    print("="*50)

    # 定义发送给人工审核界面的信息（一个可序列化的JSON对象）
    # 在实际应用中，这可以是前端展示的一个表单或弹窗。
    interrupt_payload = {
        "question": "请审核上述代码变更，您可以选择 'approve' (批准)、'reject' (拒绝) 或 'edit' (修改)。",
        "current_changes": state['code_summary']
    }

    # --- 关键点：中断并等待人工输入 ---
    # interrupt()函数会抛出GraphInterrupt异常，保存当前状态，然后暂停。
    # 当工作流恢复时，传入的Command(resume=...)中的值会作为返回值赋给`human_input`变量。
    # 注意：恢复执行时会从本节点的开头重新运行。
    # 因此，为了不重复展示上面的打印信息，并正确处理恢复后的逻辑，
    # 通常需要检查状态来判断是首次进入还是恢复进入。
    # 一种常见的幂等设计是：在首次中断前不修改任何外部状态，只做信息展示。
    # 这里为了演示，我们简单地将恢复信息直接作为审批结果。
    # 在实际生产中，你可以在state中增加一个标志位，例如`if state.get('has_approved'):`来避免重复。
    # 为了简洁并展示核心机制，我们假设这里每次进入都会中断并等待输入。
    human_input = interrupt(interrupt_payload)

    print(f"👨‍💼 收到您的输入: {human_input}")

    # 根据人工输入处理后续逻辑
    if human_input == "approve":
        print("✅ 审核通过！准备部署...")
        return {"approval_status": "approved", "edited_changes": state['code_summary']}
    elif human_input == "reject":
        print("❌ 审核被拒绝！工作流终止。")
        return {"approval_status": "rejected"}
    elif human_input.startswith("edit:"):
        # 人工可以编辑变更内容，输入格式为 'edit: <修改后的内容>'
        edited = human_input.replace("edit:", "", 1).strip()
        print(f"✏️ 收到人工修改的变更: {edited}")
        return {"approval_status": "edited", "edited_changes": edited}
    else:
        # 处理无效输入
        print("⚠️ 无效输入，请使用 'approve', 'reject', 或 'edit: <内容>'。")
        # 可以在这里选择重试或拒绝，为了演示，我们简单地拒绝
        return {"approval_status": "rejected"}


def deploy_node(state: AgentState):
    """
    节点3: 模拟部署操作。
    只有在审核状态为 'approved' 或 'edited' 时才会执行此节点。
    """
    print("\n🚀 [节点: 部署] 开始部署代码变更...")
    if state['approval_status'] == 'approved':
        changes_to_deploy = state['code_summary']
    else:  # 'edited'
        changes_to_deploy = state['edited_changes']

    print(f"🚀 正在部署变更: {changes_to_deploy}")
    # 模拟部署过程
    result = "部署成功！变更已应用到生产环境。"
    print(f"✅ {result}")
    return {"deployment_result": result, "messages": ["系统: 部署已完成。"]}


def route_after_approval(state: AgentState) -> Literal["deploy_node", END]:
    """
    条件路由函数，决定审核后的流程走向。
    """
    if state['approval_status'] in ["approved", "edited"]:
        return "deploy_node"
    else:
        return END


# ==================================================
# 3. 构建并编译图 (Graph)
# ==================================================
def build_graph():
    # 初始化图构建器，传入我们定义的状态类型
    builder = StateGraph(AgentState)

    # 添加节点
    builder.add_node("draft_changes_node", draft_changes_node)
    builder.add_node("human_approval_node", human_approval_node)
    builder.add_node("deploy_node", deploy_node)

    # 添加边，定义执行顺序
    builder.add_edge(START, "draft_changes_node")
    builder.add_edge("draft_changes_node", "human_approval_node")
    # 从审核节点出发，根据条件路由到部署节点或直接结束
    builder.add_conditional_edges("human_approval_node", route_after_approval)
    builder.add_edge("deploy_node", END)

    # --- 关键点：启用持久化（Checkpointer）---
    # 为了让工作流能够中断和恢复，必须配置一个检查点器（Checkpointer）。
    # MemorySaver 将状态保存在内存中，适合开发和演示。
    # 在生产环境中，可以使用 PostgresSaver、RedisSaver 等将状态持久化到数据库。
    memory = MemorySaver()

    # --- 关键点：设置静态断点 ---
    # 在编译图时，可以指定 interrupt_before 或 interrupt_after 来设置静态断点。
    # 这里我们在 'deploy_node' 执行前再设一个静态断点，作为二次确认。
    # 这样，即使人工审核通过，部署前仍可强制暂停，让人有机会做最后检查。
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["deploy_node"]  # 在部署节点之前暂停
    )
    return graph


# ==================================================
# 4. 运行与交互
# ==================================================
def run_example():
    print("🚀 LangGraph 人工参与 (HITL) 示例启动")
    print("本示例模拟了一个代码审查与部署流程。\n")

    # 步骤 0: 准备工作
    # 生成一个唯一的线程ID，用于标识这个对话或工作流实例。
    thread_id = str(uuid.uuid4())
    # 配置对象，LangGraph 使用 thread_id 来恢复特定状态。
    config = {"configurable": {"thread_id": thread_id}}

    # 构建图
    graph = build_graph()

    # 步骤 1: 首次执行，直到第一次中断（动态中断）
    print("\n--- 第一轮执行: 启动工作流，直到遇到动态中断 (human_approval_node) ---")
    # 注意：stream 方法会返回一个生成器，我们只关心最终状态。
    # 对于中断的情况，我们可以直接使用 invoke 或 stream，它会抛出 GraphInterrupt 异常。
    # 更优雅的做法是捕获异常，但为了演示清晰，我们直接执行。
    # 实际上，执行到 interrupt() 时，invoke 会返回一个包含 __interrupt__ 字段的字典。
    for event in graph.stream({}, config=config):
        # 这里event是一个字典，键是节点名，值是该节点的输出。
        # 在中断发生前，我们会看到 'draft_changes_node' 的输出。
        print(f"事件: {event}")
        # 如果中断发生，后续就不会再有事件了，循环结束。
        # 注意: 更可靠的检测方式是捕获 GraphInterrupt 异常，但这里为了演示流程，我们直接依赖后续的交互。
        pass

    # 检查是否因为中断而停止
    # 我们可以通过查看图的状态来确认
    state_snapshot = graph.get_state(config)
    if state_snapshot.next:
        print(f"⏸️ 工作流在节点 '{state_snapshot.next[0]}' 处被中断，等待人工输入。")

    # 步骤 2: 模拟人工输入并恢复执行
    print("\n--- 第二轮执行: 人工提供输入并恢复 ---")
    # 模拟人工的决策。在实际应用中，这可能来自前端表单、API调用等。
    # 这里我们让用户在控制台选择。
    while True:
        print("\n请做出选择:")
        print("1. 批准 (approve)")
        print("2. 拒绝 (reject)")
        print("3. 修改 (edit: <修改内容>)")
        choice = input("请输入你的选择 (1/2/3): ").strip()

        if choice == "1":
            human_decision = "approve"
            break
        elif choice == "2":
            human_decision = "reject"
            break
        elif choice == "3":
            edited_content = input("请输入修改后的代码变更内容: ")
            human_decision = f"edit: {edited_content}"
            break
        else:
            print("无效输入，请重新输入。")

    # --- 关键点：恢复执行 ---
    # 使用 Command(resume=...) 将人工输入作为恢复值传回，并再次调用 invoke。
    # 这会从之前中断的地方（human_approval_node）继续执行，并且 interrupt() 的返回值就是 human_decision。
    print("\n--- 恢复工作流 ---")
    for event in graph.stream(Command(resume=human_decision), config=config):
        print(f"事件: {event}")

    # 步骤 3: 处理静态断点（如果前面的流程没有被拒绝的话）
    # 在 deploy_node 之前，我们设置了静态断点，所以工作流会再次暂停。
    state_snapshot = graph.get_state(config)
    if state_snapshot.next and state_snapshot.next[0] == "deploy_node":
        print("\n⏸️ 工作流在部署前暂停（静态断点），等待最终确认。")
        print("工作流将在此等待人工最终确认。")
        # 模拟最终确认（例如通过一个API调用）
        final_confirm = input("是否确认部署？(y/n): ")
        if final_confirm.lower() == 'y':
            # 恢复执行，无需额外数据，只需一个空Command来继续。
            # 注意：这里 resume 的值可以是任意值，但我们不需要，所以传入 None。
            for event in graph.stream(Command(resume=final_confirm), config=config):
                print(f"事件: {event}")
            print("✅ 部署流程结束。")
        else:
            print("❌ 最终确认取消，部署终止。")
    elif state_snapshot.next:
        # 如果流程被拒绝，next 可能是空的，或者指向 END。
        print("\n✅ 工作流已结束。")

    # 可选：查看最终状态
    final_state = graph.get_state(config).values
    print("\n--- 最终工作流状态 ---")
    for key, value in final_state.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    run_example()