# ################################ 선거코드 ################################
# async def create_election_data():
#     query_param = {
#         'ServiceKey': '9p3dei4%2BnmwbLfOiX3cKgkpP6Jg7NHQWDB7THkcZHnf0%2F0RWxhIqAnpf7A%2BYQR8uC9rg1%2F1iEXYjxlrlf2U8Ow%3D%3D',
#         'numOfRows': 100,
#         'resultType': 'json'}
#     async with httpx.AsyncClient() as client:
#         with open('json/election_data.json', "a", encoding="utf-8") as json_file:
#             json_file.write('[')
#             json_file.write('\n')
#             tasks = []
#             for page in range(1, 3):
#                 election_url = f'http://apis.data.go.kr/9760000/CommonCodeService/getCommonSgCodeList?pageNo={page}'
#                 task = asyncio.create_task(parsing_election_json(client, election_url, query_param, json_file, page))
#                 tasks.append(task)
#             await asyncio.gather(*tasks)
#             json_file.write('\n')
#             json_file.write(']')
    

# async def parsing_election_json(client, url, query_param, json_file, page):
#     election_contents = await client.get(url=url, params=query_param)
#     items = election_contents.json()['response']['body']['items']['item']
#     for i, item in enumerate(items):
#         json.dump(item, json_file, ensure_ascii=False, indent=4)
#         if page == 2 and i == len(items) - 1:  # 마지막 아이템인 경우
#             continue  # 쉼표를 추가하지 않음
#         json_file.write(',')
#         json_file.write('\n')

