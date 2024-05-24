from fastapi import APIRouter
from app.service import mongodb_service
from app.service import rag
from pydantic import BaseModel


router = APIRouter()

ms = mongodb_service.MongodbService('admin', 'bills_v2')

class BillSearchRequest(BaseModel):
    q: str

search = rag.hybrid_search
chain = rag.hybrid_chain

@router.post("/search/", tags=["search"], summary='search for bills')
async def qna(request: BillSearchRequest):
    q = request.q
    retriever_results = search.invoke(q)
    top_ten = await ms.aget_top_ten_json(retriever_results)
    hybrid_chain = chain.invoke(q)
    return {
        "hybrid_chain": hybrid_chain, 
        "results": top_ten
        } 


