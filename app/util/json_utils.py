import json
from app.service import mongodb_service
from bson.json_util import dumps, loads



async def write_politician_json_one(name: str) -> None:  
    with open(f'json/{name}.json', 'w', encoding='utf-8') as file:
        col = mongodb_service.MongodbService('admin', 'politicians_google').collection
        json.dump(await col.find_one({"name": name}, {"_id": 0}), file, ensure_ascii=False, indent=4)


async def write_politician_json_all() -> None:
    with open('json/politicians.json', "w", encoding="utf-8") as file:
        col = mongodb_service.MongodbService('admin', 'politicians_google').collection
        json.dump(await col.find({}, {"_id": 0}).sort('name').to_list(length=None), file, ensure_ascii=False, indent=4)
        
async def write_politician_json_all_with_name_party() -> None:
    with open('json/name_party.json', "w", encoding="utf-8") as file:
        col = mongodb_service.MongodbService('admin', 'politicians_google').collection
        json.dump(await col.find({}, {"_id": 0, 'code': 1, 'name': 1, 'party': 1}).sort('name').to_list(length=None), file, ensure_ascii=False, indent=4)

async def write_bill_json_all() -> None:
    with open('json/bill.json', "w", encoding="utf-8") as file:
        col = mongodb_service.MongodbService('admin', 'bills_v2').collection
        x = dumps(await col.find().sort('name').to_list(length=None), ensure_ascii=False, indent=4)
        file.write(x)
        

def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["_id"] = record.get("_id")['$oid']
    metadata["proposer"] = record.get("proposer")
    metadata["politician_code"] = record.get("politician_code")
    metadata["bill_code"] = record.get("bill_code")
    metadata["propose_date"] = record.get("propose_date")
    return metadata
