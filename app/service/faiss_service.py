from langchain_community.vectorstores import FAISS
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# if not os.path.exists('test.faiss'):
#     vectorstore = FAISS.from_documents(splits, embedding=embeddings)
#     vectorstore.save_local(folder_path='.', index_name='test')
#     print(11111)
# else:
#     vectorstore = FAISS.load_local(
#         folder_path='.', 
#         embeddings=embeddings, 
#         allow_dangerous_deserialization=True, 
#         index_name='test')
#     print(22222)
    # vectorstore.add_documents(splits)

# faiss_retriever 
# faiss_retriever = vectorstore.as_retriever(
    # search_type='similarity_score_threshold', 
    # search_kwargs={'k': 5, 'score_threshold': 0.65},
# )

# bm25_retriever 
# bm25_retriever = BM25Retriever.from_documents(
#     documents=splits,
#     k=3,
# )

# ensemble_retriever 
# hybrid_search = EnsembleRetriever(
#     retrievers=[bm25_retriever, faiss_retriever],
#     weights=[0.2, 0.8],
# )


# def format_docs(docs):
#     reordering = LongContextReorder()
#     reordered_docs = reordering.transform_documents(docs)
    # print('docs =', "\n\n".join(doc.page_content for doc in docs))
    # print('----------------------')
    # print('reordered_docs =', "\n\n".join(doc.page_content for doc in reordered_docs))
    # return "\n\n".join(doc.page_content for doc in reordered_docs)

# result = hybrid_search.invoke('아동학대에 관한 법안을 제출한 사람이 누구야?')
# print('-------vector db result-------')
# format_docs(result)
# [print(x) for x in result]
# print(result[0])
# print('----------------------')

# print('-------metadata-------')
# print('제안자 :', result[0].metadata['proposer'])
# print('제안자 코드 :', result[0].metadata['politician_code'])
# print('법안 코드 :', result[0].metadata['bill_code'])
# print('제안일 :', result[0].metadata['propose_date'])
# print('----------------------')


# async def find_bill_with_metadata(bill_code):
#     return await mongo_repository.bill_col.find_one({"bill_code": bill_code}, {"_id": 0})

# print(json.dumps(asyncio.run(find_bill_with_metadata(result[0].metadata['bill_code'])), ensure_ascii=False, indent=4))

