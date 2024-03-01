from langchain.chains import RetrievalQA
from langchain.agents import Tool, load_tools
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSearchAPIWrapper


def get_vectordbqa(
        llm: ChatOpenAI,
        name: str,
        db: Chroma,
        chain_type: str="map_reduce"
        ) -> Tool:
    #qa = VectorDBQAWithSourcesChain.from_chain_type(
    #    llm,
    #    chain_type=chain_type,
    #    vectorstore=db,
    #)
    qa = RetrievalQA.from_chain_type(
        llm,
        chain_type=chain_type,
        retriever=db.as_retriever(),
    )
    return Tool(
        name=name,
        func=qa,
        description=f"Useful for when you need to answer questions about {name}."
    )

def get_googlesearch(llm):
    search = GoogleSearchAPIWrapper()
    tool = load_tools(["google-search"], llm=llm)[0]
    return tool
    #return Tool(
    #    name="search",
    #    func=search.run,
    #    description="Useful for when you need to answer questions about current events"
    #)