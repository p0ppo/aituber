import dotenv

from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic.v1 import BaseModel, Field


class SearchAgentInput(BaseModel):
    message: str = Field(
        description='''
            ウェブでの最新情報検索の担当者に伝達するユーザーの直近の発話内容です。
            以下に記載されたキャラクター設定を厳密に守りながら会話してください。
            '''
        )


dotenv.load_dotenv()
tavily_search = TavilySearchResults(max_results=5)