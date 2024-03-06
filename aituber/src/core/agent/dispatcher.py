from typing import Any, List, Tuple, Set, Union
from langchain.agents import BaseSingleActionAgent, Tool
from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel
from langchain.memory import ReadOnlySharedMemory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate,
)
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from pydantic.v1 import Extra

from .tools import *
from .utils import DestinationOutputParser
from .templates import *


class DispatcherAgent(BaseSingleActionAgent):

    llm: BaseChatModel
    memory: ReadOnlySharedMemory
    tools: List[Tool]
    verbose: bool = False

    class Config:
        extra = Extra.allow

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self._llm = llm
        #self._memory = memory
        #self._tools = tools
        #self._verbose = verbose

        self._set_router()

    def _set_router(self):
        destinations = "\n".join([
            f"{tool.name}: {tool.description}" for tool in self.tools
        ])

        router_template = ROUTER_TEMPLATE.format(destinations=destinations)
        router_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(router_template),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            SystemMessagePromptTemplate.from_template(ROUTER_PROMPT_SUFFIX),
        ])
        self._router_chain = LLMChain(
            llm=self.llm,
            prompt=router_prompt_template,
            memory=self.memory,
            verbose=self.verbose
        )
        self._route_parser = DestinationOutputParser(
            destinations=set([tool.name for tool in self.tools])
        )
    
    @property
    def input_keys(self):
        return ["input"]
    
    def plan(
            self,
            intermediate_steps: List[Tuple[AgentAction, str]],
            **kwargs: Any
            ) -> Union[AgentAction, AgentFinish]   :
        
        router_output = self._router_chain.run(kwargs["input"])
        try:
            destination = self._route_parser.parse(router_output)
        except OutputParserException as ope:
            destination = "DEFAULT"
        
        return AgentAction(tool=destination, tool_input=kwargs["input"], log="")
    
    async def aplan(
            self,
            intermediate_steps: List[Tuple[AgentAction, str]],
            **kwargs: Any
            ) -> Union[AgentAction, AgentFinish]:

        router_output = await self._router_chain.arun(kwargs["input"])
        try:
            destination = self._route_parser.parse(router_output)
        except OutputParserException as ope:
            destination = "DEFAULT"

        return AgentAction(tool=destination, tool_input=kwargs["input"], log="")