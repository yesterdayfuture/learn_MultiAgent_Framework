"""
pip install llama-index-readers-file
pip install docx2txt

建立 基础rag
加载数据-》拆分成块-> 建立所有-》存入向量库 -〉检索-》评估


# 使用支持openai格式的模型时，需要修改源码/Users/zhangtian/miniforge3/envs/agent_env/lib/python3.10/site-packages/llama_index/embeddings/openai/base.py
中的
class OpenAIEmbeddingModelType(str, Enum):

    DAVINCI = "davinci"
    CURIE = "curie"
    BABBAGE = "babbage"
    ADA = "ada"
    TEXT_EMBED_ADA_002 = "text-embedding-ada-002"
    TEXT_EMBED_3_LARGE = "text-embedding-3-large"
    TEXT_EMBED_3_SMALL = "text-embedding-3-small"
    TEXT_EMBED_Qwen = "Qwen/Qwen3-Embedding-4B" # 新增


class OpenAIEmbeddingModeModel(str, Enum):

    # davinci
    TEXT_SIMILARITY_DAVINCI = "text-similarity-davinci-001"
    TEXT_SEARCH_DAVINCI_QUERY = "text-search-davinci-query-001"
    TEXT_SEARCH_DAVINCI_DOC = "text-search-davinci-doc-001"

    # curie
    TEXT_SIMILARITY_CURIE = "text-similarity-curie-001"
    TEXT_SEARCH_CURIE_QUERY = "text-search-curie-query-001"
    TEXT_SEARCH_CURIE_DOC = "text-search-curie-doc-001"

    # babbage
    TEXT_SIMILARITY_BABBAGE = "text-similarity-babbage-001"
    TEXT_SEARCH_BABBAGE_QUERY = "text-search-babbage-query-001"
    TEXT_SEARCH_BABBAGE_DOC = "text-search-babbage-doc-001"

    # ada
    TEXT_SIMILARITY_ADA = "text-similarity-ada-001"
    TEXT_SEARCH_ADA_QUERY = "text-search-ada-query-001"
    TEXT_SEARCH_ADA_DOC = "text-search-ada-doc-001"

    # text-embedding-ada-002
    TEXT_EMBED_ADA_002 = "text-embedding-ada-002"

    # text-embedding-3-large
    TEXT_EMBED_3_LARGE = "text-embedding-3-large"

    # text-embedding-3-small
    TEXT_EMBED_3_SMALL = "text-embedding-3-small"

    # 新增
    TEXT_EMBED_Qwen = "Qwen/Qwen3-Embedding-4B"

_QUERY_MODE_MODEL_DICT = {
    (OAEM.SIMILARITY_MODE, "davinci"): OAEMM.TEXT_SIMILARITY_DAVINCI,
    (OAEM.SIMILARITY_MODE, "curie"): OAEMM.TEXT_SIMILARITY_CURIE,
    (OAEM.SIMILARITY_MODE, "babbage"): OAEMM.TEXT_SIMILARITY_BABBAGE,
    (OAEM.SIMILARITY_MODE, "ada"): OAEMM.TEXT_SIMILARITY_ADA,
    (OAEM.SIMILARITY_MODE, "text-embedding-ada-002"): OAEMM.TEXT_EMBED_ADA_002,
    (OAEM.SIMILARITY_MODE, "text-embedding-3-small"): OAEMM.TEXT_EMBED_3_SMALL,
    (OAEM.SIMILARITY_MODE, "text-embedding-3-large"): OAEMM.TEXT_EMBED_3_LARGE,
    (OAEM.TEXT_SEARCH_MODE, "davinci"): OAEMM.TEXT_SEARCH_DAVINCI_QUERY,
    (OAEM.TEXT_SEARCH_MODE, "curie"): OAEMM.TEXT_SEARCH_CURIE_QUERY,
    (OAEM.TEXT_SEARCH_MODE, "babbage"): OAEMM.TEXT_SEARCH_BABBAGE_QUERY,
    (OAEM.TEXT_SEARCH_MODE, "ada"): OAEMM.TEXT_SEARCH_ADA_QUERY,
    (OAEM.TEXT_SEARCH_MODE, "text-embedding-ada-002"): OAEMM.TEXT_EMBED_ADA_002,
    (OAEM.TEXT_SEARCH_MODE, "text-embedding-3-large"): OAEMM.TEXT_EMBED_3_LARGE,
    (OAEM.TEXT_SEARCH_MODE, "text-embedding-3-small"): OAEMM.TEXT_EMBED_3_SMALL,

    # 新增
    (OAEM.SIMILARITY_MODE, "Qwen/Qwen3-Embedding-4B"):OAEMM.TEXT_EMBED_Qwen,
    (OAEM.TEXT_SEARCH_MODE, "Qwen/Qwen3-Embedding-4B"):OAEMM.TEXT_EMBED_Qwen
}

_TEXT_MODE_MODEL_DICT = {
    (OAEM.SIMILARITY_MODE, "davinci"): OAEMM.TEXT_SIMILARITY_DAVINCI,
    (OAEM.SIMILARITY_MODE, "curie"): OAEMM.TEXT_SIMILARITY_CURIE,
    (OAEM.SIMILARITY_MODE, "babbage"): OAEMM.TEXT_SIMILARITY_BABBAGE,
    (OAEM.SIMILARITY_MODE, "ada"): OAEMM.TEXT_SIMILARITY_ADA,
    (OAEM.SIMILARITY_MODE, "text-embedding-ada-002"): OAEMM.TEXT_EMBED_ADA_002,
    (OAEM.SIMILARITY_MODE, "text-embedding-3-small"): OAEMM.TEXT_EMBED_3_SMALL,
    (OAEM.SIMILARITY_MODE, "text-embedding-3-large"): OAEMM.TEXT_EMBED_3_LARGE,
    (OAEM.TEXT_SEARCH_MODE, "davinci"): OAEMM.TEXT_SEARCH_DAVINCI_DOC,
    (OAEM.TEXT_SEARCH_MODE, "curie"): OAEMM.TEXT_SEARCH_CURIE_DOC,
    (OAEM.TEXT_SEARCH_MODE, "babbage"): OAEMM.TEXT_SEARCH_BABBAGE_DOC,
    (OAEM.TEXT_SEARCH_MODE, "ada"): OAEMM.TEXT_SEARCH_ADA_DOC,
    (OAEM.TEXT_SEARCH_MODE, "text-embedding-ada-002"): OAEMM.TEXT_EMBED_ADA_002,
    (OAEM.TEXT_SEARCH_MODE, "text-embedding-3-large"): OAEMM.TEXT_EMBED_3_LARGE,
    (OAEM.TEXT_SEARCH_MODE, "text-embedding-3-small"): OAEMM.TEXT_EMBED_3_SMALL,

    # 新增
    (OAEM.SIMILARITY_MODE, "Qwen/Qwen3-Embedding-4B"):OAEMM.TEXT_EMBED_Qwen,
    (OAEM.TEXT_SEARCH_MODE, "Qwen/Qwen3-Embedding-4B"):OAEMM.TEXT_EMBED_Qwen
}
"""

from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import TokenTextSplitter

# 加载数据
documents = SimpleDirectoryReader(input_files=["LangGraph多智能体协作系统方案文档（Word适配版）.docx"]).load_data()
print(documents)


# ============根据 document 建立块==============
# 拆分块
pipeline = IngestionPipeline(transformations=[TokenTextSplitter()])

nodes = pipeline.run(documents=documents)
print(nodes[0])
print(f"共拆分成 {len(nodes)} 个块")

# =============直接建立 node ====================
from llama_index.core.schema import TextNode, ImageNode

node1 = TextNode(text="玉米是一种粮食作物", id_="<node_id>")
# node2 = TextNode(text="白菜是一种蔬菜", id_="<node_id>")
node3 = ImageNode(image_path="123", image_url="http://1.1.1.1:80", id_="图片", text="图中有一只兔子正在悠闲的吃菜")
cur_nodes = [node1, node3]
print(f"自定义建立的node {cur_nodes[0]}")

# =============使用嵌入模型，进行向量化，构建索引================
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

embedding_model = OpenAIEmbedding(
    api_base=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("embedding_model"),
)

from llama_index.core import VectorStoreIndex
# # 在 documents 上建立索引
# vec_index = VectorStoreIndex.from_documents(documents=documents, embedding_model=embedding_model, show_progress= True)

# 在 nodes 上建立索引
vec_index = VectorStoreIndex(nodes=cur_nodes, embed_model=embedding_model, show_progress= True)

# 基础检索
# 配置 llm 模型
from llama_index.llms.openai import OpenAI
model_client = OpenAI(
    api_base=os.getenv("base_url"),
    api_key=os.getenv("api_key"),
    model=os.getenv("model_name_2"),
)

query_engine = vec_index.as_query_engine(llm=model_client)
response = query_engine.query(
    "介绍一下粮食玉米"
)
print(response)
for node_info in response.source_nodes:
    print(f"检索的相关内容: {node_info.node.text}\n 相关分数：{node_info.score}\n\n")





