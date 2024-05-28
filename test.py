# -*- coding: utf-8 -*-

import os, json, logging ,asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from app import llms, chain
from langchain_community.document_loaders import WebBaseLoader, JSONLoader, TextLoader, PyPDFLoader
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_transformers import LongContextReorder
from langchain_core.runnables import RunnablePassthrough
import app.service.mongodb_service as mongodb_service
from app.util import json_utils
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from app.util import json_utils
import nltk, re
from langchain import hub

# from konlpy.tag import Okt



# korean_stopwords = ['의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']


# def tokenize_and_morphs(text, stop_words):
#     okt = Okt()
#     tokens = okt.morphs(text)  # 형태소 분석 및 토큰화
#     tokens = [word for word in tokens if word not in stop_words]  # 불용어 제거
#     return tokens


# loader = JSONLoader(
#     file_path='json/ex2.json',
#     jq_schema='.[]',
#     content_key="content",
#     metadata_func=json_utils.metadata_func,
#     text_content=False)

# docs = loader.load()
# print(f"문서의 수: {len(docs)}")

# embeddings = OpenAIEmbeddings(
#     openai_api_key=os.environ.get('OPENAI_API_KEY')
#     )

# # text_splitter = SemanticChunker(
# #     embeddings=embeddings,
# #     breakpoint_threshold_amount=70
# # )

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500, 
#     chunk_overlap=50,
#     length_function=len,
#     is_separator_regex=False,
#     # separators=[
#     #     # "\n\n",
#     #     # "\n",
#     #     " ",
#     #     ".",
#     #     ",",
#     #     "\u200b",  # Zero-width space
#     #     "\uff0c",  # Fullwidth comma
#     #     "\u3001",  # Ideographic comma
#     #     "\uff0e",  # Fullwidth full stop
#     #     "\u3002",  # Ideographic full stop
#     #     "",
#     # ]
# )

# # splits = text_splitter.split_documents(docs)
# # print(splits)
# # print('split_length =', len(splits)) 

# index_name = "bill-search"
# namespace = 'bill'


# from app.service import pinecone_service

# ps = pinecone_service.PineconeService(
#     host=os.environ.get('PINECONE_HOST'),
#     index_name=index_name,
#     namespace=namespace,
#     embeddings=embeddings
# )



############## Party_answer #################

# from app import agent

# q = '''
# 1. {party} 소속 {politician} 의원이 아래 문제에 대해서 어떻게 생각할지 검색하여 알아보세요. 
# 2. 필요하다면 아래 [기본 정보]를 참고하여 추가적으로 정보를 알아보세요.
# 3. 알아낸 정보를 가지고 아래 [문제]의 선택지 중 {politician} 의원이 선택할만한 가능성이 가장 높아 보이는 것을 하나 선택해주세요. 
# 4. 1번부터 4번까지의 선택지 중에서 반드시 하나를 선택해야합니다.
# 5. 선택지의 번호로 답변해주세요.

# [기본 정보]:
# 강기윤 의원은 1960년 6월 4일 생으로 국민의힘 소속의 간사로 활동 중이며, 보건복지위원회에 속해 있습니다.\n\n-발의법안 : \n1. 영유아보육법 일부개정법률안\n2. 치매관리법 일부개정법률안\n3. 개발제한구역의 지정 및 관리에 관한 특별조치법 일부개정법률안\n4. 국민건강보험법 일부개정법률안\n5. 국가유공자 등 예우 및 지원에 관한 법률 일부개정법률안\n\n-외교/안보 : \n강기윤 의원은 보수 성향이 강한 외교노선을 가지고 있으며, 안보의식은 전통적인 보수성향을 보여줍니다.\n\n-사회 : \n사회 정책에 다양한 의견을 포함시키며, 초고령사회, 방문간호, 산후도우미 등 사회서비스 관리 문제에 관심을 가지고 있습니다.\n\n-경제 : \n경제 정책은 지역개발과 지역경제 활성화를 중시하며, 의료현안협의체를 통해 구체적 대안을 제시하고자 합니다.\n\n-법/제도 : \n법치와 제도에 대한 견해는 노사 법치주의를 중시하며, 국민의힘 당의 쇄신을 위해 노력하고 국민의 권익을 보호하고자 합니다.\n\n-정치인에 대한 한 줄 평가 : \n강기윤 의원은 보수 성향이 강한 정치인으로, 다양한 분야에서 활발한 활동을 펼치고 있습니다.

# [문제]:
# 부자들에게 세금을 더 걷어서 대중을 위해 써야한다.
# 1.매우 그렇다
# 2.약간 그렇다
# 3.약간 아니다
# 4.전혀 아니다
# '''
# x = agent.llama3_agent_executor.invoke({"input": q.format(party='국민의 힘', politician='강기윤')})
# print(x['output'])


from app.agent import gpt_agent_executor

ms = mongodb_service.MongodbService('admin', 'question_v2')

questions = [
    '북한과의 종전선언은 해야한다.',
    '대북 유화정책은 대북 제재정책보다 효과적이다.',
    '양안(대만, 중국) 전쟁은 우리와 무관하다.',
    '한국과 일본과의 군사협력을 강화해야한다.',
    '3불(不) 정책 (사드 추가배치X, 미국의 미사일 방어체계 편입X, 한미일 군사동맹X)은 외교적으로 이득이 된다.',
    '한국에는 구조적인 성차별(유리천장, 기울어진 운동장)이 존재한다.',
    '소형모듈원전은 개발, 도입되어야 한다.',
    '종합부동산세(종부세: 일정 금액 이상의 부동산을 소유한 사람들에게 부과되는 세금)를 완화해야한다.',
    '주4일근무제는 비현실적이다.',
    '50인 미만 사업장에 대해서도 중대재해처벌법(사업주가 안전 확보 의무 조치를 소홀히 하여 중대한 산업재해나 시민재해가 일어나 인명 피해가 발생할 경우 사업주를 처벌하는 법률)이 적용되어야 한다.',
    '전세사기특별법(선구제-후회수)은 추진되어야 한다.',
    '상속,증여세율을 낮춰야 한다.',
    '민생회복지원금(전 국민에게 25만원씩 지원)을 지급하는 것이 국민에게 이득이 된다.',
    '현행 3천억 원의 지역화폐 예산을 더욱 늘려야 한다.',
    '공기업의 민영화는 시장 경쟁력을 증대시키고 효율성을 높일 수 있다.',
    '민주유공자법(4·19 혁명과 5·18 민주화운동처럼 별도의 특별법이 없는 민주화 운동 관련 부상자 본인과 그 가족들도 유공자로 예우받도록 하는 법)은 시행되어야 한다.',
    '농산물 가격안정제(농산물 시장가격이 기준가격 미만으로 하락하는 경우에 생산자에게 그 차액의 전부 또는 일부를 지원하는 제도)는 시행되어야 한다.',
    '가맹사업법(프랜차이즈 가맹점주에게 본사를 상대로한 단체 교섭권 부여)은 시행되어야 한다.',
    '노란봉투법(사용자의 범위 확대, 노동쟁의 범위 확대, 손해배상 청구 제한)은 시행되어야 한다.',
    '한국은 공권력(군,경,검)의 힘이 강하므로 제한 혹은 축소시켜야 한다.',
    '2016년 성주에 사드를 배치한다고 했을 때 많은 논란이 있었다. 북한과 성주시 주민들의 반발은 물론이고 중국에서는 경제보복까지 했다. 그럼에도 불구하고 사드는 배치하는것이 맞는가? (정치성향이 보수적일 수록 강경한 노선을 취함)',
    '농민의 보호와 국산 쌀에 대한 보호를 위해서 국내 쌀 수요 대비 초과 생산량이 3~5%이거나 쌀값이 전년보다 5~8% 하락할 때 정부가 초과 생산량을 모두 사들여야 한다고 생각하는가?(정치성향이 진보적일 수록 정부가 쌀을 구입하고 관리해야 한다는 입장)',
    '데이트 폭력은 남성이 여성을 대상으로 한 일방적 범죄이고 이 문제는 페미니즘이나 혹은 그에 준하는 여성주의 운동을 받아들임으로써 개선될 수 있다는 의견에 대하여 어떻게 생각하는가?(정치성향이 진보적일 수록 친페미니즘 성향)',
    '금투세(주식, 채권, 펀드, 파생상품 등에 투자하여 일정 금액 이상의 소득을 올린 투자자에게 발생한 소득의 20~25% 만큼 부과하는 세금)는 완화 혹은 폐지 되어야 하는가? 시행 해야하는가?(정치성향이 진보적일 수록 금투세 적극 찬성)',
    '역사왜곡금지법(역사적 사실을 왜곡하여 폄훼하거나 피해자 및 유가족을 이유 없이 모욕하는 행위를 처벌하고자 하는 것을 목표로 하는 법률안)은 표현의 자유를 침해하고 민주주의를 위배하는 것인가? 아니면 역사 인식과 피해자들을 보호하기 위해 꼭 필요한 것인가?(정치성향이 진보적일 수록 역사왜곡금지법 적극 찬성)'
]

############### Party_answer #################
# parties = ['개혁신당', '조국혁신당', '자유통일당', '기본소득당', '진보당']
# for party in parties:
#     party_dict = {"name": party}
#     for idx, question in enumerate(questions):
#         q = '''
#         1.{party}의 발언이나 행적이나 당론에 비추어 봤을때 아래 [문제]에 대해서 {party}의 당론이 어떤지 정확한 정보를 찾아서 알려주세요.
#         2.검색결과가 있다면 요약하여 짧고 간단하게만 답변해주세요.
#         3.답변을 하기전에 당신이 하려고 했던 답변이 정확한 답변인지에 대해서 한 번 더 검증하세요.
#         4.실제로 {party}이 했던 발언이 아니면 답변해서는 안 됩니다.
#         5.답변이 없어도 되니 구체적인 정보가 없을때는 반드시 "없음"이라는 단어로만 답변해주세요.

#         [문제]
#         {question}

#         답변:
#         '''    
#         party_answer = gpt_agent_executor.invoke({"input": q.format(party=party, question=question)})['output']
#         party_dict[f'question_{idx+1}'] = party_answer
#         print(party_answer)
#     ms.collection.insert_one(party_dict)
############### Party_answer #################


############## Politician_answer #################
# with open('json/name_party.json', 'r', encoding='utf-8') as file:
#     dicts = json.loads(file.read())
#     for e in dicts:
#         poli_dict = {"code": e["code"], "name": e['name']}
#         if ms.duplicate_check(e['code']):
#             print(e['name'], 'continue')
#             continue
#         for idx, question in enumerate(questions):
#             q = '''
#             1.{party} 소속 {politician} 의원의 성향에 비추어 봤을때 아래 [문제]에 대해서 {politician} 의원이라면 어떻게 답변할지 검색해서 알려주세요.
#             2.검색결과가 있다면 요약하여 간단하게만 답변해주세요.
#             3.답변을 하기전에 당신이 하려고 했던 답변이 정확한 답변인지에 대해서 한 번 더 검증하세요.
#             4.실제로 {politician} 의원이 했던 발언이 아니면 답변해서는 안 됩니다.
#             5.{politician} 의원의 발언기록이 없으면 "없음"이라고만 답변하세요.
#             6.검색결과를 짜집기하여 거짓답변을 만들면 안 됩니다. 확실하지 않으면 "없음"이라고 답변하세요.
#             [문제]
#             {question}
#             '''    
#             answer = gpt_agent_executor.invoke({"input": q.format(party=e['party'], politician=e['name'], question=question)})['output']
#             poli_dict[f'question_{idx+1}'] = answer
#             print(answer)
#         ms.collection.insert_one(poli_dict)
############## Politician_answer #################

