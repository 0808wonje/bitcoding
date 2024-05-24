from typing import Optional
from bs4 import BeautifulSoup
import os, json, chain, httpx, asyncio, concurrent.futures, datetime, logging, app.service.mongodb_service as mongodb_service



logging.basicConfig(level=logging.INFO, filename='log/bill_log.log')

header_param = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}
bill_limit = 10
api_key = os.environ.get('PARLIAMENT_API_KEY')
executor = concurrent.futures.ThreadPoolExecutor()
mongodb_service = mongodb_service.MongodbService('admin', 'bills_v2')


async def save_bill_all():
    async for data in get_bill_data_from_all_politician():
        mongodb_service.collection.insert_one(data)
        logging.info(f'{datetime.datetime.now()} completed {data}')
    executor.shutdown()


async def get_bill_data_from_one_politician(name: str, party: str) -> dict:
    async with httpx.AsyncClient() as client:
        bill_url = f'https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?KEY={api_key}&Type=json&pIndex=1&pSize={bill_limit}&AGE=21&PROPOSER={name}'
        result = await fetch_bill_data(bill_url, name, party, client)
        logging.info(f'{datetime.datetime.now()} {name} get_bill_data_from_one_politician complete')
        print(f'{datetime.datetime.now()} {name} get_bill_data_from_one_politician complete')
        print(result)
        return result


async def get_bill_data_from_all_politician():
    async with httpx.AsyncClient() as client:
        politician_url = f'https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu?KEY={api_key}&Type=json&pIndex=1&pSize=300'
        politicians = (await client.get(politician_url, headers=header_param)).json()['nwvrqwxyaytdsfvhu'][1]['row']
        politicians_name_party_dicts = [{'name': politician['HG_NM'], 'party': politician['POLY_NM']}  for politician in politicians]
        semaphore = asyncio.Semaphore(2)
        for p in politicians_name_party_dicts:
            name = p['name']
            bill_url = f'https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn?KEY={api_key}&Type=json&pIndex=1&pSize={bill_limit}&AGE=21&PROPOSER={name}'
            async for bill_data in fetch_bill_data(bill_url, name, p['party'], semaphore, client):
                yield bill_data



async def fetch_bill_data(url: str, name:str, party: str, semaphore: asyncio.Semaphore, client: httpx.AsyncClient):
    print(f'{name} fetch_bill_data 수행 시작')
    loop = asyncio.get_running_loop()
    try:
        bills = (await client.get(url, headers=header_param)).json()['nzmimeepazxkubdpn'][1]['row']
        tasks = []
        for bill in bills:
            task = asyncio.create_task(process_bill(name, party, bill, loop, semaphore, client))
            tasks.append(task)
        for task in asyncio.as_completed(tasks):
            yield await task
        print(f'{name} fetch_bill_data 수행 종료')
    except Exception as e:
        print(f"{name} fetch_bill_data 도중 에러 발생: {e}")


async def process_bill(name: str, party: str, bill: dict, loop: asyncio.AbstractEventLoop, semaphore: asyncio.Semaphore, client: httpx.AsyncClient) -> dict:
    async with semaphore:
        bill_name = bill['BILL_NAME']
        if await mongodb_service.duplicate_check(bill['BILL_ID']):
            print(f'{bill_name} already exists')
            logging.info(f'{bill_name} already exists')
            return
        detail_link = bill['DETAIL_LINK']
        soup = BeautifulSoup((await client.get(detail_link)).content , 'html.parser')
        content = soup.find('div', attrs={'id': 'summaryContentDiv'})
        if not content:
            return
        else:
            content = content.text.strip()
        bill_dict = {
            'bill_code' : bill['BILL_ID'],
            'politician_code': await search_politician_code(name, party, client),
            'title': bill_name,
            'proposer': name,
            'co-proposer': bill['PUBL_PROPOSER'],
            'propose_date': bill['PROPOSE_DT'],
            'age': bill['AGE'],
            'committee': bill['COMMITTEE'],
            'process_result': bill['PROC_RESULT'],
            'content': content,
            'summary_content': await loop.run_in_executor(executor, chain.bill_summary_chain.invoke, {"bill": content}),
            'children_summary_content': await loop.run_in_executor(executor, chain.bill_children_summary_chain.invoke, {"bill": content}),
            'detail_link': detail_link
        }
        await asyncio.sleep(1)
        return bill_dict


async def search_politician_code(name: str, party: str, client: httpx.AsyncClient) -> str:
    politician_url = f'https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu?KEY={api_key}&Type=json&pIndex=1&pSize=300&HG_NM={name}&POLY_NM={party}'
    politician = (await client.get(politician_url, headers=header_param)).json()['nwvrqwxyaytdsfvhu'][1]['row'][0]
    return politician['MONA_CD']

