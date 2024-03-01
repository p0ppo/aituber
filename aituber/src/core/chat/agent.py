import dotenv
import os
import warnings

from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.agents import (
    initialize_agent,
    AgentType,
    AgentExecutor,
    ZeroShotAgent,
    create_openai_functions_agent,
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings

from .text_segmenter import Segmenter
from ...rag import get_vectordbqa, get_googlesearch


class Agent:
    def __init__(self, segment=True):
        dotenv.load_dotenv()
        self._set_agent()
        self.segment = segment
        if segment:
            self._segmenter = Segmenter(max_characters=140)

    def _set_agent(self):
        # LLM chain settings
        self._llm = ChatOpenAI(
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            model_name="gpt-4",
            streaming=True, 
        )
        #self._llm_chain = LLMChain(
        #    llm=self._llm,
        #    prompt=self._prompt,
        #    verbose=True,
        #    memory=self._memory_handler,
        #)

        # Retrieval Augmented Generation (RAG) settings
        self._set_embeddings()
        self._set_database()
        
        #self._agent = initialize_agent(
        #    self._database,
        #    self._llm,
        #    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        #    verbose=True,
        #)

        # Integrate altoghther
        self._set_prompt()
        self._set_memory()

        self._agent = create_openai_functions_agent(
            self._llm,
            self._database,
            self._prompt
            )
        self._agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self._agent,
            tools=self._database,
            verbose=True,
            memory=self._memory_handler,
        )

    def _set_prompt(self):
        character_file = os.environ.get("CHARACTER_PATH")
        with open(character_file, "r", encoding="utf-8") as f:
            self._system_prompt = f.read()
        self._prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self._system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ]
        )

    def _set_memory(self):
        self._memory_handler = ConversationSummaryBufferMemory(
            memory_key="chat_history",
            llm=OpenAI(),
            return_messages=True
            )
    
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
                
        self._database = list()
        for d, v in rag_path_dict.items():
            db = Chroma(
                embedding_function=self._embeddings,
                persist_directory=v
                )
            self._database.append(get_vectordbqa(self._llm, d, db))
        self._database.append(get_googlesearch(self._llm))
    
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

    def get_messages(self, message):
        print(self._memory_handler.load_memory_variables({}))
        #resp = self._chain.predict(input=message)
        #resp = self._agent.run(self._prompt.format(input=message))
        resp = self._agent_chain.invoke(
            {
                "input": message
            }
        )["output"]
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