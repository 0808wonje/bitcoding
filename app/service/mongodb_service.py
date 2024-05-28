import pymongo, os, asyncio
import motor.motor_asyncio
from bson.objectid import ObjectId


class MongodbService():
    def __init__(self, db_name, collection_name):
        self.url = os.environ.get('MONGODB_URL')
        self.client = pymongo.MongoClient(self.url)
        self.aclient = motor.motor_asyncio.AsyncIOMotorClient(self.url)
        self.db = self.client[db_name]
        self.adb = self.aclient[db_name]
        self.collection = self.db[collection_name]
        self.acollection = self.adb[collection_name]

    def duplicate_check(self, code) -> bool:
        if self.collection.find_one({'code': code}):
            return True
        return False
    
    async def aduplicate_check(self, code) -> bool:
        if await self.acollection.find_one({'code': code}):
            return True
        return False
    
    def find_by_id(self, _id) -> dict:
        return self.collection.find_one({'_id': ObjectId(_id)}, {'_id': 0})
    
    async def afind_by_id(self, _id) -> dict:
        return await self.acollection.find_one({'_id': ObjectId(_id)}, {'_id': 0})
    
    async def aget_top_ten_json(self, lst):
        tasks = []
        for e in lst[:11]:
            tasks.append(asyncio.create_task(self.afind_by_id(e.metadata['_id']))) 
        result = await asyncio.gather(*tasks)
        return result




# 뉴스 데이터 -> txt 파일
# def create_news_data_to_txt():
#     # 삽입할 데이터 (최신 뉴스)
#     mydata = news_crawling.get_naver_news()
#     # mongodb에 데이터 삽입
#     for e in mydata:
#         news_collection.insert_one(e)
#     print('mongodb에 데이터 삽입')
#     with open('data.txt', 'w', encoding='utf-8') as news_data:
#         for e in mydata:
#             news_data.write(e['title'])
#             news_data.write('\n')
#             news_data.write(e['contents'])
#             news_data.write(e['pubDate'])
#             news_data.write('\n')
#         print('data.txt 생성 완료')

