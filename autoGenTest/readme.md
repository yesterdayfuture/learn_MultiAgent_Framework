# AutoGen 学习项目

本项目用于学习和实践 Microsoft AutoGen 框架的各种功能。

**官方文档地址：** https://www.aidoczh.com/autogen/stable/user-guide/agentchat-user-guide/tutorial/messages.html

## 环境安装

```bash
pip install -U "autogen-agentchat"
pip install "autogen-ext[openai]"
pip install mcp
```

## 文件说明

| 文件名 | 功能描述 |
|--------|----------|
| 01_use_model.py | 基础模型调用示例，展示如何使用 OpenAIChatCompletionClient 与模型进行交互对话 |
| 02_use_multimodal_message.py | 多模态消息处理示例，演示如何发送包含图片和文本的多模态消息 |
| 03_use_AssistantAgent.py | AssistantAgent 使用示例，包含工具调用和流式/非流式输出 |
| 04_auto_function_conversion_tool.py | 自动函数转换工具示例，展示如何将 Python 函数自动转换为工具（使用 inspect 模块提取函数信息） |
| 05Assistant.py | 单一智能体完整示例，包含模型定义、工具定义和智能体配置 |
| 05_use_mcp.py | MCP (Model Context Protocol) 集成示例，展示如何连接远程 MCP 服务并使用其工具 |
| 06_use_context.py | 上下文管理示例，使用 BufferedChatCompletionContext 缓存模型输出，让智能体使用上下文 |
| 07_use_MutliModel_to_agent.py | 多模态模型代理示例，处理图片信息，使用支持视觉的模型分析图片内容 |
| 08_use_team.py | 团队代理示例，展示多智能体协作，使用 RoundRobinGroupChat 实现轮询团队 |
| 09_user_join_team.py | 用户参与团队协作示例，引入 UserProxyAgent 让人工参与多智能体对话 |
| 10_use_selector_team.py | 选择器团队示例，使用 SelectorGroupChat 由中控智能体进行调度决策 |
| 11_use_selector_team2.py | 高级选择器团队示例，使用自定义选择函数，添加用户反馈机制控制调度逻辑 |
| 12_use_swarm_team.py | 蜂群团队示例，使用 Swarm 模式，由中控智能体进行调度，支持任务交接 |
| 13_use_magenticOne_team.py | MagenticOne 团队示例，使用 MagenticOneGroupChat 进行多智能体协作编排 |
| 14_use_memory.py | 记忆系统示例，展示如何使用 ListMemory 为智能体添加记忆功能 |

## 核心概念

### 1. 模型客户端 (Model Client)
- 使用 `OpenAIChatCompletionClient` 连接 OpenAI 格式的 API
- 支持配置模型能力信息（vision、function_calling、json_output 等）

### 2. 智能体 (Agent)
- **AssistantAgent**: 基础助手智能体，支持工具调用和系统消息
- **UserProxyAgent**: 用户代理智能体，用于人工参与对话

### 3. 团队 (Team)
- **RoundRobinGroupChat**: 轮询团队，按顺序让每个智能体发言
- **SelectorGroupChat**: 选择器团队，由中控智能体决定下一个发言者
- **Swarm**: 蜂群团队，支持智能体之间的任务交接
- **MagenticOneGroupChat**: MagenticOne 团队编排模式

### 4. 上下文管理
- **BufferedChatCompletionContext**: 缓存聊天历史，控制上下文窗口大小

### 5. 记忆系统
- **ListMemory**: 列表形式的记忆存储
- **MemoryContent**: 记忆内容封装

### 6. 工具集成
- **FunctionTool**: 将 Python 函数转换为工具
- **MCP 工具**: 通过 Model Context Protocol 连接远程工具服务

## 运行示例

```bash
python 01_use_model.py
```

每个文件都是独立的示例，可以直接运行。
