from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers import EnsembleRetriever, ParentDocumentRetriever, ContextualCompressionRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_transformers import LongContextReorder
from langchain.storage import InMemoryStore
import os, re
from app.util import json_utils
from langchain.retrievers.multi_query import MultiQueryRetriever
from app.llms import gpt
from app.prompt import custom_bill_qna_prompt_v1, multiquery_prompt
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_community.vectorstores import Chroma


# 텍스트 전처리
def normalize_text(text: str, metadata: dict):
    text = re.sub(r'[^\w\s]', '', text)  # 문장 부호 제거
    text = re.sub(r'\s+', ' ', text).strip()  # 공백 정리
    proposer = metadata['proposer']
    date = metadata['propose_date']
    text += f'\n[tag] 법안을 발의한 사람:, {proposer}, 제안일, {date}'
    return text.replace('제안이유 및 주요내용', '').replace('제안이유', '') # 불필요한 단어 제외

reordering = LongContextReorder()
def reordering_format_docs(docs):
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
    normalized_text = normalize_text(i.page_content, i.metadata)
    i.page_content = normalized_text
    

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
# print(splits[1000:1011])


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
# ps.delete_all_vector()

if not ps.get_total_vector_count():
    print('add_documents')
    ps.add_documents(splits)

pinecone_retriever = ps.vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={'k': 10, 'score_threshold': 0.75},
)

bm25_retriever = BM25Retriever.from_documents(
    documents=splits,
    k=10,
)

multiquery_retriever = MultiQueryRetriever.from_llm(
    retriever=pinecone_retriever,
    llm=gpt,
    prompt=multiquery_prompt
)

parent_document_retriever = ParentDocumentRetriever(
    vectorstore=ps.vectorstore,
    docstore=InMemoryStore(),
    child_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50),
    search_kwargs={"k": 10}
)
# parent_document_retriever.add_documents(
#     documents=docs,
#     ids=None
# )

document_content_description = "법안의 제안 이유 및 주요 내용입니다."
metadata_field_info = [
    AttributeInfo(
        name="proposer",
        description="법안을 발의한 의원입니다.",
        type="string",
    ),
    AttributeInfo(
        name="propose_date",
        description="법안이 발의된 날짜입니다.",
        type="integer",
    )
]
self_query_retriever = SelfQueryRetriever.from_llm(
    llm=gpt,
    vectorstore=Chroma.from_documents(documents=splits, embedding=embeddings),
    document_contents=document_content_description,
    metadata_field_info=metadata_field_info,
    search_kwargs={"k": 10}
)


hybrid_retriever = EnsembleRetriever(
    retrievers=[
        bm25_retriever, 
        pinecone_retriever, 
        multiquery_retriever, 
        parent_document_retriever, 
        self_query_retriever
        ],
    weights=[
        0.2, 
        0.2, 
        0.2, 
        0.2,
        0.2
        ],
)

model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
compressor = CrossEncoderReranker(model=model, top_n=10)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=hybrid_retriever
)
############### Prompt and Chain ###############
hybrid_chain = (
    {"context": compression_retriever | reordering_format_docs, "question": RunnablePassthrough()}
    | custom_bill_qna_prompt_v1
    | gpt
    | StrOutputParser()
)

