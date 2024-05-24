from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_transformers import LongContextReorder
import os
import re
from app.util import json_utils


# 텍스트 전처리
def normalize_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # 문장 부호 제거
    text = re.sub(r'\s+', ' ', text).strip()  # 공백 정리
    return text.replace('제안이유 및 주요내용', '').replace('제안이유', '') # 불필요한 단어 제외

# 검색한 문서 결과를 Rerank 이후 하나의 문단으로 병합
reordering = LongContextReorder()
def format_docs(docs):
    reordered_docs = reordering.transform_documents(docs)
    return "\n\n".join(doc.page_content for doc in reordered_docs)


# ############### Load ###############
loader = JSONLoader(
    file_path='json/bill_0518.json',
    jq_schema='.[]',
    content_key="content",
    metadata_func=json_utils.metadata_func,
    text_content=False)

docs = loader.load()
print(f"문서의 수: {len(docs)}")

for i in docs:
    normalized_text = normalize_text(i.page_content)
    

# ############### Split ###############
# 길이 짧게 + 많이 chunking
# 텍스트에 meta 데이터를 tag로 붙여서 임베딩하면 좋음
# chunk hierarchy

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

splits = text_splitter.split_documents(docs)
print('split_length =', len(splits)) 


# ############### Embed and Store ###############
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
# embeddings = HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-base')

from app.service import pinecone_service
index_name = 'bill-search'
namespace = 'bill'

ps = pinecone_service.PineconeService(
    host=os.environ.get('PINECONE_HOST'),
    index_name=index_name,
    namespace=namespace,
    embeddings=embeddings
)

if not ps.get_total_vector_count():
    print('add_documents')
    ps.add_documents(splits)

pinecone_retriever = ps.vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={'k': 10, 'score_threshold': 0.8},
)

bm25_retriever = BM25Retriever.from_documents(
    documents=splits,
    k=5,
)

hybrid_search = EnsembleRetriever(
    retrievers=[bm25_retriever, pinecone_retriever],
    weights=[0.3, 0.7],
)


############### Prompt and Chain ###############
from app.llms import gpt
from app.prompt import custom_bill_qna_prompt

hybrid_chain = (
    {"context": hybrid_search | format_docs, "question": RunnablePassthrough()}
    | custom_bill_qna_prompt
    | gpt
    | StrOutputParser()
)

