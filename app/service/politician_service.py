import asyncio, httpx, os, datetime, logging, json, concurrent.futures, app.service.mongodb_service as mongodb_service
from app import chain, agent
from typing import Optional, List

logging.basicConfig(level=logging.INFO, filename='log/politician_log.log')

header_param = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}

bill_limit = 5
api_key = os.environ.get('PARLIAMENT_API_KEY')
executor = concurrent.futures.ThreadPoolExecutor()
mongodb_service = mongodb_service.MongodbService('admin', 'politicians_google')


async def save_politician_all():
    async for data in get_politician_data_all():
        mongodb_service.collection.insert_one(data)
        logging.info(f'{datetime.datetime.now()} completed {data}')
    executor.shutdown()


async def get_politician_data_one(name: str) -> dict:
    async with httpx.AsyncClient() as client:
        politician_url = f'https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu?KEY={api_key}&Type=json&pIndex=1&pSize=100&HG_NM={name}'
        result = await fetch_politician_data(client, politician_url)
        logging.info(f'{datetime.datetime.now()} {name} get_politician_data_one complete')
        print(f'{datetime.datetime.now()} {name} get_politician_data_one complete')
        print(result)
        return result


async def get_politician_data_many(names: List[str]):
    tasks = [get_politician_data_one(name) for name in names]
    await asyncio.gather(*tasks)


async def get_politician_data_all():
    async with httpx.AsyncClient() as client:
        politician_url = f'https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu?KEY={api_key}&Type=json&pIndex=1&pSize=300'
        async for politician_data in fetch_politician_data(politician_url, client):
            yield politician_data


async def fetch_politician_data(url: str, client: httpx.AsyncClient):
    loop = asyncio.get_running_loop()
    try:
        politician_get_url = await client.get(url, headers=header_param)
        politicians = politician_get_url.json()['nwvrqwxyaytdsfvhu'][1]['row']
        semaphore = asyncio.Semaphore(1)
        tasks = []
        for politician in politicians:
            task = asyncio.create_task(process_politician(loop, politician, client, semaphore))
            tasks.append(task)
        for task in asyncio.as_completed(tasks):
            yield await task
    except Exception as e:
        print(f"Error occurred while fetching politician data: {e}")
        logging.warning(f"{datetime.datetime.now()} Error occurred while fetching politician data: {e}")


async def process_politician(loop: asyncio.AbstractEventLoop, politician: dict, client: httpx.AsyncClient, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        code = politician['MONA_CD']
        name = politician['HG_NM']
        if await mongodb_service.duplicate_check(code):
            print(f'{name} already exists')
            logging.info(f'{name} already exists')
            return
        party = politician['POLY_NM']
        profile = json.dumps(politician, ensure_ascii=False).encode('utf-8').decode('utf-8')
        bill_names = await get_bills_for_description(politician_name=name, bill_limit=bill_limit, client=client)
        bills_names_join = '\n'.join(bill_names)
        diplomat_opinion = await get_perspective_of_topic(name, party, '외교/안보', loop)
        society_opinion = await get_perspective_of_topic(name, party, '사회', loop)
        economy_opinion = await get_perspective_of_topic(name, party, '경제', loop)
        law_opinion = await get_perspective_of_topic(name, party, '법/제도', loop)
        description = await loop.run_in_executor(executor, get_description, (profile, bills_names_join, diplomat_opinion, society_opinion, economy_opinion, law_opinion))
        politician_dict = {
            'code' : code,
            'name': name,
            'birth_date': politician['BTH_DATE'],
            'gender': politician['SEX_GBN_NM'],
            'party': party,
            'eletion_type': politician['ELECT_GBN_NM'],
            'local': politician['ORIG_NM'],
            'election_count': politician['REELE_GBN_NM'],
            'committee': politician['CMITS'],
            'email': politician['E_MAIL'],
            'homepage': politician['HOMEPAGE'],
            'career': politician['MEM_TITLE'],
            'diplomat_opinion': diplomat_opinion,
            'society_opinion': society_opinion,
            'economy_opinion': economy_opinion,
            'law_opinion': law_opinion,
            'description': description
        }
        await asyncio.sleep(2)
        return politician_dict


# descrition에 들어갈 법안 타이틀 5개를 가져오는 메서드
async def get_bills_for_description(politician_name: str, bill_limit: int, client: httpx.AsyncClient, politician_id: Optional[str] = None) -> List[str]:
    try:
        print(f'{politician_name} get_bills_of_politician 수행 시작')
        bill_url = f'https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?KEY={api_key}&Type=json&pIndex=1&pSize={bill_limit}&AGE=21&PROPOSER={politician_name}'
        bills_request_get = await client.get(bill_url, headers=header_param)
        bills = bills_request_get.json()['nzmimeepazxkubdpn'][1]['row']
        bill_names = []
        for idx, bill in enumerate(bills):
            bill_name = bill['BILL_NAME']
            bill_names.append(f'{idx + 1}. {bill_name}')
        print(f'{politician_name} get_bills_of_politician 수행 종료')
        return bill_names
    except Exception as e:
        print(f"{politician_name} get_bills_of_politician 도중 에러 발생: {e}")


# 4개의 분야별로 정치인의 perspective를 가져오는 메서드
async def get_perspective_of_topic(name: str, party: str, topic: str, loop: asyncio.AbstractEventLoop) -> str:
    print(f'{name} : {topic} 시작')
    perspective = await loop.run_in_executor(executor, get_agent_answer, agent.llama3_agent_executor, name, party, topic) 
    print(f'{name} : {topic} 종료')
    return perspective


# agent로 부터 답변을 구해오는 메서드
def get_agent_answer(agent_executor: agent.AgentExecutor, name: str, party: str, topic: str) -> str:
    if topic == "외교/안보":
        llama3_response = agent_executor.invoke({
            "input": f"{party} {name} 외교성향을 검색하고 마땅한 결과가 없으면 안보관을 검색해주세요. 최대한 다양한 의견이 포함될 수 있도록 검색해주세요. 그리고 검색한 모든 정보를 바탕으로 {party} {name} 의원의 외교노선, 안보의식이 어떤식으로 평가받는지 알려주세요."
        })
    elif topic == "사회":
        llama3_response = agent_executor.invoke({
            "input": f"{party} {name} 사회 정책을 검색해주세요. 최대한 다양한 의견이 포함될 수 있도록 검색해주세요. 그리고 검색한 모든 정보를 바탕으로 {party} {name} 의원의 사회 정책이 어떤식으로 평가받는지 알려주세요."
        })
    elif topic == "경제":
        llama3_response = agent_executor.invoke({
            "input": f"{party} {name} 경제 정책을 검색해주세요. 최대한 다양한 의견이 포함될 수 있도록 검색해주세요. 그리고 검색한 모든 정보를 바탕으로 {party} {name} 의원의 경제 정책이 어떤식으로 평가받는지 알려주세요."
        })
    else:
        llama3_response = agent_executor.invoke({
            "input": f"{party} {name} 법치와 제도를 각각 검색해주세요. 최대한 다양한 의견이 포함될 수 있도록 검색해주세요. 그리고 검색한 모든 정보를 바탕으로 {party} {name} 의원의 법치와 제도에 대한 견해를 알려주세요."
        })
    result = f'{topic} : {llama3_response["output"]}'
    return result


# description 생성 메서드
def get_description(data) -> str:
    description = chain.description_chain.invoke({
        "profile": data[0], 
        "bills": data[1] ,
        "diplomat": data[2],
        "society": data[3],
        "economy": data[4],
        "law": data[5],
        })
    return description


