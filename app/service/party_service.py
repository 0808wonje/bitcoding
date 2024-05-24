import mongodb_service
from app.agent import gpt_agent_executor

ms = mongodb_service.MongodbService('admin', 'party')

parties = ['더불어민주당', '국민의힘', '정의당', '새로운미래', '개혁신당', '조국혁신당', '자유통일당', '기본소득당', '진보당']



q = '''
더불어민주당이라면 아래 [문제]에 대해서 어떻게 답변할지 검색해서 알려주세요.

[문제]
인도주의적 차원에서 북한에 대한 경제적 지원을 해야 한다고 생각하십니까? 단, 한국이 지원해 준 돈을 북한 정권이 어떻게 쓰는지에 대해서는 한국이 관여할 수 없습니다.
'''
z = gpt_agent_executor({"input": q})
print(z)