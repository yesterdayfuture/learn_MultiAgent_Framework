from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.vectordb.search import SearchType
from agno.models.openai.like import OpenAILike
from agno.knowledge.embedder.openai import OpenAIEmbedder
import os
from dotenv import load_dotenv

# 引入 CohereReranker 重排序模型
from agno.knowledge.reranker.cohere import CohereReranker


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

# 初始化嵌入模型
embed_model = OpenAIEmbedder(
    base_url=os.getenv("embedding_base_url"),
    api_key=os.getenv("embedding_api_key"),
    id=os.getenv("embedding_model"),
)

# Create a knowledge base
knowledge = Knowledge(
    vector_db=ChromaDb(
        collection="docs",
        path="tmp/chromadb",
        persistent_client=True,
        embedder=embed_model,
        search_type=SearchType.hybrid,
        reranker=CohereReranker()
    ),
)

# Load content
# knowledge.insert(url="https://docs.agno.com/introduction.md", skip_if_exists=True)
knowledge.insert(text_content="我喜欢跑步、美食和旅游", skip_if_exists=True)

# Create an agent that searches the knowledge base
agent = Agent(
    model=client_model,
    knowledge=knowledge,
    search_knowledge=True
)
# agent.print_response("我的爱好是什么")

result = agent.run("我的爱好是什么")
print(result.content)