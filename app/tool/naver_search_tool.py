from typing import Any, Dict, List, Optional
import aiohttp
import requests
from pydantic.class_validators import root_validator
from pydantic.main import BaseModel
from typing_extensions import Literal
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.utils import get_from_dict_or_env
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
import os

class NaverSearchAPIWrapper(BaseModel):
    display: int = 15
    start: int = 10
    sort: str = "sim"    
    type: Literal["news","blog","kin","doc"] = "news"


    X_Naver_Client_Id: str = os.environ.get("X-Naver-Client-Id") 
    X_Naver_Client_Secret: str = os.environ.get("X-Naver-Client-Secret")

    aiosession: Optional[aiohttp.ClientSession] = None

    class Config:
        arbitrary_types_allowed = True
    
    
    
    def results(self, query:str, **kwargs: Any) -> Dict:
        return self._naver_search_api_results(
            search_term = query,
            display= self.display,
            start = self.start,
            sort = self.sort,
            search_type=self.type,
            **kwargs,
        )
    
    def run(self, query: str, **kwargs: Any) -> str:
        results = self._naver_search_api_results(
            search_term = query,
            display= self.display,
            start = self.start,
            sort = self.sort,
            search_type=self.type,
            **kwargs,
        )
        return self._parse_results(results)
    
    async def aresults(self, query: str, **kwargs: Any) -> Dict:
        results = await self._async_naver_search_api_results(
            search_term = query,
            display= self.display,
            start = self.start,
            sort = self.sort,
            search_type=self.type,
            **kwargs,
        )
        return results
    
    async def arun(self, query: str, **kwargs: Any) -> str:
        results = await self._async_naver_search_api_results(
            search_term = query,
            display= self.display,
            start = self.start,
            sort = self.sort,
            search_type=self.type,
            **kwargs,
        )
        return self._parse_results(results)
    
    def _parse_descriptions(self, results: dict) -> List[str] :
        descriptions = []
        for result in results["items"]:
            if "description" in result:
                descriptions.append(result["description"])            

        if len(descriptions) == 0:
            return ["No good Naver Search Result was found"]
        return descriptions

    def _parse_results(self, results: dict) -> str:
        result = " ".join(self._parse_descriptions(results))
        return result    

    def _naver_search_api_results(
            self, search_term: str, search_type: str = "kin", **kwargs: Any
    ) -> dict:
        headers = {
            "X-Naver-Client-Id" : self.X_Naver_Client_Id,
            "X-Naver-Client-Secret" : self.X_Naver_Client_Secret
        }
        params = {
            "query" : search_term,
            **{key: value for key, value in kwargs.items() if value is not None},
        }
        response = requests.get(
            f"https://openapi.naver.com/v1/search/{search_type}.json", headers=headers, params=params
        )
        response.raise_for_status()
        search_results = response.json()
        return search_results
    
    async def _async_naver_search_api_results(
            self, search_term: str, search_type: str = "kin", **kwargs: Any
    ) -> dict:
        headers = {
            "X-Naver-Client-Id" : self.X_Naver_Client_Id,
            "X-Naver-Client-Secret" : self.X_Naver_Client_Secret
        }
        url = f"https://openapi.naver.com/v1/search/{search_type}.json"
        params = {
            "query" : search_term,
            **{key: value for key, value in kwargs.items() if value is not None},
        }

        if not self.aiosession:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, headers=headers, raise_for_status=False
                ) as response:
                    search_results = await response.json()
        else:
            async with self.aiosession.get(
                url, params=params, headers=headers, raise_for_status=True
            ) as response:
                search_results = await response.json()

        return search_results




search = NaverSearchAPIWrapper()

class NaverSearchTool(BaseTool):
    name = "custom_search"
    description = "Use this tool for informations."

    def _run(
            self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        result = search.run(query)
        return result
    
    async def _arun(
            self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        result = search.arun(query)
        return result

