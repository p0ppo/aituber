from langchain.chains.llm import LLMChain
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
#from langchain.agents import tool
from pydantic.v1 import BaseModel, Field


class ChatAgentInput(BaseModel):
    message: str = Field(description="一般的な内容の担当者に伝達するユーザーの直近の発話内容です。")


def get_chat_tool(llm, chat_history, character_prompt, memory):
    system_prompt = """あなたはAIのアシスタントです。
    ユーザの質問に答えたり、議論したり、日常会話を楽しんだりします。
    """

    chat_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        chat_history,
        character_prompt,
        HumanMessagePromptTemplate.from_template("{input}"),
    ])

    return LLMChain(
        llm=llm,
        prompt=chat_prompt_template,
        memory=memory,
        verbose=True,
    )