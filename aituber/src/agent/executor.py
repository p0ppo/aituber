
#from langchain.chains import LLMChain
#from langchain.agents import (
#    initialize_agent,
#    AgentType,
#    AgentExecutor,
#    ZeroShotAgent,
#    create_openai_functions_agent,
#)

#from ...rag import get_vectordbqa, get_googlesearch

import dotenv
import os
import warnings

import langchain
from langchain.chains.llm import LLMChain
from langchain.memory import ReadOnlySharedMemory, ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate,
)
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.agents import AgentType, initialize_agent, Tool, AgentExecutor
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from .text_segmenter import Segmenter
from .tools import *
from .utils import DestinationOutputParser
from .templates import *
from .dispatcher import DispatcherAgent


class Executor:
    def __init__(self, segment=True, verbose=True):
        self._set_env(verbose)
        self._set_agent()
        self.segment = segment
        if segment:
            self._segmenter = Segmenter(max_characters=140)
    
    def _set_env(self, verbose):
        dotenv.load_dotenv()
        self._verbose = verbose
        langchain.debug = verbose

    def _set_agent(self):
        # LLM chain settings
        self._llm = ChatOpenAI(
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            model_name="gpt-3.5-turbo",
            streaming=True, 
        )

        # Retrieval Augmented Generation (RAG) settings
        self._set_embeddings()
        self._set_database()
        
        # Integrate altoghther
        #self._set_prompt()
        self._set_memory()

        self._set_nodes()
        self._set_dispatcher()
        self._agent = AgentExecutor.from_agent_and_tools(
            agent=self._dispatcher_agent,
            tools=self._tools,
            memory=self._memory,
            verbose=self._verbose
        )

    def _set_embeddings(self):
        # TODO: Better if this list is managed by config file
        embedding_list = [
            "ada_002",
            "multilingual_e5"
        ]

        model_name = os.environ.get("VECTOR_STORE_EMBEDDING")
        if model_name not in embedding_list:
            raise ValueError(f"Model name {model_name} is not supported.")
        if model_name == "ada_002":
            self._embeddings = OpenAIEmbeddings()
        elif model_name == "multilingual_e5":
            self._embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

    def _set_database(self):
        database_list = os.environ.get("DATABASE_LIST").split(",")
        vec_list = [
            os.path.join(os.environ.get("VECTOR_STORE_PATH"), d) \
            for d in database_list
        ]
        rag_path_dict = dict()
        for d, v in zip(database_list, vec_list):
            if os.path.exists(v):
                rag_path_dict[d] = v
            else:
                warnings.warn(f"Vector store of {d} does not exist. Skip.")
                
        self._database = dict()
        for d, v in rag_path_dict.items():
            db = Chroma(
                embedding_function=self._embeddings,
                persist_directory=v
                )
            self._database[d] = db
            #self._database.append(get_vectordbqa(self._llm, d, db))
        #self._database.append(get_googlesearch(self._llm))

    def _set_memory(self):
        self._memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
            )
        self._read_only_memory = ReadOnlySharedMemory(memory=self._memory)
        self._chat_history = MessagesPlaceholder(variable_name="chat_history")
        self._character_prompt = SystemMessagePromptTemplate.from_template(CHARACTER_PROMPT)
    
    def _set_nodes(self):
        agent_kwargs = {
            "system_message" : SystemMessagePromptTemplate.from_template(FF14_TEMPLATE),
            "extra_prompt_messages": [
                self._chat_history,
                self._character_prompt
                ]
        }
        self._ff14_tools = [
            get_ff14_wiki(
                llm=self._llm,
                database=self._database["ff14"],
            ),
        ]
        self._ff14_agent = initialize_agent(
            self._ff14_tools,
            self._llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=self._verbose,
            agent_kwargs=agent_kwargs,
            memory=self._read_only_memory,
        )

        agent_kwargs = {
            "system_message" : SystemMessagePromptTemplate.from_template(SEARCH_TEMPLATE),
            "extra_prompt_messages": [
                self._chat_history,
                self._character_prompt
                ]
        }
        self._search_tools = [
            tavily_search,
        ]
        self._search_agent = initialize_agent(
            self._search_tools,
            self._llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=self._verbose,
            agent_kwargs=agent_kwargs,
            memory=self._read_only_memory,
        )

        self._chat_agent = get_chat_tool(
            llm=self._llm,
            chat_history=self._chat_history,
            character_prompt=self._character_prompt,
            memory=self._read_only_memory,
        )

        self._tools = [
            Tool.from_function(
                func=self._ff14_agent.run,
                name="ff14_agent",
                description="Final Fantasy 14の専門家です。Final Fantasy 14に関係する会話の対応はこの担当者に任せるべきです。",
                args_schema=FF14AgentInput,
                return_direct=True,
            ),
            Tool.from_function(
                func=self._search_agent.run,
                name="search_agent",
                description="ネットでの最新情報検索の担当者です。最新の情報や調査が必要な会話の対応はこの担当者に任せるべきです。",
                args_schema=SearchAgentInput,
                return_direct=True,
            ),
            Tool.from_function(
                func=self._chat_agent.run,
                name="DEFAULT",
                description="一般的な会話の担当者です。一般的で特定の専門家に任せるべきではない会話や抽象的な質問に対して詳細化を促す場合の対応はこの担当者に任せるべきです。",
                args_schema=ChatAgentInput,
                return_direct=True,
            ),
        ]
    
    def _set_dispatcher(self):
        self._dispatcher_agent = DispatcherAgent(
            llm=self._llm,
            memory=self._read_only_memory,
            tools=self._tools,
            verbose=self._verbose,
        )
    
    def get_agent(self):
        return self._agent

    def get_messages(self, message):
        print(self._memory.load_memory_variables({}))
        #resp = self._chain.predict(input=message)
        resp = self._agent.run(message)
        #resp = self._agent_chain.invoke(
        #    {
        #        "input": message
        #    }
        #)["output"]
        print(resp)
        if self.segment:
            seg = self._segmenter.segmentation(resp)
            return resp, seg
        return resp


if __name__ == "__main__":
    from tts import voicepeak

    adapter = OpenAIChatBot(segment=True)
    #test_message = adapter.create_chat("こんにちは！")
    test_message, segmented_message = adapter.create_chat("君のことを教えて？")
    print(test_message)
    print(segmented_message)
    for s in segmented_message:
        print(len(s))

    narrator = "Miyamai Moca"
    emotion = {
        "doyaru" : 0,
        "honwaka" : 100,
        "angry" : 0,
        "teary" : 0,
    }
    for s in segmented_message:
        voicepeak(s, narrator, **emotion)