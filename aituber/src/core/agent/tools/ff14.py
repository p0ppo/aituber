from typing import Annotated, List, Tuple, Union

from langchain.agents import Tool, load_tools
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field


#class FF14_tools():
#    def __init__(self, llm):
#        self._llm = llm
#    
#    def set_wiki_qa(self, database, chain_type):
#        self._wiki_qa = RetrievalQA.from_chain_type(
#            self._llm,
#            retriever=database.as_retriever(),
#            chain_type=chain_type,
#        )
#
#    @tool
#    def wiki(self, query: str):
#        """Useful for when you need to answer questions about general information about final fantasy 14 (ff14)."""
#        if self._wiki_qa is None:
#            raise Exception("QA chain for ff14 wiki does not exist. Run '.set_wiki()' first.")
#        return self._wiki_qa.run



#@tool
#def ff14_wiki(
#    query: str, 
#    llm: ChatOpenAI, 
#    database: Chroma, 
#    chain_type: str="map_reduce"
#    ) -> str:
#    """Useful for when you need to answer questions about general information about final fantasy 14 (ff14)."""
#    qa = RetrievalQA.from_chain_type(
#        llm,
#        retriever=database.as_retriever(),
#        chain_type=chain_type,
#    )
#    return qa.run(query)

class FF14AgentInput(BaseModel):
    message: str = Field(
        description='''
        Final Fantasy 14の専門家に伝達するユーザーの直近の発話内容です。
        以下に記載されたキャラクター設定を厳密に守りながら会話してください。
        '''
    )


def get_ff14_wiki(
    llm: ChatOpenAI, 
    database: Chroma, 
    chain_type: str="map_reduce"
    ) -> str:
    qa = RetrievalQA.from_chain_type(
        llm,
        chain_type=chain_type,
        retriever=database.as_retriever(),
        #return_source_documents=True,
    )
    return Tool(
        name="ff14_wiki",
        func=qa,
        description=f"Useful for when you need to answer questions about final fantasy 14 (ff14)."
    )